# Audiveris

## 功能

保存 Audiveris 的版本记录、配置和操作说明，用于将来源谱识别为可继续校订和导出的 MusicXML 成果。

## 本级模块职责

本目录只承担 Audiveris 工具层面的资料整理。具体曲目的来源谱、Audiveris 工程和导出成果不放在这里，而应按照 [`../../score/README.md`](../../score/README.md) 放入对应曲目目录。

## 命名规则

- 工具说明使用 `README.md`。
- 配置文件使用能够说明用途的稳定名称，不使用阶段性词语。
- 版本信息优先写入 Git 提交或明确命名的版本记录，不通过重复复制整个工具目录表达版本。

## 使用建议

确认 Audiveris 版本与项目工程兼容后再进行识别和导出。工程校订和成果检查流程见 [`../../score/README.md`](../../score/README.md)。

## 本机安装与验证

最后验证日期：2026-10-31。本机采用用户级 Flatpak 安装，应用 ID 为 `org.audiveris.audiveris`，来源为 `flathub`，分支为 `stable`。

| 项目 | 实测结果 |
| --- | --- |
| Flatpak | 1.12.9 |
| Audiveris | 5.11.0 |
| 运行时 | org.freedesktop.Platform/x86_64/25.08，已安装 |
| 应用内 Java | OpenJDK 25.0.4.1，可运行 |
| OCR 引擎 | 程序版本命令报告 Tesseract 5.5.2 |
| 命令行入口 | `-help`、`-version` 均正常退出 |

复查安装与程序入口：

```bash
flatpak info --user org.audiveris.audiveris
flatpak run org.audiveris.audiveris -version
flatpak run org.audiveris.audiveris -help
```

上述检查确认安装和命令行启动可用。验证会话没有图形显示环境，尚未验证 GUI 窗口、实际谱面识别或 MusicXML 导出。

## 项目访问与启动

默认文件权限为 `xdg-documents` 和 `xdg-pictures`。实测默认沙箱无法读取本项目 `/home/eda/my_lab/projects/study/music`，启动时应显式授权此目录：

```bash
flatpak run --filesystem=/home/eda/my_lab/projects/study/music org.audiveris.audiveris
```

已验证该启动参数使沙箱内的项目文件可读、`score/` 目录具有写入权限；未执行持久权限覆盖。请在本机图形终端运行上述命令，并按曲目目录组织工程与导出成果。
