# Related systems and memory pilots (Oct 2026)

Four open-source systems read in October 2026, plus three small pilots that
test mechanisms they implement. The systems were read, not installed; the pilots
use a local Qwen2.5-7B and synthetic data. This page is a comparison and a set
of testable borrowings, not an endorsement or a benchmark of the systems.

## Four systems

| System | What it is | Mechanism worth studying |
|---|---|---|
| [ai-memory](https://github.com/akitaonrails/ai-memory) | Long-term memory for coding agents; Rust binary, git-backed Markdown wiki | Four tiers (working/episodic/semantic/procedural), access-weighted decay, supersede-not-delete with `restore-page`, claim-once handoffs |
| [Hy-Memory](https://github.com/Tencent-Hunyuan/Hy-Memory) | Dual-process memory for self-evolving agents | L0–L7 hierarchy, conservative fact reconciliation, coding version-evolution diff chain, a memory benchmark (CMB) |
| [Harness²](https://arxiv.org/abs/2610.14224) | Recursive harness optimization for agents | Eight editable components (prompt, guardrails, memory, tool guidance, subagents, skills, scripts, plugins), Propose–Probe–Compose, parallel/sequential recursion |
| [context-mode](https://github.com/mksglu/context-mode) | MCP server that budgets the context window | Sandboxed `ctx_execute` (only printed output enters context), SQLite + FTS5 session continuity, auto-indexing outputs over ~5 KB |

### What is genuinely different in each

- **ai-memory** separates truth from index: Markdown in git is the source of
  truth, the database is rebuildable. Its default path uses zero LLM calls, and
  forgetting is reversible (tombstone → grace period → hard delete; restore from
  git). The handoff protocol is claim-once, and the design note records a real
  failure where an unrelated session consumed a handoff.
- **Hy-Memory** treats memory as a model, not a store. Facts are versioned,
  conflicts are resolved by a conservative rule (subject + materially same goal
  + continuation/retry/extension/verification), and coding sessions get a
  version-evolution diff chain so a reverted revision is still recoverable.
- **Harness²** makes the harness itself the optimization target and reports the
  component diff with each run; a failed judge is `None`, not zero. That is a
  three-state verdict in the same spirit as this repository's refusal taxonomy.
- **context-mode** enforces a context budget at the tool boundary: code runs in
  a subprocess and only its printed output is returned; large outputs are
  indexed and retrieved by search. Its execution tool is explicitly marked
  destructive and network-open, so the sandbox is a claim to verify.

## Three pilots

Scripts and raw records:
[`replications/2026-10-memory-pilots/`](../replications/2026-10-memory-pilots/).

### 1. Access-weighted decay is a weeks-scale extension, not immortality

Re-implementing ai-memory's retention formula with its defaults
(λ=0.02, σ=0.6, μ=0.04, threshold 0.20), a page last accessed 60 days before
the update survives **119 days** versus **81 days** for a never-accessed page
(1.47×). Twenty accesses at day 0 buy only **93 days**: the access term itself
has a ~17-day half-life (μ=0.04). With a 180-day half-life, retention is
**418 days** for every access pattern tested — the time term dominates and
access is invisible at the eviction margin.

At a fixed age, an old page with three accesses 30 days ago scores **0.3412**
(kept) while a 180-day-old unused page scores **0.0273** (evicted). The formula
does what it says; what it does not do is let one access pin a page for years.

### 2. Conservative conflict rules trade recall for precision

20 synthetic fact pairs (8 true continuations, 12 negatives), Qwen2.5-7B:

| Rule | True supersede | False supersede | Accuracy |
|---|---|---|---|
| Conservative (Hy-Memory-style) | 6/8 | **0/12** | 18/20 |
| Permissive (same subject/topic) | 8/8 | 4/12 | 16/20 |

The conservative rule never merged a parallel task, but missed two subtle
continuations (a preference update and an investigation that turned into a
fix). The permissive rule caught all continuations and merged four parallel
tasks. The false-merge cost is asymmetric: merging two sessions destroys their
separate history, while a missed continuation leaves a redundant fact. This
supports INSERT as the safe default, with a separate mechanism for preference
updates.

### 3. Deletion residue depends on the summarizer

Extending the AfterDeleteBench pilot to multi-record summaries, 10 profiles:

| Variant | Condition | Recovered | Target in summary |
|---|---|---|---|
| Extractive summary | forget (source deleted, summary kept) | **10/10** | 10/10 |
| Extractive summary | clean (never exposed) | **0/10** | 0/10 |
| Extractive summary | closure (summary retired) | **0/10** | 0/10 |
| Model-written summary | forget | **0/10** | **0/10** |
| Model-written summary | clean | 0/10 | 0/10 |

Extractive summaries preserve the deleted secret every time; provenance closure
removes it every time. Qwen's own three-bullet summary omitted the secret in
**10/10** cases, so recovery was zero. That is a property of one prompt, not a
deletion guarantee: the same memory system can leak or not leak depending on how
its summaries are written. Evaluate deletion at the memory-system level and
distinguish "the summary happened to drop it" from "the mechanism removes it".

## Four borrowings for this repository

1. **Truth/index separation.** Markdown/git or an event log plus FTS5 makes the
   store rebuildable; a vector index should never be the only copy.
2. **Supersede, don't destroy.** Version chains and tombstones make forgetting
   auditable and reversible; test what remains recoverable, not just that a row
   is gone.
3. **Record the harness as an independent variable.** A score without the
   harness configuration (or its diff hash) is not comparable to another score.
4. **Three-state verdicts.** A failed judge is `None`, not zero; `superseded` is
   not deleted; an unknown cache state is not a miss. Put the refusal in the
   schema.

These connect directly to the two 2026 papers already replicated here:
harness-induced success (`arXiv:2610.26632`) and post-deletion residue
(`arXiv:2610.31366`).

## Limits

- One local model, one prompt per condition, 10–20 synthetic examples; no
  meaningful confidence intervals.
- No upstream code was installed or executed. The decay formula was
  re-implemented from the Rust source; the conflict prompt is a paraphrase.
- Upstream benchmark claims (context reduction, harness gains, memory
  leaderboards) were not reproduced.
- The model-written summary result is prompt-dependent; it demonstrates a
  failure mode, not a fixed rate.
