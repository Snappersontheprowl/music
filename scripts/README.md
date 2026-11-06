# 乐谱工作流命令

`score.py` 按脚本所在位置定位项目根目录，不依赖启动时所在目录。所有 Python 入口共用根 `.venv/`，解释器版本与依赖统一在根目录维护，完整安装步骤见 [项目环境](../doc/ENVIRONMENT.md)。

```bash
uv pip sync --python .venv/bin/python requirements.txt
.venv/bin/python scripts/score.py --help
```

## 文件职责

- `score.py`：初始化目录、验证工具、运行识别、导入 MSCZ、打开编辑器、导出成果。
- `test_score.py`：目录隔离、页序与覆盖保护的自动检查。
- `check_public_history.py`：检查待公开引用的完整 Git 历史，阻止曲谱与私有备份进入推送。
- `test_public_history.py`：用真实提交、删除历史、标签和本地推送验证公开边界。
- `test_tablature.py`：用原创合成音符验证六线谱合并、时间位置与覆盖保护。
- `public_examples.json`：经明确登记的教学片段精确路径与 SHA-256 清单，由历史检查逐提交验证；不放行整个曲目目录。

## 命令

以下命令从项目根目录运行；`WORK`、`EDITION` 替换为实际标识。

| 命令 | 行为 |
| --- | --- |
| `.venv/bin/python scripts/score.py doctor` | 检查两个 Flatpak 应用实际启动、Pillow 和默认英文 OCR 数据；失败返回非零 |
| `.venv/bin/python scripts/score.py init WORK EDITION` | 创建一个来源版本的四个工作目录、来源模板和校订模板 |
| `.venv/bin/python scripts/score.py recognize WORK EDITION` | 检查页码，打包多页 TIFF 或读取单个 PDF，运行批处理识谱 |
| `.venv/bin/python scripts/score.py import WORK EDITION INPUT` | 将本版本识别目录内的指定 MXL / MusicXML 转换为编辑主文件 |
| `.venv/bin/python scripts/score.py edit WORK EDITION` | 在图形会话中打开 MSCZ，命令等待编辑器退出 |
| `.venv/bin/python scripts/score.py publish WORK EDITION` | 从 MSCZ 导出 PDF 和未压缩 MusicXML；不自动判断音乐正确性 |

`INPUT` 相对路径按当前工作目录解释。完整示例见 [操作指南](../doc/SCORE_WORKFLOW.md)。目录和文件命名规则集中维护在 [score/README.md](../score/README.md)。

## 执行约定

固定使用 Flatpak ID，不回退到其他安装方式。每次调用增加项目路径访问权限，不写持久 override；应用原有权限不会因此缩小。

图片打包应用 EXIF 方向，将超过 Audiveris 5.11 默认上限（2000 万像素）的页面等比例缩小到上限以内，透明区域合成白色，派生结果使用无损 RGB TIFF 编码。原图保持不变；不做裁切、纠偏或自动增强。大批高分辨率图片会占用内存，应按实际分册组织。

识别工作目录必须为空，导入和发布目标不得已存在。重新运行前先在仓库外进行私有备份，再人工确认应移除的派生文件；脚本没有覆盖开关。识别失败保留工作目录，供诊断与手工校正。

MSCZ 转换和发布先在目标目录内的临时目录生成，转换全部成功才复制到正式位置；异常时清理临时目录。正式文件逐个写入，进程被强制中断时仍须检查残留。PDF 与 MusicXML 同源导出后仍须目视复核，与主文件和校订记录一起保存到私有备份。曲目工作目录由 Git 忽略。

## 推送前检查

每个克隆执行一次 `git config --local core.hooksPath .githooks`，启用版本化的 `.githooks/pre-push`。钩子使用项目 `.venv`；环境缺失时阻止推送并说明原因。

```bash
.venv/bin/python scripts/check_public_history.py
.venv/bin/python scripts/check_public_history.py main
```

检查覆盖拟推送分支和标签的全部可达提交。即使最新提交删除了曲谱，旧提交仍含未经登记曲谱也会被拒绝；删除远程引用不发送本地历史。教学示例以提交自身的精确文件与哈希清单作为限定例外，完整规则见 [公开仓库维护](../doc/PUBLIC_REPOSITORY.md)。

运行检查：

```bash
.venv/bin/python -m unittest discover -s scripts -p 'test_*.py'
```
