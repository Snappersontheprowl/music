# 公开仓库与本地资料维护

- 状态：`active`
- 最后验证：`2026-11-06`
- 适用范围：本仓库的提交、推送、本地曲谱与私有备份
- 单一事实来源：[忽略规则](../.gitignore)、[历史检查](../scripts/check_public_history.py)、[曲谱规范](../score/README.md)

## 公开范围

公开仓库保存通用脚本、环境定义、工具配置和说明。`score/` 下仅 `README.md` 可跟踪；曲目原图、裁剪、音符转录、JSON、文本预览、工程、导出、专用脚本和参数均留在本地。格式变化不改变项目的不公开规则。

程序检查使用自行构造的音符或合成图片，运行产物在临时目录生成并清理。以后要公开授权样例，需先确认具体授权、调整允许范围并更新检查与文档；当前没有例外目录。

## 日常操作与检查

曲目初始化、识别、编辑和导出照常使用 `score/`。修订通过仓库外私有备份追溯，连同工具版本、处理参数、文件清单和 SHA-256 保存。

每个新克隆创建根 `.venv` 后，启用本地钩子：

```bash
git config --local core.hooksPath .githooks
.venv/bin/python scripts/check_public_history.py
```

钩子配置不随 Git 提交自动生效。普通终端推送和使用本机 Git 钩子的编辑器推送会执行检查；环境缺失或检查失败时中止。不得跳过钩子或强制添加曲谱来绕过公开边界。

检查拟推送分支和标签的全部可达提交树，拒绝以下内容：

- `score/README.md` 之外的 `score/` 路径，包括曲目 README 和专用脚本。
- 任意路径中的图片、PDF、MusicXML、Guitar Pro、MuseScore、Audiveris、MIDI 等谱面/工程格式，以及 Git bundle 和常见备份归档。
- 任意路径中名为 `events.json`、`reference.json`、`parsed.json`、`conversion.json`、`preview.txt` 的常见转录结果。

检查依据路径和格式规则，无法判断任意改名文本是否含有乐谱；公开提交仍须人工查看差异。最新树已删除但祖先提交仍有曲谱时也会拒绝。指向非提交对象的引用无法正常审核时拒绝；删除远程引用不发送本地历史。

## 历史整理与恢复

本次以原远程干净提交重建本地公开提交，保留环境和通用工具更新，排除曲谱与具体转录报告。曲目原路径、专用脚本和成果保留，旧历史保存为仓库外 `repository.bundle`，不创建旧历史分支。本次不推送、不修改 GitHub 可见性。

查阅原历史时，把 bundle 克隆到另一个私有目录：

```bash
git clone /path/to/private-backup/repository.bundle /path/to/private-restore
```

该克隆的来源是本地 bundle，仅作私有查阅，不能重新连接公开远程后推送。备份中的 `score-sha256.json` 可核对独立曲谱副本，恢复不依赖公开仓库。

本次整理约束后续推送范围，不证明此前上传内容已从 GitHub 缓存、旧链接或他人副本彻底消失。是否调整仓库可见性或处理既有公开副本，需另外决定。
