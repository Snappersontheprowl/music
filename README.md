# Music

本仓库用于整理音乐学习资料，包括乐理学习、曲式分析，以及从图片乐谱到可编辑工程和 PDF 的数字化流程。

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `score/` | 按作品、来源版本保存原谱、识别工程、编辑工程与发布成果 |
| `theory/` | 保存乐理笔记、曲式分析、练习和配套资料 |
| `doc/` | 保存项目级文档规范与操作说明 |
| `tools/` | 保存工具版本、配置和使用说明 |
| `scripts/` | 提供曲目初始化、工具检查、识别、编辑与导出命令 |

协作规则见 [`AGENTS.md`](AGENTS.md)，待办事项见 [`TODO`](TODO)。

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
python3 scripts/score.py doctor
python3 scripts/score.py init chopin-nocturne-op9-no2 imslp-peters
```

第二条命令创建真实曲目目录，请替换为实际作品与来源标识。放入原图并登记来源后继续识别、校对、排版和导出。完整操作见 [乐谱数字化指南](doc/SCORE_WORKFLOW.md)，目录命名见 [乐谱规范](score/README.md)，命令说明见 [脚本入口](scripts/README.md)。

工具说明：[Audiveris](tools/Audiveris/README.md)、[MuseScore Studio](tools/MuseScore/README.md)。批量识别和文件导出可无界面运行，目视校对与排版使用图形编辑器。

## 文件与版本

- 原始谱面只保留来源版本，不在原文件上做不可逆修改。
- 导出文件必须能够追溯到对应曲目、版本和 Audiveris 工程。
- 大文件进入仓库前先评估体积；需要时再启用 Git LFS，不在当前阶段预置。
- 文件名和目录名使用稳定业务语义，不使用 `new`、`final`、`tmp`、`test2`、`v2` 等阶段性名称。

## 文档维护

目录职责、文件格式、命名规则或工作流发生变化时，应在同一次修改中更新相关 README。README 的编写建议见 [`doc/README_GUIDE.md`](doc/README_GUIDE.md)。
