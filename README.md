# 海龟汤 · Turtle Soup Skill

一个可直接用于 AI Agent（WorkBuddy / Claude 等）的**海龟汤（水平思考谜题）主持人技能包**：内置 **143 道带完整汤底**的谜题，支持「出题 → 是/不是/与此无关提问 → 逐级提示 → 揭底」的完整游戏流程。

> 海龟汤是一种「情境推理」游戏：主持人只给出一个看似离奇的**汤面**，玩家通过只能回答「是 / 不是 / 与此无关」的问题，推理出背后的**汤底**（真相）。

---

## 特性

- **143 道题，题题有汤底**：每题都带 `solution`（完整真相），不是只有谜面。
- **判定依据结构化**：每题 `key_facts` 给出「回答是/不是」所依据的关键事实，避免主持人临场编造。
- **递进式提示**：每题 `hints` 从模糊到明确，卡住时可逐步放出。
- **难度分级**：简单 / 中等 / 烧脑（启发式标注，供出题参考）。
- **零依赖**：数据为纯 JSON，脚本仅用 Python 标准库，随处可跑。
- **可扩展**：附带 `ingest/` 解析脚本，按约定格式即可导入自己的题库。

## 快速开始

### 作为 Agent 技能使用

把本仓库放到你的技能目录（例如 WorkBuddy）：

```bash
git clone https://github.com/solcat1007/haitao-puzzle.git \
  ~/.workbuddy/skills/haitao-puzzle
```

之后对 Agent 说「来一题海龟汤 / 玩海龟汤 / 出个题」，Agent 会读取 `SKILL.md` 的规则并开始游戏：只念 `surface`（汤面），按 `key_facts` 回答「是 / 不是 / 与此无关」，需要时给 `hints`，最后揭晓 `solution`。

### 直接查看题库

```bash
python -c "import json;d=json.load(open('puzzles/puzzles.json'));print('题目数:',len(d['puzzles']))"
```

随机抽一题：

```bash
python - <<'PY'
import json, random
d = json.load(open('puzzles/puzzles.json', encoding='utf-8'))
p = random.choice(d['puzzles'])
print('【汤面】', p['surface'])
print('（难度：%s）' % p['difficulty'])
print('【汤底】', p['solution'])
PY
```

## 游戏流程

1. **出题**：主持人只展示 `surface`（汤面），绝不提前剧透。
2. **提问**：玩家用能被「是 / 不是 / 与此无关」回答的问题提问。
3. **判定**：主持人依据该题 `key_facts`，只回「是」「不是」「与此无关」之一。
4. **提示**：玩家卡住时，按 `hints` 顺序给递进提示。
5. **揭底**：玩家说出接近真相的推理，或主动放弃时，公布 `solution`。

详细的主持规则见 [`SKILL.md`](./SKILL.md)。

## 数据格式

`puzzles/puzzles.json`：

```json
{
  "meta": {
    "source": "素材来源说明",
    "total": 143,
    "notes": "难度为启发式标注……"
  },
  "puzzles": [
    {
      "id": 1,
      "title": "题名（取汤面前 14 字）",
      "difficulty": "简单 | 中等 | 烧脑",
      "surface": "汤面（呈现给玩家，不剧透）",
      "solution": "汤底（完整真相，即解法）",
      "key_facts": ["判定「是/不是」的关键事实，若干条"],
      "hints": ["递进式提示，从模糊到明确"],
      "source_file": "原始素材来源"
    }
  ]
}
```

字段说明：

| 字段 | 含义 |
|---|---|
| `surface` | 汤面，玩家看到的谜面 |
| `solution` | 汤底，完整真相（每道题必有） |
| `key_facts` | 回答「是/不是」的依据，防止主持人乱判 |
| `hints` | 递进提示 |
| `difficulty` | 难度档位（启发式） |

## 添加自己的题库

把你的题库整理成纯文本（每题两段：第一段汤面、第二段汤底，题与题之间用 59 个 `=` 分隔），然后：

```bash
python ingest/build_puzzles.py your_puzzles.txt
```

脚本会解析题面/汤底、切分 `key_facts` 与 `hints`、标注难度，并写回 `puzzles/puzzles.json`。

## 目录结构

```
haitao-puzzle/
├── README.md              # 本文件
├── SKILL.md               # Agent 技能定义（frontmatter + 主持规则）
├── LICENSE                # MIT（代码与文档）
├── DATA_NOTICE.md         # 题库来源与使用声明
├── puzzles/
│   └── puzzles.json       # 143 道题（题面 + 汤底 + 判定事实 + 提示）
└── ingest/
    └── build_puzzles.py   # 题库解析脚本（纯标准库）
```

## 许可

- 代码与文档：**MIT**（见 [LICENSE](./LICENSE)）
- 题库内容：见 [DATA_NOTICE.md](./DATA_NOTICE.md)

## 免责声明

海龟汤属民间广泛流传的推理游戏体裁。本仓库题库仅供**个人学习与娱乐**使用；若你是相关素材的权利人并希望移除，请提 issue，我们会及时处理。
