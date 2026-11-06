# 图片乐谱数字化指南

- 状态：`active`
- 最后验证：`2026-11-01`
- 适用范围：本仓库的印刷五线谱图片 / PDF 到可编辑乐谱与发布 PDF
- 单一事实来源：[目录规范](../score/README.md)、[脚本入口](../scripts/README.md)、[工具资料](../tools/README.md)

## 文件流与编辑主文件

原图 → Audiveris `.omr` → 初步 `.mxl` → MuseScore `.mscz` → 校对后的 `.musicxml` 与 `.pdf`。

MusicXML 保存可交换的音乐结构；MSCZ 保存持续编辑与排版的主工程；OMR 保留识别阶段信息。仅把原图拼成 PDF 无法得到结构化乐谱。MusicXML 跨软件导入可能需要整理排版，见 [MuseScore 官方说明](https://handbook.musescore.org/file-management/working-with-musicxml-files)。

以下示例使用 `chopin-nocturne-op9-no2` / `imslp-peters`，操作时替换为实际名称。

执行前按 [项目环境](ENVIRONMENT.md) 创建根 `.venv/` 并同步根依赖清单；本指南中的 Python 命令均使用该环境。

## 1. 检查环境并初始化

```bash
.venv/bin/python scripts/score.py doctor
.venv/bin/python scripts/score.py init chopin-nocturne-op9-no2 imslp-peters
```

在 `source/imslp-peters/README.md` 填写来源与使用条件，在作品 README 填写曲名和作曲者。初始化支持为已有作品添加另一来源版本，不覆盖已有版本。

## 2. 导入原始图片

将图片复制到 `score/chopin-nocturne-op9-no2/source/imslp-peters/`，按页序命名为 `page-001.png`、`page-002.jpg` 等。PDF 则使用 `score.pdf`，不要混放两种输入。

检查页面方向、清晰度、五线谱边缘和页序。若需要人工裁切或修复，另行保留原件和处理说明，不覆盖来源；当前自动入口处理方向、超大页面的等比例缩小与格式打包，均不改写原图。

## 3. 批量识别

```bash
.venv/bin/python scripts/score.py recognize chopin-nocturne-op9-no2 imslp-peters
```

脚本按页码打包多页 TIFF，再运行 Audiveris，无需图形界面。工程、日志和初步 MXL 留在本版本 `audiveris/`。

运行完成后检查实际生成的 `.omr` 和 `.mxl` 路径；脚本检查两类文件均存在，但无法判断音乐正确性。有多个 MXL 时检查是否为独立乐章，不能任选一个就视为整部作品完成。

需要修正谱表、声部、小节边界等识别问题时，在项目根目录的图形终端运行：

```bash
flatpak run --filesystem="$PWD" org.audiveris.audiveris
```

在 Audiveris 中打开该版本 `.omr`，校正并重新导出。[Split and merge](https://audiveris.github.io/audiveris/_pages/guides/main/book_portions/split_merge/) 也可用于人工组织分册或乐章。

## 4. 导入编辑器并校对

先查看实际输出：

```bash
find score/chopin-nocturne-op9-no2/audiveris/imslp-peters -name '*.mxl'
```

将所需完整乐谱的实际路径传给 import，以下 `INPUT.mxl` 须替换为上一条命令找到的文件路径：

```bash
.venv/bin/python scripts/score.py import chopin-nocturne-op9-no2 imslp-peters INPUT.mxl
.venv/bin/python scripts/score.py edit chopin-nocturne-op9-no2 imslp-peters
```

`import` 可无界面运行，`edit` 需要本机图形桌面。导入后以 `notation/imslp-peters/imslp-peters.mscz` 为编辑主文件。多乐章若需合成同一主文件，在编辑器内人工完成并对照原图确认顺序。

按 `notation/imslp-peters/README.md` 中的清单检查音高、节奏、声部、反复与文字，记录未解决问题。先确认音乐结构，再调整纸张、谱表大小、行距和换页；播放仅辅助校对。

## 5. 导出、检查和提交

保存并关闭编辑器后运行：

```bash
.venv/bin/python scripts/score.py publish chopin-nocturne-op9-no2 imslp-peters
```

输出到 `export/imslp-peters/`，同时生成 PDF 和 MusicXML。打开 PDF 检查符号、字体与分页，更新校订状态和导出记录，再将原图、主工程、记录与成果一起保存到仓库外私有备份。曲目目录不进入公开 Git 跟踪范围。

后续修改主文件会使旧导出过期。重新导出前先私有备份旧成果，再人工移除本版本待更新的 PDF / MusicXML，重新执行 publish，避免脚本静默覆盖人工资料。公开传播的授权独立确认，项目的 `publish` 命令仅负责本地导出。

## 故障边界

- `doctor` 失败：按对应工具 README 修复安装，禁止把缺失工具当成成功。
- Audiveris 报错或没有 MXL：保留日志与 OMR，图形界面定位识别问题；不要反复覆盖现场。
- 初始化失败：检查名称、已有版本及目录权限，不通过更换阶段性名称绕过冲突。
- 导入后缺页或缺声部：回到识别工程检查结构，再决定重导入或在编辑器中修订。
- 无图形会话：可以执行识别、导入和导出；目视修订留到图形会话。
- 识别准确率取决于原图与记谱复杂程度。自动化不会把未核对的结果标记为已校对。

PDF 导出与命令行转换依据：[MuseScore 导出说明](https://handbook.musescore.org/file-management/file-export)、[命令行说明](https://handbook.musescore.org/appendix/command-line-usage)。

## 本机验证范围

2026-10-31 已验证用户级 Audiveris 5.11.0、MuseScore Studio 4.7.5、Pillow 12.0.0 和默认英文 OCR 数据。两页合成五线谱 PNG 完整经过识别、MXL 导入、MSCZ 保存以及 PDF / MusicXML 导出；识别 MXL 的 32 个音符音高顺序与合成原稿一致，最终导出 MusicXML 保留 32 个音符。

目录隔离、覆盖保护、页序、派生缩放与原图不变、导出失败不发布等自动检查均通过。图形窗口与用户真实谱面的准确率尚未验证，中文歌词语言数据尚未配置。
