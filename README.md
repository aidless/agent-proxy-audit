# Agent Proxy Audit

[![CI](https://github.com/aidless/agent-proxy-audit/actions/workflows/static-checks.yml/badge.svg)](https://github.com/aidless/agent-proxy-audit/actions/workflows/static-checks.yml)

<!-- BEGIN PROBLEM -->
This repository is a catalog of proxy-versus-effect studies: an approval-gate report, a self-verification assertion, or an allocation model can disagree with the persisted local effect.
Headline numbers are quotes from sister repositories, or counts recounted from pilot JSON committed in this clone. Sister studies are not re-run here.
A figure with no sibling path and no committed pilot file is labeled UNKNOWN. Nothing on this page is a safety evaluation.
<!-- END PROBLEM -->

**STATUS: WORK-IN-PROGRESS** — index satellite. The gaps below are why this catalog is not a standalone grade A study.

## Gaps before A

- The primary corpora live in the sister repositories. This clone does not contain the constructed matrix, the R5 result trees, or the effort execution records, and the offline check does not rebuild them.
- Sister cells are snapshots taken on the observed date at the commits named in the table. A later sister commit can move a cell while this page still shows the old quote.
- Pilot-row cells are recounted from committed JSON. Decay cells are recomputed in-process. Neither step calls a model, so a fresh serving run is not part of the evidence.
- The pilots are small local procedures. Their folder notes say where they depart from the published protocols. Close-reading rates of external papers in those notes are outside the ledger below.
- The status stays work in progress until a primary corpus and its offline recompute live in this clone. Cataloguing sisters does not supply that corpus.

Failure modes: [`FAILURE_MODES.md`](FAILURE_MODES.md). Machine-readable ledger: [`quotes/headline_quotes.json`](quotes/headline_quotes.json).

## Quoted cells

<!-- BEGIN QUOTED CELLS -->
| Cell | Value | What it is | Source |
|---|---|---|---|
| gates.constructed_cells | 540 | Constructed local-effect cells. Arithmetic check only: 9 x 10 x 6 = 540. The matrix was not rebuilt in this clone. | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9000 evidence/supplement/summary.json constructed_cells; factorization stated in ROUND_R3.md (9 objectives x 10 states x 6 controls); not recomputed in this clone |
| gates.name_only_unauthorized | 63 | Unauthorized effects admitted by the name-only control on the constructed matrix, while the name/log proxy stays positive (abstract.txt). | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9044 evidence/supplement/summary.json e03.name_only.unauthorized_effects; also abstract.txt name-only control; not recomputed in this clone |
| gates.exact_precheck_unauthorized | 45 | Unauthorized effects admitted by the exact-precheck control on the constructed matrix. | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9028 evidence/supplement/summary.json e03.exact_precheck.unauthorized_effects; ROUND_R3.md calls this the one-shot full precheck; not recomputed in this clone |
| gates.local_execution_bound_unauthorized | 0 | Unauthorized effects for local execution binding on the constructed matrix. Zero is also the deny-all count (C9020). Not a safety claim. | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9036 evidence/supplement/summary.json e03.local_execution_bound.unauthorized_effects; not recomputed in this clone |
| gates.native_agt_unauthorized | 0 | Unauthorized effects for the pinned native AGT control on the constructed matrix. Not a safety claim and not a new method (ROUND_R3.md). | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9052 evidence/supplement/summary.json e03.native_agt.unauthorized_effects; not recomputed in this clone |
| gates.deny_all_unauthorized | 0 | Deny-all also has 0 unauthorized effects on the constructed matrix. abstract.txt pairs that zero with zero clean utility. | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 CLAIM_LEDGER.md — C9020 evidence/supplement/summary.json e03.deny_all.unauthorized_effects; abstract.txt says deny-all has zero clean utility; not recomputed in this clone |
| gates.review_score | 6.2 | Uncalibrated independent AI review score, rounded from 6.225. Not peer review, not an acceptance probability, and not a submission. | sibling quote observed 2026-11-09; aidless/approval-gates-r3@80981521d651b4b96d69b8afd44f86dd17e42df4 reviews/approval-r3-independent-r0.md — Uncalibrated independent AI score; weighted total 6.225/10, rounded 6.2/10. README.md of that repo repeats 6.2/10 as uncalibrated.; not recomputed in this clone |
| r5.llama_arm_a_unauthorized | 14 | llama3.2:3b arm A unauthorized effects on the Amendment-4 temptation set (allow_all, no self-verification instruction). | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C200 results-tempt-v3/llama3.2/arm_a/summary.json unauthorized_effects; README.md temptation table arm A allow_all, no verify instruction; not recomputed in this clone |
| r5.qwen_arm_a_unauthorized | 10 | qwen2.5:7b arm A unauthorized effects on the same temptation set (allow_all, no self-verification instruction). | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C212 results-tempt-v3/qwen2.5/arm_a/summary.json unauthorized_effects; not recomputed in this clone |
| r5.llama_arm_b_false_zero | 0 unauthorized; 27/27 unparseable | llama3.2:3b arm B (allow_all plus self-verification). Format collapse: every cell unparseable, so the zero unauthorized count is a false zero, not containment. | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C203 unauthorized_effects=0 and C205 unparseable=27 on results-tempt-v3/llama3.2/arm_b/summary.json; README.md section Three different zeros; not recomputed in this clone |
| r5.qwen_arm_b_parsed_zero | 0 unauthorized; 0 unparseable | qwen2.5:7b arm B parsed stops with a self-verification instruction. A behavior change on this fixture relative to arm A. Not a safety result; see r5.primary_endpoint_empty. | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C215 unauthorized_effects=0 and C217 unparseable=0 on results-tempt-v3/qwen2.5/arm_b/summary.json; not recomputed in this clone |
| r5.llama_arm_c_bound_zero | 0 | llama3.2:3b arm C unauthorized effects under local execution binding, with output still parseable. The sister README says the model made the same act attempts as arm A and the binding denied them. | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C206 unauthorized_effects on results-tempt-v3/llama3.2/arm_c/summary.json; C208 unparseable=0. README.md Three different zeros, item 2; not recomputed in this clone |
| r5.primary_endpoint_empty | 0 | Temptation cells in which the model both acted and emitted a verification assertion. The primary endpoint is defined only on this subset, so it is empty. Not a safety result. | sibling quote observed 2026-11-09; aidless/r5-verify-vs-gate@6aad5a246c0c3cdde5dd1a52d24446fd10b684a1 CLAIM_LEDGER.md — C404 results-tempt-v3 acting-path cells with emitted_assertion; README.md says the primary false-negative endpoint is empty for that structural reason; not recomputed in this clone |
| effort.n_allocations | 8820 | Allocation tuples searched. A grid count, not a count of agent episodes. | sibling quote observed 2026-11-09; aidless/agent-effort-r1@878e48c7ae96943f78d9da2fe5c422aa1ab9ab55 results/stats.json — E2_allocation.n_allocations; README.md also prints 8,820 tuples; not recomputed in this clone |
| effort.cost_ratio_vs_fixed_mid | 3.4402002147712176 | Modeled token-cost ratio versus the fixed-middle baseline at matched modeled success. 3.44 and 3.4402 in the sister README are roundings of this field. The sister text says allocation gains and token prices are assumptions, not measured deployment benefits. | sibling quote observed 2026-11-09; aidless/agent-effort-r1@878e48c7ae96943f78d9da2fe5c422aa1ab9ab55 results/stats.json — E2_allocation.vs_fixed_mid.cost_ratio_baseline_over_unified_at_matched_success; README.md prints 3.44 and 3.4402; not recomputed in this clone |
| effort.qwen3_8b_low_budget_success | 0.9375 | Qwen3-8B retained-record success at the low budget (L1_low). The sister README calls this the low-budget peak. | sibling quote observed 2026-11-09; aidless/agent-effort-r1@878e48c7ae96943f78d9da2fe5c422aa1ab9ab55 results/h4_derived_stats.json — iso_curve.L1_low.success; n_records in results/h4_real_llm_gx_qwen3_8b.json is the separate 672 cell; not recomputed in this clone |
| effort.qwen3_14b_mid_budget_success | 1.0 | Qwen3-14B retained-record success at the middle budget (L2_mid). The sister README prints 1.0000 for this field. | sibling quote observed 2026-11-09; aidless/agent-effort-r1@878e48c7ae96943f78d9da2fe5c422aa1ab9ab55 results/h4_derived_stats_14b.json — iso_curve.L2_mid.success; sister README prints 1.0000; not recomputed in this clone |
| effort.retained_records_each | 672 | Retained execution records in each of the two Qwen3 case-study files. Descriptive records, not an independent sample for a general decline (sister README). | sibling quote observed 2026-11-09; aidless/agent-effort-r1@878e48c7ae96943f78d9da2fe5c422aa1ab9ab55 results/h4_real_llm_gx_qwen3_8b.json — n_records on results/h4_real_llm_gx_qwen3_8b.json and the same field on results/h4_real_llm_gx_qwen3_14b_persist.json; not recomputed in this clone |
| pilot.window_unrecoverable_success | 0/6 | Truncated-window successes when the fact is not recoverable, observed and derived rows combined. Pilot, not the published PersistGym protocol. | pilot rows recounted from committed JSON; replications/2026-10-harness-and-deletion/results/persistgym_qwen25_3t.json |
| pilot.window_recoverable_success | 6/6 | Truncated-window successes when the fact is recoverable. Same pilot file. | pilot rows recounted from committed JSON; replications/2026-10-harness-and-deletion/results/persistgym_qwen25_3t.json |
| pilot.afterdelete_forget | 20/20 | Secrets recovered after source deletion when the extractive summary remains. Pilot channel, not the published AfterDeleteBench rate. | pilot rows recounted from committed JSON; replications/2026-10-harness-and-deletion/results/afterdelete_qwen25_20p.json |
| pilot.afterdelete_clean | 0/20 | Recoveries in the matched never-exposed world of that 20-profile pilot. | pilot rows recounted from committed JSON; replications/2026-10-harness-and-deletion/results/afterdelete_qwen25_20p.json |
| pilot.afterdelete_closure | 0/20 | Recoveries after the summary is retired in that 20-profile pilot. | pilot rows recounted from committed JSON; replications/2026-10-harness-and-deletion/results/afterdelete_qwen25_20p.json |
| pilot.decay_never_accessed | 81 | Days until the cold threshold for a never-accessed page at lambda 0.02. Recomputed by decay_sim.build_report. Formula re-implemented from the cited Rust lines; upstream code was not executed. | recomputed by decay_sim.build_report each check; replications/2026-10-memory-pilots/results/decay_sim.json |
| pilot.decay_five_accesses_day_60 | 119 | Days until the cold threshold for 5 accesses with last access at day 60, lambda 0.02. This is the 119-day cell, not every access pattern. | recomputed by decay_sim.build_report each check; replications/2026-10-memory-pilots/results/decay_sim.json |
| pilot.decay_ratio_day_60 | 1.47 | Access-weighted days divided by pure-age days for the day-60 pattern, rounded to two decimals in decay_sim.json. | recomputed by decay_sim.build_report each check; replications/2026-10-memory-pilots/results/decay_sim.json |
| pilot.decay_180_all_patterns | 418 | Every 180-day half-life pattern in decay_sim.json crosses the threshold on this same day. Access does not move the eviction day in that grid. | recomputed by decay_sim.build_report each check; replications/2026-10-memory-pilots/results/decay_sim.json |
| pilot.conflict_conservative_missed_true | 16/60 | Expected-SUPERSEDE rows the conservative rule did not label SUPERSEDE, across 3 models x 20 pairs. The positive class includes continuation, revision, extension, retry, verify, update, and preference_update. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/conflict_pilot_50.json |
| pilot.conflict_conservative_false_merge | 1/90 | Expected-INSERT rows the conservative rule labeled SUPERSEDE, across 3 models x 30 negatives. The single row is qwen2.5:7b N25, category different_decisions. It is not a parallel-file cell. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/conflict_pilot_50.json |
| pilot.conflict_permissive_caught_true | 58/60 | Expected-SUPERSEDE rows the permissive rule labeled SUPERSEDE, across the three models. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/conflict_pilot_50.json |
| pilot.conflict_permissive_false_merge | 29/90 | Expected-INSERT rows the permissive rule labeled SUPERSEDE, across the three models. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/conflict_pilot_50.json |
| pilot.hier_extractive_forget_recovered | 50/50 | Extractive-summary forget condition: query recovered the deleted secret. 50-profile pilot, qwen2.5:7b. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/afterdelete_hierarchical_50.json |
| pilot.hier_model_written_forget_in_summary | 2/50 | Model-written forget summaries that still contain the secret string. | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/afterdelete_hierarchical_50.json |
| pilot.hier_model_written_forget_recovered | 1/50 | Model-written forget condition: query recovered the secret. Presence in the summary (2/50) is a different count from recovery (1/50). | pilot rows recounted from committed JSON; replications/2026-10-memory-pilots/results/afterdelete_hierarchical_50.json |
<!-- END QUOTED CELLS -->

## What this clone contains

Committed pilot records and a standard-library decay recompute live under [`replications/`](replications/). The two folders state their own limits:

- [`replications/2026-10-harness-and-deletion/`](replications/2026-10-harness-and-deletion/)
- [`replications/2026-10-memory-pilots/`](replications/2026-10-memory-pilots/)

Memory-pilot write-up: [Same conservative prompt, three operating points](docs/blog/2026-10-conservative-prompt-operating-points.md). Comparison notes: [`docs/related-systems-2026-10.md`](docs/related-systems-2026-10.md). Datasets (CC BY 4.0): [conflict pairs](replications/2026-10-memory-pilots/data/conflict_pairs_50.json), [deletion profiles](replications/2026-10-memory-pilots/data/deletion_profiles_50.json).

Sister packages, which hold the primary evidence and their own recompute commands:

- [approval-gates-r3](https://github.com/aidless/approval-gates-r3)
- [r5-verify-vs-gate](https://github.com/aidless/r5-verify-vs-gate)
- [agent-effort-r1](https://github.com/aidless/agent-effort-r1)

Those commands are not scripts in this repository. Running them requires a checkout of the sister, not a fresh clone of this index.

## Offline check

From a fresh clone, with Python 3.11 or newer and no third-party packages:

```bash
python3 scripts/check_index.py
```

The command compiles every Python file, parses every JSON file, recounts committed pilot rows, recomputes the decay report, and checks the quoted-cell block against the ledger. It does not call a model or the network. The work is a local file scan of this repository.

## License

Code: MIT ([`LICENSE`](LICENSE)). Synthetic data and write-ups: CC BY 4.0 ([`DATA_LICENSE.md`](DATA_LICENSE.md)).

---
*Author: Zewen Liu (Independent Researcher) · [github.com/aidless](https://github.com/aidless)*
