# Music

本仓库用于整理音乐学习资料，包括乐理学习、曲式分析，以及从图片乐谱到可编辑工程和 PDF 的数字化流程。

公开仓库保存工具、环境和通用文档。`score/` 下的曲目资料在本地维护，Git 仅跟踪其目录指南 `score/README.md`。原谱、转录数据、工程、PDF 和曲目专用参数均需单独进行私有备份。

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `score/` | 本地曲目工作区，按作品、来源版本保存原谱、工程与导出；仅目录指南公开 |
| `theory/` | 保存乐理笔记、曲式分析、练习和配套资料 |
| `doc/` | 保存项目级文档规范与操作说明 |
| `tools/` | 保存工具版本、配置和使用说明 |
| `scripts/` | 提供曲目初始化、工具检查、识别、编辑与导出命令 |

协作规则见 [`AGENTS.md`](AGENTS.md)，待办事项见 [`TODO`](TODO)。

## 运行环境

项目 Python 入口统一使用根目录 `.venv/`。`.python-version` 固定解释器版本，`requirements.txt` 维护全部 Python 依赖；创建环境、安装外部工具和检查步骤见 [项目环境](doc/ENVIRONMENT.md)。

```bash
uv venv --python 3.12.13 .venv
uv pip sync --python .venv/bin/python requirements.txt
git config --local core.hooksPath .githooks
```

首次创建后，日常运行直接使用 `.venv/bin/python`。Audiveris 和 MuseScore 由用户级 Flatpak 管理。

## 乐理学习流程

1. 在 `theory/` 下按主题建立笔记，记录概念、例子、练习和参考资料。
2. 需要结合具体作品时，在笔记中使用相对链接指向 `score/` 中对应的曲目目录。
3. 新增或修正结论时，同步更新笔记中的数据、谱例和参考来源。
4. 笔记达到多个文件的规模后，升级为主题目录，并在其中提供 `README.md` 作为索引。

## 乐谱整理流程

```text
PNG / JPG / PDF → Audiveris（OMR 工程）→ MusicXML / MXL
                                           ↓
                              MuseScore Studio（MSCZ 编辑主文件）
                                           ↓
                                  MusicXML + PDF 发布成果
```

在项目根目录开始：

```bash
.venv/bin/python scripts/score.py doctor
.venv/bin/python scripts/score.py init chopin-nocturne-op9-no2 imslp-peters
```

第二条命令创建真实曲目目录，请替换为实际作品与来源标识。放入原图并登记来源后继续识别、校对、排版和导出。完整操作见 [乐谱数字化指南](doc/SCORE_WORKFLOW.md)，目录命名见 [乐谱规范](score/README.md)，命令说明见 [脚本入口](scripts/README.md)。

工具说明：[Audiveris](tools/Audiveris/README.md)、[MuseScore Studio](tools/MuseScore/README.md)。批量识别和文件导出可无界面运行，目视校对与排版使用图形编辑器。

上述自动识别入口用于五线谱。六线谱的裁行计划、识别与导出入口见 [PDF-to-GP5](tools/PDF-to-GP5/README.md)，评估方法与局限见 [六线谱处理说明](doc/TABLATURE_EVALUATION.md)。

## 文件与版本

- 原始谱面只保留来源版本，不在原文件上做不可逆修改。
- 导出文件必须能够追溯到对应曲目、版本和 Audiveris 工程。
- 曲目文件保留在本地，大小不影响公开边界；使用仓库外私有备份保存原图、工程与导出。
- 文件名和目录名使用稳定业务语义，不使用 `new`、`final`、`tmp`、`test2`、`v2` 等阶段性名称。

## 提交与推送

提交工具代码和通用说明，曲谱资料由 `.gitignore` 排除。每个克隆需执行一次上面的钩子配置；普通 Git 推送会检查每个待推送引用的完整可达历史，拒绝曲目路径、谱面文件和常见转录数据。可以单独运行：

```bash
.venv/bin/python scripts/check_public_history.py
```

检查规则与备份恢复边界见 [公开仓库维护](doc/PUBLIC_REPOSITORY.md)。

## 文档维护

目录职责、文件格式、命名规则或工作流发生变化时，应在同一次修改中更新相关 README。README 的编写建议见 [`doc/README_GUIDE.md`](doc/README_GUIDE.md)。
