# Same conservative prompt, three operating points

**English TL;DR:** I gave three local models the same "supersede only on task
continuation" prompt and 50 labeled fact pairs. The operating points did not
match: Llama3.1-8B scored 19/20 true supersedes with 0/30 false merges,
Qwen2.5-7B 17/20 with 1/30, Gemma3-4B 8/20 with 0/30. Preference updates were
missed by all three. In a separate deletion test, an extractive summary
recovered a deleted secret 50/50, while a model-written summary retained it only
2/50 and recovered 1/50 — presence in a summary is not recoverability.

**中文一句话版本：** 我拿同一段“只在任务延续时覆盖旧记忆”的保守规则去测三个本地模型，它们的 precision/recall 完全不在一个位置——同一段 prompt 不是同一个操作点。

---

## 问题

做 agent 记忆的人，大多会在 prompt 里写一句类似的话：

> 只有在主体相同、目标实质相同、新轨迹延续/重试/扩展/验证/完成旧轨迹时，才覆盖旧事实；否则插入。

听起来很稳。问题是，这句话不是一条可执行的判据，而是一个交给模型解释的自然语言规则。解释权在模型手里，操作点就不在 prompt 里。

我做了 50 对合成事实，20 对是真延续（同主体、同目标，重试/扩展/验证/修订），30 对是负例（同文件不同目标、同模块不同文件、不同人、不同项目、只共享技术、不同时期、不确定）。每对让模型输出一个 JSON：`SUPERSEDE` 或 `INSERT`。每个模型跑两套提示词：保守版（按 Hy-Memory 的 reconciler 规则改写）和宽松版（同主体或同主题就覆盖）。

## 结果

真延续召回 / 负例误合并：

| 模型 | 保守 | 宽松 |
|---|---|---|
| Qwen2.5-7B | 17/20 · 1/30 | 19/20 · 17/30 |
| Llama3.1-8B | 19/20 · **0/30** | 20/20 · 9/30 |
| Gemma3-4B | **8/20** · 0/30 | 19/20 · 3/30 |

同一段保守提示词，Llama 只漏 1 个真延续，Gemma 漏了 12 个（revision、extension、retry、update、verify 几乎全判成 INSERT）。同一段宽松提示词，Qwen 误合并 17 个负例，Gemma 只误合并 3 个。最佳操作点因此是模型特定的：Llama 保守 49/50，Qwen 保守 46/50，Gemma 宽松 46/50。

这不是“哪个模型更好”，而是说：**“我们用了保守规则”不是一句可复现的实验描述**。报告里至少要写清模型、提示词、以及这个模型在这套数据上的 precision/recall。

## 偏好更新是另一个失败面

三个模型的保守规则都漏了偏好更新：

- “用户偏好 pytest” → “用户现在偏好 pytest + uv”
- “用户偏好上午开会” → “用户偏好下午开会”

在“任务延续”的判据下，这两个更新看起来像“同一主题的新陈述”，但又不构成“继续/重试/扩展/验证/完成”。保守规则倾向于 INSERT，于是旧偏好继续留在记忆里。这不是模型不听话，是判据覆盖错了对象：**偏好更新需要单独的通道**，不能和任务延续共用一条 supersede 规则。

## 删除：摘要里有，不等于能恢复

另一组实验测“删掉源记录后，派生摘要是否还泄漏”。50 个 profile，每个有背景记录、干扰项、一个访问码；源记录删除，摘要保留。

| 摘要类型 | 删除源、保留摘要 | 从未暴露 | provenance closure |
|---|---|---|---|
| 抽取式（逐字拼接） | **50/50 恢复** | 0/50 | 0/50 |
| 模型生成（三行摘要） | **1/50 恢复**（2/50 摘要仍含码） | 0/50 | — |

两个保留案例的差别很有意思：

- Profile 22 的摘要写 “Your access code is SOUTH-IPAV-782.”，查询恢复。
- Profile 29 的摘要写 “their access code is SOUTH-KUWR-679.”，字符串在，但问 “What is my access code?” 返回 `UNKNOWN`。

**摘要里有 ≠ 可恢复。** 人称、所有格、查询措辞都是测量的一部分。10-profile 的 pilot 是 0/10，50 profiles 是 1/50——小样本里的“零”不是零。模型摘要把秘密省掉，不是删除保证，只是一次压缩行为；换个提示词或模型，结论可能反过来。

## 衰减也不是“用了就永久保留”

顺手复算了 ai-memory 的保留公式（默认 λ=0.02、σ=0.6、μ=0.04、阈值 0.20）：

| 设置 | 保留天数 |
|---|---|
| 从未访问 | 81 |
| 20 次访问，最后在 day 0 | 93 |
| 5 次访问，最后在 day 60 | 119（纯年龄的 1.47×） |
| 180 天半衰期，任何访问模式 | 418 |

访问加权是“周级延长”，不是永久保留。原因是访问项自身有一个约 17 天的半衰期（μ=0.04）；半衰期一长，时间项完全压过访问项。

## 我会因此改的三件事

1. **报告操作点，不只报告规则名。** 写“conservative prompt”没用；写“Llama3.1-8B + 这段 prompt，在 50 对上是 19/20 召回、0/30 误合并”。
2. **偏好更新单独走一条路。** 不要和任务延续共用 supersede 判据。
3. **删除在记忆系统层评估。** 别把“摘要恰好没写秘密”当成删除成功；测字符串是否在、是否可恢复、以及查询措辞变化时是否仍可恢复。

## 数据与代码

- 50 对冲突样本：[`conflict_pairs_50.json`](../../replications/2026-10-memory-pilots/data/conflict_pairs_50.json)（CC BY 4.0）
- 50 个删除 profile：[`deletion_profiles_50.json`](../../replications/2026-10-memory-pilots/data/deletion_profiles_50.json)（CC BY 4.0）
- 脚本与原始记录：[`replications/2026-10-memory-pilots/`](../../replications/2026-10-memory-pilots/)
- 系统对照（ai-memory / Hy-Memory / Harness² / context-mode）：[`docs/related-systems-2026-10.md`](../related-systems-2026-10.md)

```bash
python conflict_pilot_50.py --out results/conflict_pilot_50.json
python afterdelete_hierarchical.py --profiles 50 --out results/afterdelete_hierarchical_50.json
```

## 限制

合成数据、50 对/50 profiles、三个模型（删除只用 Qwen2.5-7B）、单提示词；没有安装或执行上游代码；不是 Hy-Memory 或 ai-memory 的 benchmark；上游的数字没有复现。这些是方向性结果，不是生产环境的比率。

如果你在做 agent memory，欢迎拿你的模型跑同一套 50 对，把操作点贴出来——比“我们用了保守规则”有用得多。
