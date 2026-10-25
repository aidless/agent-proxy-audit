# Memory-mechanism pilots (Oct 2026)

Three small pilots derived from reading `ai-memory` and `Hy-Memory`, plus an
extension of the AfterDeleteBench replication. Local models via Ollama;
synthetic data. These are **directional checks**, not validation of either
upstream system.

Two scales are reported where they exist: an initial pilot (20 conflict pairs,
10 deletion profiles, Qwen2.5-7B) and a scaled run (50 pairs × 3 models; 50
deletion profiles). The scaled run is the headline; the initial run is kept
because it shows how much a small sample can move a rate.

Frozen datasets: [`data/conflict_pairs_50.json`](data/conflict_pairs_50.json) and
[`data/deletion_profiles_50.json`](data/deletion_profiles_50.json) (CC BY 4.0).
Public write-up:
[`docs/blog/2026-10-conservative-prompt-operating-points.md`](../../docs/blog/2026-10-conservative-prompt-operating-points.md).


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

## 2. Conflict resolution

Prompt A is paraphrased from Hy-Memory's reconciler
(`hy_memory/coding/fact_reconciler.py:214-237`): supersede only if the subject
matches AND the goal is materially the same AND the new trace continues/retries/
extends/verifies/finishes; otherwise INSERT. Prompt B is a strawman: supersede
if the two records share a subject or topic.

The pair set has 20 true continuations and 30 negatives spanning parallel files,
different goals in the same area, different people/projects, context-only,
different causes, different periods, and uncertain cases.

### Initial pilot (20 pairs, Qwen2.5-7B)

| Rule | True supersede | False supersede | Accuracy |
|---|---|---|---|
| conservative | 6/8 | 0/12 | 18/20 |
| permissive | 8/8 | 4/12 | 16/20 |

### Scaled run (50 pairs × 3 models)

| Model | Rule | True supersede | False supersede | Accuracy |
|---|---|---|---|---|
| qwen2.5:7b | conservative | 17/20 | 1/30 | 46/50 |
| qwen2.5:7b | permissive | 19/20 | 17/30 | 32/50 |
| llama3.1:8b | conservative | 19/20 | **0/30** | **49/50** |
| llama3.1:8b | permissive | 20/20 | 9/30 | 41/50 |
| gemma3:4b | conservative | **8/20** | 0/30 | 38/50 |
| gemma3:4b | permissive | 19/20 | 3/30 | 46/50 |

Aggregate: conservative **44/60** true, **1/90** false, 133/150; permissive
**58/60** true, **29/90** false, 119/150.

**Reading:** "conservative" is not a property of the prompt; it is an
interaction between prompt and model. The same conservative rule missed 1/20
continuations on llama, 3/20 on qwen, and 12/20 on gemma (revision, extension,
retry, update, verify). Under the permissive rule, false merges ranged from
3/30 (gemma) to 17/30 (qwen). The best operating point is model-specific, and a
deployment needs per-model calibration plus a separate path for preference
updates, which the conservative rule missed on all three models (P03/P11).

## 3. Post-deletion recovery under summaries (`afterdelete_hierarchical.py`)

Extension of the AfterDeleteBench replication. Background + distractor records
plus one target (or a matched neutral record). Two summary constructions:

- **extractive**: all records joined verbatim into one summary;
- **model-written**: the model summarizes the records into three bullets.

### Initial pilot (10 profiles, Qwen2.5-7B)

| Variant | Condition | Recovered | Target in summary |
|---|---|---|---|
| extractive | forget (source deleted, summary kept) | 10/10 | 10/10 |
| extractive | clean (never exposed) | 0/10 | 0/10 |
| extractive | closure (summary retired) | 0/10 | 0/10 |
| model-written | forget | 0/10 | 0/10 |
| model-written | clean | 0/10 | 0/10 |

### Scaled run (50 profiles, Qwen2.5-7B)

| Variant | Condition | Recovered | Target in summary |
|---|---|---|---|
| extractive | forget | **50/50** | 50/50 |
| extractive | clean | **0/50** | 0/50 |
| extractive | closure | **0/50** | 0/50 |
| model-written | forget | **1/50** | **2/50** |
| model-written | clean | 0/50 | 0/50 |

The two model-written summaries that retained the secret are the interesting
part. Profile 22's summary said "Your access code is SOUTH-IPAV-782" and the
model recovered it. Profile 29's summary said "their access code is
SOUTH-KUWR-679" — the string survived, but the query "What is my access code?"
returned `UNKNOWN`. Presence in a summary is not the same as recoverability:
person, possessive, and query wording are part of the measurement.

**Reading:** with an extractive summary, deleting the source record removes
nothing behaviorally: the secret is in the summary and the model recovers it
50/50; provenance closure removes it 50/50. A model-written summary omitted the
secret in 48/50 cases, but not all: it retained it twice, recovered once.
That is not a deletion guarantee; it is one prompt's compression behavior, and
it can leak depending on phrasing. Evaluate deletion at the memory-system level
and distinguish "the summary happened to drop it" from "the mechanism removes
it".

## Limits

- One local model for deletion (`qwen2.5:7b`); three for conflict, temperature 0.
- 50 synthetic examples per conflict cell aggregation, 50 profiles for deletion;
  per-cell counts still do not support precise production rates.
- No upstream code was installed or executed; the decay formula was
  re-implemented from the Rust source, and the conflict prompt is a paraphrase.
- The model-written summary result depends on the instruction "three concise
  bullets"; a summary asked to preserve all secrets would behave differently.
- Nothing here validates the upstream systems' own benchmark claims.

## Rerun

```bash
python decay_sim.py
ollama pull qwen2.5:7b llama3.1:8b gemma3:4b
python conflict_pilot_50.py --out results/conflict_pilot_50.json
python afterdelete_hierarchical.py --profiles 50 --out results/afterdelete_hierarchical_50.json
python analyze_scaled.py results/conflict_pilot_50.json results/afterdelete_hierarchical_50.json
```

`decay_sim.py` is deterministic and needs only the standard library. The others
need a local Ollama server; the scaled conflict run is 300 calls and the
deletion run is ~300 calls, tens of minutes on a 6 GB GPU.
