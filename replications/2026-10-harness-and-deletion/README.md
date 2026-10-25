# Pilot replications: harness truncation and post-deletion residue (Oct 2026)

Two recent papers ask questions close to this repository's thesis. This folder
contains a close reading of four papers and pilot-scale replications of two of
them, with the scripts and the raw result records.

**Status: pilot, not a replication of the published protocols.** Local
Qwen2.5-7B-Instruct via Ollama, small samples, no pre-registration, and a much
smaller context window than the papers use. Directional agreement is the claim;
the published rates are not.

## Papers read

### 1. *When the harness decides success: state that cannot be re-observed* (arXiv:2610.26632, 2026-10-19)

Raimondas Lencevicius (Microsoft). Agent harnesses choose what survives context
growth. The paper separates two cases that cost accounting conflates: a fact
that is dropped but **can be looked up again**, and a fact that is dropped and
**cannot be re-observed**. In `PersistGym-lite` (observed/derived fact ×
recoverable/not × near/far, 200 templates, 10-way answer), truncating the window
cost a confirmatory model almost nothing when the fact was recoverable (100%)
and dropped it to 7.5% when it was not (chance 10%): Δ = **+92.5 points**
(90% CI [89.5, 95.5]). A pre-registered replication on a second provider's model
gave 0/200 vs 200/200, Δ = **+101.0 points**. On ARC-AGI-3, replacing truncation
with summarization recovered **86%** of a 63-point Standard-to-Adapter gap;
removing the note-taking instruction and adding native reasoning replay account
for the rest, as point estimates from one run per configuration and game.

**Limits the paper states:** one model per provider; synthetic probe; ARC shares
are one run per cell over four selected games; replay is bundled with the
provider's item format; costs are provider-specific.

### 2. *AfterDeleteBench: Auditing Post-Deletion Information Persistence in LLM Agents* (arXiv:2610.31366, 2026-10-22)

Saleh et al. (Ohio State). Fixed-weight agents with external memory can retain a
deleted record through **derived state** (summaries). Paired worlds —
exposed-then-deleted vs matched never-exposed — attribute recovery to the
exposure. Primary Qwen2.5-7B setting: a single direct query recovers the deleted
secret in **ΔRec = 0.680** of IID profiles [0.615, 0.745] and **0.640** OOD
[0.575, 0.705]; clean controls recover **0/200**. Recovery does not need a
surviving literal: components stored separately under a public composition rule
give 0.615–0.990 across Qwen, Mistral and Phi-3. Provenance-aware closure
removes the tracked descendant channel (0), while a write-time exact-literal
gate blocks reinsertion but cannot erase existing residue. The response contract
is part of the measurement: parser/format mismatches can hide target-bearing
replies and even reverse an apparent write effect on matched states.

**Limits:** synthetic exact-string targets, a controlled extractive memory.
Natural-language and semantic secrets, learned/compressed memory, incomplete
provenance and production systems remain open.

### 3. *Who Verifies the Agent's Success Claim? Self-Report Leakage in GUI-Agent Completion Judging* (arXiv:2610.29609, 2026-10-21)

Zhu et al. A **dangerous misreport** is an unhedged success claim the execution
trace does not support. The AWARE/BLIND intervention shows self-report leakage:
the same judge reads the same task and trace, and only the agent's self-report
is included or withheld. Withholding it raises trace-only dangerous-misreport
recall by **43.4 points** (Qwen3.5-35B-A3B) and **13.3 points**
(DeepSeek-284B-A13B), with the same trend held out. Their structured auditor
separates claim interpretation from claim-blind trace analysis and reaches
F1 0.75–0.78 on 465 records (0.77–0.81 held out). This is the same separation
this repository's r5 study makes between a self-verification assertion and a
persisted effect.

### 4. *Auditing the Product, Not the Recursion: The Evaluation Evidence Behind Recursive Self-Improvement Claims* (arXiv:2610.27610, 2026-10-20)

