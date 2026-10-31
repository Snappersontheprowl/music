# MuseScore Studio

负责导入 Audiveris 生成的 MusicXML / MXL、编辑音乐内容、校对与排版，并从 MSCZ 主文件导出 PDF 和 MusicXML。

## 安装与入口

本项目使用用户级 Flatpak，应用 ID 为 `org.musescore.MuseScore`：

```bash
flatpak install --user flathub org.musescore.MuseScore
flatpak info --user org.musescore.MuseScore
python3 scripts/score.py doctor
```

在图形桌面打开本项目的编辑主文件：

```bash
python3 scripts/score.py edit WORK EDITION
```

该命令从用户级 Flatpak 启动 MuseScore，并为本次运行增加项目目录访问权限。

## 本机安装记录

最后验证日期：2026-10-31。已安装 MuseScore Studio 4.7.5，运行时为 `org.kde.Platform/x86_64/6.9`；无显示环境下 `--version` 已正常退出。实际图形窗口仍需在桌面会话中验证。

无界面转换实测通过：16 音符合成 MusicXML → MSCZ → PDF / MusicXML，导出后音符数量保持 16；两页合成 PNG 经 Audiveris 得到 MXL，再导入 MSCZ 并导出 PDF / MusicXML，最终保留 32 个音符。验证在临时目录进行，样例和输出已清理，未作为正式曲目入库。

安装时 Flathub 将该包依赖的 KDE 6.9 和部分 GL 24.08 运行时标记为已停止维护；这是当前 Flatpak 包的依赖状态。更新工具时应同时复查其运行时状态。

## 文件与操作

本目录保存工具资料；具体曲目的 MSCZ 主文件属于 `score/<work-slug>/notation/<edition-slug>/`。本目录说明文件使用 `README.md`；后续工具配置使用能描述用途的稳定名称。

统一工作流和目录命名见 [操作指南](../../doc/SCORE_WORKFLOW.md) 与 [乐谱规范](../../score/README.md)。

`import` 将指定 MXL / MusicXML 转为 MSCZ；导入后用 MuseScore 编辑主文件，保存后再执行 `publish`。PDF 和 MusicXML 都从这个主文件导出，避免两者独立维护。

批处理使用 `-o` 选择输出格式，并同时设置 `QT_QPA_PLATFORM=offscreen`、`MU_QT_QPA_PLATFORM=offscreen`，用于无图形显示环境。图形编辑不设置这些变量。编辑器中也可以通过“文件 → 导出”生成 PDF。

## 参考

- [MusicXML 导入与整理](https://handbook.musescore.org/file-management/working-with-musicxml-files)
- [文件导出](https://handbook.musescore.org/file-management/file-export)
- [命令行转换](https://handbook.musescore.org/appendix/command-line-usage)
