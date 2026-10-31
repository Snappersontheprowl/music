# 乐谱工作流命令

`score.py` 按脚本所在位置定位项目根目录，不依赖启动时所在目录。使用 Python 3.10 及以上、Flatpak 和 Pillow：

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/score.py --help
```

## 文件职责

- `score.py`：初始化目录、验证工具、运行识别、导入 MSCZ、打开编辑器、导出成果。
- `requirements.txt`：固定图片打包所需 Pillow 版本。
- `test_score.py`：目录隔离、页序与覆盖保护的自动检查。

## 命令

以下命令从项目根目录运行；`WORK`、`EDITION` 替换为实际标识。

| 命令 | 行为 |
| --- | --- |
| `python3 scripts/score.py doctor` | 检查两个 Flatpak 应用实际启动和 Pillow；失败返回非零 |
| `python3 scripts/score.py init WORK EDITION` | 创建一个来源版本的四个工作目录、来源模板和校订模板 |
| `python3 scripts/score.py recognize WORK EDITION` | 检查页码，打包多页 TIFF 或读取单个 PDF，运行批处理识谱 |
| `python3 scripts/score.py import WORK EDITION INPUT` | 将本版本识别目录内的指定 MXL / MusicXML 转换为编辑主文件 |
| `python3 scripts/score.py edit WORK EDITION` | 在图形会话中打开 MSCZ，命令等待编辑器退出 |
| `python3 scripts/score.py publish WORK EDITION` | 从 MSCZ 导出 PDF 和未压缩 MusicXML；不自动判断音乐正确性 |

`INPUT` 相对路径按当前工作目录解释。完整示例见 [操作指南](../doc/SCORE_WORKFLOW.md)。目录和文件命名规则集中维护在 [score/README.md](../score/README.md)。

## 执行约定

固定使用 Flatpak ID，不回退到其他安装方式。每次调用增加项目路径访问权限，不写持久 override；应用原有权限不会因此缩小。

图片打包只应用 EXIF 方向、将透明区域合成白色并保存无损 RGB TIFF；不做裁切、纠偏或自动增强，原图保持不变。大批高分辨率图片会占用内存，应按实际分册组织。

识别工作目录必须为空，导入和发布目标不得已存在。重新运行前先保存 Git，再人工确认应移除的派生文件；脚本没有覆盖开关。识别失败保留工作目录，供诊断与手工校正。

MSCZ 转换和发布先在目标目录内的临时目录生成，转换全部成功才复制到正式位置；异常时清理临时目录。正式文件逐个写入，进程被强制中断时仍须检查残留。命令不自动提交 Git、不自动勾选校订清单。PDF 与 MusicXML 同源导出后仍须目视复核并一起提交。

运行检查：

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
```
