# Memory-mechanism pilots (Oct 2026)

Three small pilots derived from reading `ai-memory` and `Hy-Memory`, plus an
extension of the AfterDeleteBench replication. Local Qwen2.5-7B via Ollama;
synthetic data; tiny samples. These are **directional checks**, not validation
of either upstream system.

## 1. Retention decay (`decay_sim.py`, no LLM)

Implements `ai-memory`'s formula exactly
(`crates/ai-memory-store/src/decay.rs:196-202`):

```
score = salience*exp(-lambda*age_days)
      + sigma*ln(1+access_count)*exp(-mu*days_since_access)
```

Defaults from the Rust source: λ=0.02 (~35-day half-life), σ=0.6, μ=0.04,
salience=1.0, cold threshold 0.20 (`decay.rs:92-103`). A page is evicted when
its score falls below 0.20. The simulation models a page updated at t=0 and last
accessed at a fixed day; after that it is not touched again.

| Setting | Retention days |
|---|---|
| default λ, never accessed | **81** |
| default λ, 20 accesses, last access at day 0 | **93** |
| default λ, 5 accesses, last access at day 60 | **119** |
| 180-day half-life, never accessed | **418** |
| 180-day half-life, any access pattern tested | **418** |

At a fixed age, an old page with 3 accesses 30 days ago scores **0.3412**
(above threshold) while a 180-day-old unused page scores **0.0273** (evicted);
a new unused page scores 0.8187.

**Reading:** access reinforcement is real but bounded. Because μ=0.04 (a ~17-day
half-life on the access term), 20 accesses at day 0 buy only ~12 extra days at
the eviction margin; a late access at day 60 buys ~47% over pure age (81→119).
With a 180-day half-life, the time term dominates and the access term is
invisible at the threshold. "Access-weighted retention" is not immortality; it
is a weeks-scale extension.

## 2. Conflict resolution (`conflict_pilot.py`, Qwen2.5-7B)

20 synthetic fact pairs: 8 true continuations (same subject, same goal,
retry/extension/verification) and 12 negatives (parallel files, different goals
in the same area, different people, context-only, uncertain, different periods).
Two prompts:

- **conservative** — paraphrased from Hy-Memory's reconciler
  (`hy_memory/coding/fact_reconciler.py:214-237`): supersede only if subject
  matches AND goal is materially the same AND the new trace continues/retries/
  extends/verifies/finishes; otherwise INSERT.
- **permissive** — supersede if the two records share a subject or topic.

| Rule | True supersede | False supersede | Accuracy |
|---|---|---|---|
| conservative | **6/8** | **0/12** | 18/20 |
| permissive | **8/8** | **4/12** | 16/20 |

**Reading:** the conservative rule never merged a parallel task in this sample,
but missed two genuine continuations (a preference update `pytest` →
`pytest+uv`, and `investigating` → `found/fix/verify`). The permissive rule
caught every continuation and merged four parallel tasks (two files in one
module, two OOM causes, two meeting decisions, Q1 vs Q2). The tradeoff is
explicit: false-merge cost vs missed-continuation cost. Hy-Memory's choice of
INSERT as the safe default is supported by this sample, but its recall on
subtle continuations is the weak side.

## 3. Post-deletion recovery under summaries (`afterdelete_hierarchical.py`)

Extension of the AfterDeleteBench replication. 10 profiles; six background
records, three distractors, one target (or a matched neutral record). Two
summary constructions:

- **extractive**: all records joined verbatim into one summary (the earlier
  pilot's construction, now with more records);
- **model-written**: Qwen summarizes the records into three bullets.

| Variant | Condition | Recovered | Target in summary |
|---|---|---|---|
| extractive | forget (source deleted, summary kept) | **10/10** | 10/10 |
| extractive | clean (never exposed) | **0/10** | 0/10 |
| extractive | closure (summary retired) | **0/10** | 0/10 |
| model-written | forget | **0/10** | **0/10** |
| model-written | clean | 0/10 | 0/10 |

**Reading:** with an extractive summary, deleting the source record removes
nothing behaviorally: the secret is still in the summary, and the model
recovers it every time; provenance closure removes it every time. With a
model-written summary, the summarizer omitted the secret in **10/10** cases,
so post-deletion recovery was zero. That is not a privacy control: it is one
prompt's compression behavior, and it could reverse with a different prompt or
model. The lesson is the one AfterDeleteBench states: evaluate deletion at the
memory-system level, and distinguish a summary that *happens* to drop a fact
from a deletion mechanism that *guarantees* it.

## Limits

- One local model (`qwen2.5:7b`), temperature 0; one prompt per condition.
- 10–20 synthetic examples per pilot; no confidence intervals are meaningful.
- No upstream code was installed or executed; the decay formula was
  re-implemented from the Rust source, and the conflict prompt is a paraphrase.
- The model-written summary result depends on the instruction "three concise
  bullets"; a summary asked to preserve all secrets would behave differently.
- Nothing here validates the upstream systems' own benchmark claims.

## Rerun

```bash
python decay_sim.py
ollama pull qwen2.5:7b
python conflict_pilot.py
python afterdelete_hierarchical.py
```

`decay_sim.py` is deterministic and needs only the standard library. The other
two need a local Ollama server and take a few minutes on a 6 GB GPU.
