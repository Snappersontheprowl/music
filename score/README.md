# 乐谱资料

按作品和来源版本，保存原始乐谱、识别工程、编辑主文件与发布成果。自动识别对象为印刷五线谱；简谱、手写谱和其他记谱法须先评估样张。

## 目录模型

```text
score/<work-slug>/
├── README.md
├── source/<edition-slug>/
│   ├── README.md
│   ├── page-001.png
│   └── page-002.jpg
├── audiveris/<edition-slug>/
│   ├── input.tiff
│   └── ...
├── notation/<edition-slug>/
│   ├── README.md
│   └── <edition-slug>.mscz
└── export/<edition-slug>/
    ├── <edition-slug>.musicxml
    └── <edition-slug>.pdf
```

这是运行流程后的示意结构；初始化只创建目录和记录模板。

| 目录 / 文件 | 职责 |
| --- | --- |
| 曲目 `README.md` | 作品信息、目录职责与版本入口 |
| `source/` | 原始来源，各版本 README 记录来源、页序与使用条件 |
| `audiveris/` | 派生的识别输入、`.omr` 工程、日志与未校对 `.mxl` |
| `notation/` | `.mscz` 编辑主文件、工具版本、校订清单与发布记录 |
| `export/` | 经过校对、从同一编辑主文件导出的 MusicXML 与 PDF |

## 命名规则

- `<work-slug>` 使用小写 ASCII 字母、数字和连字符，优先包含作曲家与作品标识，例如 `chopin-nocturne-op9-no2`。
- `<edition-slug>` 使用相同字符规则，描述出版社、来源或编配，例如 `imslp-peters`；不同来源、编配分开建版本。
- 图片使用 `page-001.png`、`page-002.jpg` 等三位连续页码，从 001 开始，允许 PNG、JPG、JPEG 混合，扩展名小写。同一页码不得出现两个文件。
- PDF 来源使用 `score.pdf`；单一版本选择 PDF 或逐页图片，二者不混放。页数超过 999 时先明确分册。
- 编辑工程与发布成果统一使用 `<edition-slug>` 基名；识别工作文件保留 Audiveris 实际生成的名称。
- 修订使用 Git 历史管理，全局命名原则见 [AGENTS.md](../AGENTS.md)。

## 主文件与追溯

原始文件保持不变。`.omr` 用于回到识别阶段校正，`.mscz` 是导入后日常编辑的主文件，MusicXML 是交换格式，PDF 是阅读与打印成果。

导入后优先在 MuseScore 中继续修改；若回到 Audiveris 重新导出，重新导入会替换编辑起点，必须先在 Git 中保存并明确处理已有排版修改。脚本拒绝覆盖现有工程和发布文件，不自动合并两个阶段的改动。

主文件变化后应更新校订记录并重新发布，旧 PDF 不代表当前编辑内容。发布文件与主文件在同一次 Git 提交中保存。来源不明或未完成校对时，不应把输出登记为已发布。

## 操作入口

使用根目录的 `python3 scripts/score.py` 初始化和执行工作流，完整命令、人工校对和故障处理见 [乐谱数字化指南](../doc/SCORE_WORKFLOW.md)。

多页图片由脚本按页码无损打包为多页 TIFF，交给 Audiveris 作为一本乐谱处理；逐个图片参数输入不能视为自动合并。同一作品含多个乐章时，识别结果仍可能有多个 MXL，应在导入前检查作品与乐章边界。

## 大型文件

导入前检查原图、派生 TIFF 和 OMR 工程的总体体积。识别输入可以由原图重建，但应在确认工程可重开后再决定是否删除；不要无意重复保存多个副本。根据实际增长决定是否启用 Git LFS。
