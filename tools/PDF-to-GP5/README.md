# PDF-to-GP5

本地吉他六线谱识别、裁行评估、合并和草稿导出。五线谱仍使用 `scripts/score.py recognize` 的 Audiveris 入口。

## 环境与文件职责

- 上游：[F100Pilot/PDF-to-GP5](https://github.com/F100Pilot/PDF-to-GP5)，固定版本 0.9.0、提交 `4754a207ff4a08be8dfb4b5097c4a4c3775004d4`，未修改上游识别器。
- 共用根 `.venv/`，依赖由根清单和 [项目环境](../../doc/ENVIRONMENT.md) 维护；MuseScore 使用用户级 Flatpak。
- `evaluate.py`：调用上游 API，保留 GP5、工具报告、事件、预览和环境清单；失败记录异常并返回非零。
- `export.py`：读取本地裁行计划，识别、合并、设置 TAB 谱表，导出 GP5、MusicXML、MSCZ 和 PDF。

公开代码不包含具体曲谱；原图、坐标、元数据、人工修订和结果均放在本地 `score/`，规则见 [曲谱目录](../../score/README.md)。

## 单个图片或 PDF 的评估

```bash
.venv/bin/python tools/PDF-to-GP5/evaluate.py INPUT OUTPUT
```

`INPUT` 为图片或 PDF，`OUTPUT` 为曲目目录内尚不存在的结果目录。`--tempo 80 --meter 4/4` 表示人工提供元数据，须与自动检测区分。结果不提交到公开历史。

## 裁行计划与导出

人工确认页序、调弦、Capo、速度、拍号和每行小节数，将计划保存在本地曲目的 `recognition/<edition>/pdf-to-gp5/plan.json`。以下是接口示意，坐标和小节数需根据自己的谱面填写：

```json
{
  "name": "guitar-study",
  "title": "自行创作的吉他练习",
  "tempo": 80,
  "meter": "4/4",
  "tuning": [64, 59, 55, 50, 45, 40],
  "capo": 0,
  "systems": [
    {
      "source": "score/guitar-study/source/author/page-001.png",
      "box": [40, 100, 1200, 260],
      "measures": 4
    }
  ]
}
```

`name` 是小写字母、数字和连字符组成的文件基名；`title` 为显示标题。`tuning` 明确指定第 1–6 弦的空弦 MIDI 音高。`systems` 按阅读顺序排列，`box` 是原图像素左、上、右、下坐标，应包含六根弦与节奏符号；`source` 相对项目根目录解释。计划、原图和输出必须都在本地 `score/` 内。

```bash
.venv/bin/python tools/PDF-to-GP5/export.py \
  score/guitar-study/recognition/author/pdf-to-gp5/plan.json \
  score/guitar-study/recognition/author/pdf-to-gp5/system-crops
```

输出目录须不存在。逐行保留裁剪、原始识别和日志，小节数不符时停止；全部通过才合并导出。异常保留现场与 `failure.json`，不覆盖已有工程。

## 草稿边界

按印刷顺序合并，省略反复/结尾和音符/拍效果，保留基本音符、闷音及识别时值。延音按前面的同弦音符统一品位，找不到前音时中止。仅含跨行延音的小节可能被识别为休止，需对照原图确认。

Capo 保留为文字，播放不叠加变调夹移调，以免本机 MuseScore 导入后改写品位。检查 TAB 谱表、小节数及逐小节弦号/品位多重集合；这不能代替识别准确率评估。漏音、分组、节奏和演奏技法需人工校订，方法见 [六线谱处理说明](../../doc/TABLATURE_EVALUATION.md)。

原有曲目专用脚本、参数和修订证据继续留在本地目录，不随本次通用代码提取而改写。

从图片输入、原始报告到导出与误差分析的完整演示，见 [四小节技术示例](../../examples/tablature-recognition/bushiyinweijimocaixiangni-opening/README.md)。该片段按精确文件登记，整谱继续保存在本地。
