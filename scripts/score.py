#!/usr/bin/env python3
"""Project-local score digitization commands. Run with --help for usage."""

import argparse
from datetime import datetime
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
AUDIVERIS = "org.audiveris.audiveris"
MUSESCORE = "org.musescore.MuseScore"
MAX_IMAGE_PIXELS = 20_000_000  # Audiveris 5.11 default LOAD limit.


def slug(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("标识须使用小写 ASCII 字母、数字和连字符")
    return value


def inside(path, parent):
    path = path.resolve()
    if not path.is_relative_to(parent.resolve()):
        raise ValueError(f"路径越出允许目录：{path}")
    return path


def locations(args):
    work = inside(ROOT / "score" / args.work, ROOT / "score")
    return {name: inside(work / name / args.edition, work)
            for name in ("source", "audiveris", "notation", "export")}


def run(app, *options, headless=False, timeout=None):
    command = ["flatpak", "run", "--user", f"--filesystem={ROOT}"]
    if headless:
        command += ["--env=QT_QPA_PLATFORM=offscreen", "--env=MU_QT_QPA_PLATFORM=offscreen"]
    command += [app, *map(str, options)]
    subprocess.run(command, check=True, timeout=timeout)


def require_edition(paths):
    for path in paths.values():
        if not path.is_dir():
            raise ValueError(f"版本目录未初始化：{path}")


def initialize(args):
    paths = locations(args)
    work = ROOT / "score" / args.work
    # Preflight the entire edition before creating anything.
    if any(p.exists() for p in paths.values()):
        raise ValueError("该版本已有目录，拒绝覆盖；请检查现有资料")
    for path in paths.values():
        path.mkdir(parents=True)
    readme = work / "README.md"
    if not readme.exists():
        readme.write_text(f"# {args.work}\n\n作品名称：待填写\n\n作曲者：待填写\n\n"
                          "## 目录职责\n\n"
                          "- `source/`：按来源版本保存原始资料。\n"
                          "- `audiveris/`：按版本保存识别输入、工程与未校对导出。\n"
                          "- `notation/`：按版本保存 MuseScore 编辑主文件和校订记录。\n"
                          "- `export/`：按版本保存经过校对的发布文件。\n\n"
                          "## 版本索引\n\n每个版本的来源与进度见 "
                          "`source/<edition-slug>/README.md`；目录与命名规则见 "
                          "[乐谱规范](../README.md)。\n", encoding="utf-8")
    (paths["source"] / "README.md").write_text(
        f"# {args.edition} 来源记录\n\n登记日期：{datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()}\n\n"
        "- 出版社 / 编配者：待填写\n- 来源链接或取得方式：待填写\n"
        "- 来源版本 / 出版年份：待填写\n- 版权或使用条件：待填写\n"
        "- 页数与页序：待填写\n- 图像类型（印刷五线谱 / 其他）：待填写\n\n"
        "原图按 `page-001.png`、`page-002.jpg` 顺序保存；PDF 使用 `score.pdf`。"
        "一个版本只选择一种输入组织方式，不混放 PDF 与逐页图片。\n",
        encoding="utf-8")
    (paths["notation"] / "README.md").write_text(
        f"# {args.edition} 校订记录\n\n"
        f"编辑主文件：`{args.edition}.mscz`（导入后生成）。\n\n"
        "## 工具与进度\n\n- Audiveris 版本：待填写\n"
        "- MuseScore Studio 版本：待填写\n- 状态：待识别\n"
        "- 待解决问题：待填写\n\n## 核对清单\n\n"
        "- [ ] 页序、乐器、谱表和声部完整\n"
        "- [ ] 谱号、调号、拍号和小节数量\n"
        "- [ ] 音高、时值、休止符和临时升降号\n"
        "- [ ] 连线、连音、反复和跳转\n"
        "- [ ] 歌词、表情、速度和力度\n"
        "- [ ] 对照原图检查，辅助播放试听\n"
        "- [ ] PDF 字体、符号重叠、页边距与翻页位置\n\n"
        "## 发布记录\n\n记录发布日期、对应 Git 提交、导出文件和剩余问题。"
        "主文件修改后，旧 export 成果须重新校对并导出。\n",
        encoding="utf-8")
    print(f"已初始化：{work}，版本 {args.edition}")


def doctor(_args):
    failed = False
    for app, flag in ((AUDIVERIS, "-version"), (MUSESCORE, "--version")):
        try:
            run(app, flag, headless=True, timeout=45)
        except (OSError, subprocess.SubprocessError) as error:
            print(f"工具检查失败：{app}：{error}", file=sys.stderr)
            failed = True
    try:
        from PIL import Image
        print(f"Pillow：{Image.__version__}")
    except ImportError:
        print("缺少 Pillow：python3 -m pip install -r scripts/requirements.txt", file=sys.stderr)
        failed = True
    english = Path.home() / ".var/app" / AUDIVERIS / "config/tessdata/eng.traineddata"
    if english.is_file() and english.stat().st_size:
        print(f"Audiveris 英文 OCR 数据：{english}")
    else:
        print("缺少默认英文 OCR 数据，请按 tools/Audiveris/README.md 安装", file=sys.stderr)
        failed = True
    if failed:
        raise ValueError("工具链检查未通过")


def recognize(args):
    paths = locations(args)
    require_edition(paths)
    target = paths["audiveris"]
    if any(target.iterdir()):
        raise ValueError("识别工作目录非空，拒绝覆盖；请先检查并整理已有工程")
    files = [p for p in paths["source"].iterdir() if p.name != "README.md"]
    pdf = paths["source"] / "score.pdf"
    if files == [pdf]:
        source = inside(pdf, paths["source"])
        if not source.is_file():
            raise ValueError("score.pdf 须为普通文件")
    else:
        if not files or any(not re.fullmatch(r"page-\d{3}\.(png|jpg|jpeg)", p.name)
                            or not p.is_file() for p in files):
            raise ValueError("来源须为单个 score.pdf，或 page-001.png 等连续编号图片")
        files.sort(key=lambda p: p.name)
        if [int(p.stem[5:]) for p in files] != list(range(1, len(files) + 1)):
            raise ValueError("图片页码须从 001 连续编号，且不得重复")
        from PIL import Image, ImageOps
        images = []
        try:
            for file in files:
                inside(file, paths["source"])
                with Image.open(file) as image:
                    oriented = ImageOps.exif_transpose(image)
                    if oriented.width * oriented.height > MAX_IMAGE_PIXELS:
                        factor = math.sqrt(MAX_IMAGE_PIXELS / (oriented.width * oriented.height))
                        original_size = oriented.size
                        oriented.thumbnail((max(1, int(oriented.width * factor)),
                                            max(1, int(oriented.height * factor))),
                                           Image.Resampling.LANCZOS)
                        print(f"派生输入缩小：{file.name} {original_size} → {oriented.size}")
                    rgba = oriented.convert("RGBA")
                    rgb = Image.new("RGB", rgba.size, "white")
                    rgb.paste(rgba, mask=rgba.getchannel("A"))
                    images.append(rgb)
            source = target / "input.tiff"
            images[0].save(source, save_all=True, append_images=images[1:],
                           compression="tiff_deflate")
        finally:
            for image in images:
                image.close()
    inside(source, ROOT)
    run(AUDIVERIS, "-batch", "-transcribe", "-save", "-export",
        "-output", target, "--", source)
    if not list(target.rglob("*.omr")) or not list(target.rglob("*.mxl")):
        raise ValueError("未同时生成 OMR 和 MXL；请检查 Audiveris 输出，保留现场排查")
    print(f"识别输出：{target}（待校对；多乐章可能产生多个 MXL）")


def convert(source, destination):
    if destination.exists():
        raise ValueError(f"目标已存在，拒绝覆盖：{destination}")
    run(MUSESCORE, "-o", destination, source, headless=True, timeout=180)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ValueError(f"工具未生成有效文件：{destination}")


def import_score(args):
    paths = locations(args)
    require_edition(paths)
    source = inside(Path(args.input), paths["audiveris"])
    if not source.is_file() or source.suffix.lower() not in (".mxl", ".musicxml"):
        raise ValueError("输入须为本版本 audiveris 目录内的 MXL 或 MusicXML 文件")
    destination = paths["notation"] / f"{args.edition}.mscz"
    if destination.exists():
        raise ValueError(f"编辑主文件已存在，拒绝覆盖：{destination}")
    with tempfile.TemporaryDirectory(prefix=".convert-", dir=paths["notation"]) as directory:
        staged = Path(directory) / destination.name
        convert(source, staged)
        if not zipfile.is_zipfile(staged):
            raise ValueError("转换结果不是 MSCZ 压缩工程")
        # Exclusive creation also protects against a concurrent import.
        with destination.open("xb") as output, staged.open("rb") as data:
            shutil.copyfileobj(data, output)
    print(f"编辑主文件：{destination}（请校对后发布）")


def edit(args):
    paths = locations(args)
    require_edition(paths)
    source = inside(paths["notation"] / f"{args.edition}.mscz", paths["notation"])
    if not source.is_file():
        raise ValueError("编辑主文件不存在，请先执行 import")
    run(MUSESCORE, source)


def publish(args):
    paths = locations(args)
    require_edition(paths)
    source = inside(paths["notation"] / f"{args.edition}.mscz", paths["notation"])
    if not source.is_file():
        raise ValueError("编辑主文件不存在，请先执行 import")
    destinations = [paths["export"] / f"{args.edition}{ext}"
                    for ext in (".pdf", ".musicxml")]
    if any(p.exists() for p in destinations):
        raise ValueError("发布目标已存在；请先确认 Git 已保存旧成果，再移除待更新目标")
    with tempfile.TemporaryDirectory(prefix=".publish-", dir=paths["export"]) as directory:
        for destination in destinations:
            convert(source, Path(directory) / destination.name)
        if not (Path(directory) / destinations[0].name).read_bytes().startswith(b"%PDF-"):
            raise ValueError("导出结果不是 PDF")
        for destination in destinations:
            with destination.open("xb") as output:
                output.write((Path(directory) / destination.name).read_bytes())
    print("已导出 PDF 和 MusicXML；请目视检查 PDF 并更新 notation 中的校订与发布记录")


def main():
    parser = argparse.ArgumentParser(description="图片乐谱 → 可编辑工程 → PDF")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, function, help_text in (
            ("doctor", doctor, "检查工具链"),
            ("init", initialize, "初始化作品的一个来源版本"),
            ("recognize", recognize, "按页序识别图片或 PDF"),
            ("import", import_score, "将识别 MXL 导入 MSCZ 主文件"),
            ("edit", edit, "打开 MuseScore 图形编辑器"),
            ("publish", publish, "从编辑主文件导出 PDF 与 MusicXML")):
        command = commands.add_parser(name, help=help_text)
        command.set_defaults(function=function)
        if name != "doctor":
            command.add_argument("work", type=slug)
            command.add_argument("edition", type=slug)
        if name == "import":
            command.add_argument("input", help="识别得到的 MXL / MusicXML 路径")
    args = parser.parse_args()
    try:
        args.function(args)
    except (ValueError, OSError, ImportError, subprocess.SubprocessError) as error:
        parser.exit(1, f"错误：{error}\n")


if __name__ == "__main__":
    main()
