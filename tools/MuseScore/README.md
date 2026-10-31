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

## 文件与操作

本目录保存工具资料；具体曲目的 MSCZ 主文件属于 `score/<work-slug>/notation/<edition-slug>/`。本目录说明文件使用 `README.md`；后续工具配置使用能描述用途的稳定名称。

统一工作流和目录命名见 [操作指南](../../doc/SCORE_WORKFLOW.md) 与 [乐谱规范](../../score/README.md)。

`import` 将指定 MXL / MusicXML 转为 MSCZ；导入后用 MuseScore 编辑主文件，保存后再执行 `publish`。PDF 和 MusicXML 都从这个主文件导出，避免两者独立维护。

批处理使用 `-o` 选择输出格式，并同时设置 `QT_QPA_PLATFORM=offscreen`、`MU_QT_QPA_PLATFORM=offscreen`，用于无图形显示环境。图形编辑不设置这些变量。编辑器中也可以通过“文件 → 导出”生成 PDF。

## 参考

- [MusicXML 导入与整理](https://handbook.musescore.org/file-management/working-with-musicxml-files)
- [文件导出](https://handbook.musescore.org/file-management/file-export)
- [命令行转换](https://handbook.musescore.org/appendix/command-line-usage)
