# 乐谱资料

本目录保存可追溯的乐谱来源、Audiveris 工程和数字化导出成果。

## 目录模型

每部作品使用一个稳定曲目标识目录：

```text
score/
└── <work-slug>/
    ├── README.md
    ├── source/
    │   └── <edition-slug>.<ext>
    ├── audiveris/
    │   └── <edition-slug>/
    └── export/
        └── <edition-slug>.<ext>
```

- `source/` 保存原始 PDF、图片或 MusicXML，不覆盖原始来源。
- `audiveris/` 保存对应版本的 Audiveris 工程及其必要工作文件。
- `export/` 保存经过校对的 MusicXML、MXL、MIDI 或 PDF 等成果。
- 曲目目录中的 `README.md` 记录作品信息、来源、版权或使用条件、Audiveris 版本和校订状态。

同一作品存在多个编配、出版社或来源时，以不同的 `edition-slug` 区分，不覆盖已有版本。

## 命名规则

- `<work-slug>`：小写 ASCII 单词和连字符，优先包含作曲家和作品标识，例如 `chopin-nocturne-op9-no2`。
- `<edition-slug>`：描述来源或编配，例如 `piano-solo`、`satb`、`imslp-peters`。
- 扩展名必须对应真实文件格式。
- 禁止使用 `new`、`final`、`tmp`、`test2`、`v2` 等阶段性名称决定文件身份。
- 同一版本的不同导出格式尽量使用相同的 `edition-slug` 基名。

## 整理流程

1. 建立 `<work-slug>/README.md`，登记作品、来源和用途。
2. 将原始来源放入 `source/`，文件名使用稳定的 `edition-slug`。
3. 在 `audiveris/<edition-slug>/` 中完成识别和人工校订。
4. 将可复用的成果放入 `export/`，并记录导出格式和完成状态。
5. 校订后检查调号、拍号、临时升降号、连音、休止、反复和分页信息。
6. 确认来源和版权提示完整后再提交。

## 大型文件

导入扫描谱、音频或大型工程前，先检查文件体积和增长趋势。若普通 Git 管理成本过高，应记录实际体积后统一启用 Git LFS，不应把大文件散落或重复保存。
