# 项目运行环境

- 状态：`active`
- 最后验证：`2026-11-01`
- 适用范围：本仓库的 Python 脚本、Flatpak 应用和 OCR 数据
- 单一事实来源：[Python 版本](../.python-version)、[依赖清单](../requirements.txt)、[工具说明](../tools/README.md)

## 环境组成

| 部分 | 管理方式与职责 |
| --- | --- |
| Python | 根 `.python-version` 固定解释器版本；所有项目 Python 入口共用根 `.venv/` |
| Python 包 | 根 `requirements.txt` 是唯一活动依赖清单，由 uv 同步；包含主流程、六线谱评估及其传递依赖 |
| Audiveris、MuseScore | 用户级 Flatpak 应用及其运行时，版本与操作由对应工具 README 维护 |
| OCR 语言数据 | Audiveris 用户配置中的模型文件，来源、位置与校验值见 Audiveris README |
| 项目资料 | 原谱、工程、评估与发布文件按 `score/README.md` 管理，不放进虚拟环境 |

Python 环境覆盖主工作流和 PDF-to-GP5 评估。依赖清单统一采用 Pillow 13.0.0，PDF-to-GP5 固定至已评估源码提交。历史结果中的 `manifest.json` 保留当时的解释器、安装路径和依赖版本，不随环境迁移改写。

## 创建与同步

在项目根目录执行。先准备 Git、uv，以及 `.python-version` 指定的 Python；本机使用已有的 `/usr/bin/python3.12`。

```bash
uv venv --python 3.12.13 .venv
uv pip sync --python .venv/bin/python requirements.txt
```

第一条用于首次创建环境；已有正确环境时只执行同步命令。uv 需要访问包索引及固定提交的 Git 源码，已下载内容可复用本机缓存。

`sync` 会按照清单安装并移除清单外的包。变更依赖时统一修改根清单、同步并验证，再提交；不在其他目录新增活动依赖清单。根清单当前包含完整的版本固定结果，新增或升级直接依赖时也要更新关联的传递依赖。

虚拟环境包含绝对路径，项目换位置或解释器版本变化时，应删除旧 `.venv/` 并按上述步骤重建，不直接搬运环境目录。

## 运行入口

默认明确指定解释器，不依赖终端是否激活 Conda 或其他环境：

```bash
.venv/bin/python scripts/score.py doctor
.venv/bin/python scripts/score.py --help
.venv/bin/python tools/PDF-to-GP5/evaluate.py --help
.venv/bin/python tools/PDF-to-GP5/export.py --help
```

也可以用 `source .venv/bin/activate` 激活后运行 `python`。文档统一使用显式路径，便于确认运行位置；Conda base 不承担本项目依赖安装。

`doctor` 检查当前是否使用根 `.venv/`、解释器是否符合 `.python-version`，再检查主流程工具与默认英文 OCR 数据。PDF-to-GP5 的 OCR 库还需通过实际样张测试确认，不以主流程 doctor 代替。

VSCode 中执行 `Python: Select Interpreter`，选择本项目 `.venv/bin/python`；更换解释器后在新终端中复查。编辑器选择和终端激活是两个设置，文档命令通过显式路径确定解释器。

## 外部应用与模型

Python 依赖同步不会安装 Flatpak 应用或 OCR 模型。首次配置时按以下文档准备：

- [Audiveris](../tools/Audiveris/README.md)：用户级安装、项目目录权限与英文 OCR 数据。
- [MuseScore Studio](../tools/MuseScore/README.md)：用户级安装、无界面导出和图形编辑。
- [PDF-to-GP5](../tools/PDF-to-GP5/README.md)：共享 Python 环境中的评估入口及已知工具限制。

批量识别和文件转换可无界面执行，交互编辑需要图形桌面。外部应用通过启动参数增加项目目录访问权限；不把模型、软件安装目录或 Flatpak 运行时复制进 Git。

## 检查与版本管理

```bash
uv pip check --python .venv/bin/python
.venv/bin/python -m unittest discover -s scripts -p 'test_*.py'
.venv/bin/python scripts/score.py doctor
```

依赖检查确认已安装包的声明一致，单元检查覆盖图片处理与资料保护，doctor 检查实际工具入口。依赖更新后还应按变更范围执行转换样张，记录成功或预期失败；环境检查通过不代表识别质量通过。

提交 `.python-version`、`requirements.txt` 和相关文档；`.venv/` 由 `.gitignore` 排除，视为可重建的本机文件。下载缓存不作为唯一依赖来源。

每个克隆还须执行 `git config --local core.hooksPath .githooks`，使推送通过项目 `.venv` 运行公开历史检查。曲目资料由 Git 忽略，使用仓库外私有备份，详细规则见 [公开仓库维护](PUBLIC_REPOSITORY.md)。

本次迁移验证覆盖当前 Linux 主机；其他平台的原生依赖和图形工具需在对应系统验证。

2026-11-01 本机已完成共享环境验证：23 个包依赖一致，8 项现有测试和 doctor 通过；六线谱裁行输出的事件与原评估完全相同，整页测试复现已知 `KeyError: 26`。旧的独立评估虚拟环境已移除，历史评估文件保持原样。
