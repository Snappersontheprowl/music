# 工具资料

## 功能

保存音乐学习与乐谱整理所需工具的版本、配置、操作说明和必要辅助文件；不保存乐谱来源和 Audiveris 工程本体。

## 本级模块职责

- `Audiveris/`：保存 Audiveris 的版本、配置和操作说明。
- `MuseScore/`：保存 MuseScore Studio 安装、编辑与 PDF 导出说明。
- `PDF-to-GP5/`：保存六线谱候选识别工具的固定环境、评估入口与结论；尚未接入主识别命令。

Audiveris 与 MuseScore 通过 MusicXML 交换乐谱。Python 脚本和评估入口共用根 `.venv/`，安装与依赖定义见 [项目环境](../doc/ENVIRONMENT.md)，统一操作入口见 [scripts/README.md](../scripts/README.md)。

## 命名规则

- 工具目录使用工具的正式名称。
- 操作说明统一使用 `README.md`，具体配置文件使用能够表达用途的稳定名称。
- 不使用 `new`、`final`、`tmp`、`test2`、`v2` 等阶段性词语。

## 使用建议

先阅读对应工具目录的 README，再进行安装或配置。乐谱的 Audiveris 工程文件属于具体曲目，应放入 [`../score/`](../score/README.md) 约定的曲目目录。