Chen, Zhu and Zheng. Full-text coding of 114 eligible studies (90 describe
themselves as recursive self-improvement). Product evaluation is common (90%
report evaluation beyond development tasks under a broad criterion), but process
evidence is thin: only **22%** audit two or more reruns of the full loop (14% in
a human-coded sample), and of 26 studies claiming a better improvement
procedure, only **4** compare earlier and later procedures from identical
starting artifacts at a matched budget. Three mechanisms explain why product
scores do not establish process claims: selection effects, shared evaluator
errors, and changes in system state.

## Replication 1: truncation × re-observability

**Design (pilot).** Six-step episodes: one session fact (observed, or derived
from two parts plus a rule), four routine turns, then a need step with ten
options. Harnesses: full history, or a 180-character history budget that
**always keeps the current request** and drops older turns. Recoverable cells
offer a `LOOKUP` action that re-shows the fact; non-recoverable cells do not.
Three templates × four cells × two harnesses = 24 episodes. Model:
`qwen2.5:7b`, temperature 0.

**Result** (`results/persistgym_qwen25_3t.json`):

| Cell | Full history | Truncated window |
|---|---|---|
| observed, not recoverable | 3/3 | **0/3** |
| observed, recoverable | 3/3 | **3/3** (3/3 lookups) |
| derived, not recoverable | 3/3 | **0/3** |
| derived, recoverable | 3/3 | **3/3** (3/3 lookups) |

The recoverable/non-recoverable contrast at a truncated window is
**+100 points** (6/6 vs 0/6) in this pilot, with the same direction as the
paper's +92.5 and +101.0. Every recoverable window episode chose `LOOKUP`;
the full-history episodes never did.

**What this does not show:** the paper's exact rates, the note-taking and
summarization arms, ARC-AGI-3, or transfer to other models. An earlier pilot run
had a harness bug — the window also dropped the current request — and is not
reported as evidence; the fix is in `visible()`.

## Replication 2: post-deletion residue

**Design (pilot).** For each of 20 synthetic secrets (`REGION-MNEMONIC-NUMBER`),
memory holds background records plus the target record; an extractive summary
joins the records before deletion. Worlds: **forget** (delete the source record,
keep the summary), **clean** (matched neutral record), **closure** (retire the
summary). A single direct query asks for the code; scoring is exact substring,
case-insensitive.

**Result** (`results/afterdelete_qwen25_20p.json`):

| Condition | Recovered |
|---|---|
| forget (source deleted, summary retained) | **20/20** |
| clean (never exposed) | **0/20** |
| closure (summary retired) | **0/20** |

The channel replicates: source-level deletion does not remove information
carried by the derived summary, and a matched never-exposed world recovers
nothing. Our 20/20 rate is higher than the paper's ~2/3 because the pilot's
summary is a single verbatim join, so the secret is plainly visible; the paper's
rate comes from a more realistic pipeline. This shows the **channel**, not the
published rate.

## What replicates and what does not

- **Replicates:** the direction of both effects; the zero clean-control rate;
  provenance closure removing the tracked descendant; lookup restoring success
  when the fact is re-observable.
- **Does not replicate:** exact rates, other models/providers, the ARC-AGI-3
  decomposition, note-taking/summarization arms, response-contract reversal,
  adaptive auditors, or the RSI/self-report studies (read, not rerun).

## Rerun

```bash
ollama pull qwen2.5:7b
python persistgym_mini.py --templates 3 --model qwen2.5:7b --out results/persistgym.json
python afterdelete_mini.py --profiles 20 --model qwen2.5:7b --out results/afterdelete.json
```

Both scripts need only the Python standard library and a local Ollama server.
Runtime is minutes on a 6 GB laptop GPU. Results are deterministic at
temperature 0 except for model-serving nondeterminism.

## Why this belongs here

The papers supply benchmarks and failure taxonomies for the same gap this
repository measures: a proxy (a harness report, a summary, a success claim) is
not the persisted effect. The replications are deliberately small; their purpose
is to check that the mechanisms reproduce on a model and harness we can inspect,
not to compete with the published sweeps.
