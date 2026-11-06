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

上述检查确认安装和命令行启动可用。验证会话没有图形显示环境，GUI 窗口和用户真实谱面的识别质量仍待验证。

## 项目访问与启动

默认文件权限为 `xdg-documents` 和 `xdg-pictures`。实测默认沙箱无法读取本项目 `/home/eda/my_lab/projects/study/music`，启动时应显式授权此目录：

```bash
flatpak run --filesystem=/home/eda/my_lab/projects/study/music org.audiveris.audiveris
```

已验证该启动参数使沙箱内的项目文件可读、`score/` 目录具有写入权限；未执行持久权限覆盖。请在本机图形终端运行上述命令，并按曲目目录组织工程与导出成果。

## 批处理与后续编辑

Audiveris 支持 `-batch -transcribe -save -export`，无需图形窗口即可完成识别、保存 OMR 工程和导出 MXL。统一入口为：

```bash
.venv/bin/python scripts/score.py recognize WORK EDITION
```

在项目根目录执行，并先用 `init` 初始化来源版本、放入原图。脚本按页码将多张图片打包为多页 TIFF，避免将各页误当成彼此独立的乐谱。识别工程和初步 MXL 留在曲目 `audiveris/`，人工校对后使用 [MuseScore Studio](../MuseScore/README.md) 编辑和排版。

`.omr` 保留识别阶段信息，应与原始图片一起保留。MXL 是跨工具交换文件，PDF 发布由后续排版阶段完成。具体操作见 [乐谱数字化指南](../../doc/SCORE_WORKFLOW.md)。

## OCR 语言数据

应用安装后不预装 OCR 语言数据；Tesseract 的版本命令成功不代表语言模型已安装。缺失时文本识别步骤会被跳过，详见 [官方语言说明](https://audiveris.github.io/audiveris/_pages/guides/main/languages/)。

本机已安装默认英文 `eng`，位置为 `~/.var/app/org.audiveris.audiveris/config/tessdata/eng.traineddata`。使用 [Tesseract tessdata 4.1.0 的英文模型](https://github.com/tesseract-ocr/tessdata/blob/4.1.0/eng.traineddata)，同时包含 legacy / LSTM 数据，文件大小 23,466,654 字节，SHA-256 为 `daa0c97d651c19fba3b25e81317cd697e9908c8208090c94c3905381c23fc047`。

重新安装或增加语言时，优先在图形界面使用 `Tools → Languages`，并在 Book 参数中选择实际需要的语言。Audiveris 需要支持 legacy 引擎的数据，不能用仅含 LSTM 的 `tessdata_fast` / `tessdata_best` 模型代替。当前只配置默认英文，不代表中文歌词识别已配置。

`doctor` 会检查默认位置的英文数据文件；`recognize` 会对超过 2000 万像素的图片仅缩小派生 TIFF 页面，以适应本机 Audiveris 5.11 的默认输入上限，保留原图不变。

## 批处理验证范围

2026-10-31 使用 MuseScore 渲染的两页合成五线谱（每页 16 个四分音符、300 DPI）验证多页 TIFF 识别，成功生成 OMR 与单个 MXL。MXL 中 32 个音符的音高顺序与合成原稿一致，英文 OCR 步骤可运行。

该结果用于确认多页输入和工具链可用，不代表用户扫描件、手机照片、复杂声部或歌词的识别准确率。
