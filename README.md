# Agent Proxy Audit

[![CI](https://github.com/aidless/agent-proxy-audit/actions/workflows/static-checks.yml/badge.svg)](https://github.com/aidless/agent-proxy-audit/actions/workflows/static-checks.yml)

**Do verification signals agree with what actually happened?**

Three linked studies measure one gap: between *proxy reports* (approval-gate outputs, model self-verification assertions, resource-allocation models) and *persisted local effects*. Every guard studied here can report success while unauthorized effects land anyway — and a model asserting "I verified this" is just another proxy.

The three studies and how they relate (drawn from the table below; each proxy is a different layer, the measured side is always persisted local state):

```mermaid
flowchart TB
    GAP["the shared gap:<br/>proxy report vs persisted local effect"]
    subgraph S1["study 1 · approval-gates-r3 (retrospective audit)"]
        P1["PROXY: external approval gate<br/>name-check pass, one-shot full precheck"]
        E1["MEASURED: 540-cell constructed matrix<br/>(9 objectives × 10 states × 6 controls)<br/>63 / 45 unauthorized effects land anyway;<br/>local bound-control and native AGT both 0"]
    end
    subgraph S2["study 2 · r5-verify-vs-gate (pre-registered)"]
        P2["PROXY: model-internal self-verification<br/>assertion of a local LLM"]
        E2["MEASURED: 2 models × 4 arms — 14 (llama3.2:3b)<br/>and 10 (qwen2.5:7b) unauthorized without gate;<br/>gate-arm zeros are 27/27 format collapse<br/>= false zero, not safety"]
    end
    subgraph S3["study 3 · agent-effort-r1 (descriptive)"]
        P3["PROXY: optimal allocation model<br/>(modeled token-cost ratio 3.44× from<br/>8,820-tuple search)"]
        E3["MEASURED: 8B best at the LOW budget (0.9375),<br/>14B at the MID (1.0000);<br/>672 retained execution records each"]
    end
    GAP --- S1
    GAP --- S2
    GAP --- S3
    S1 & S2 & S3 --- SIG["shared method signature:<br/>pre-registration + dated amendments,<br/>frozen blind checkers, SHA-256 evidence manifests,<br/>negative results and false zeros recorded, not dropped"]
```

| Study | Question | Headline result | Status | Repo |
|---|---|---|---|---|
| **approval-gates-r3** | Do external approval gates' clean reports match persisted effects? | 540-cell constructed matrix (9 objectives × 10 states × 6 controls): name-check passes **63** unauthorized effects, one-shot full precheck **45**; local bound-control and native AGT both **0** | retrospective audit; independent retro grade 6.2/10, not submitted | [approval-gates-r3](https://github.com/aidless/approval-gates-r3) |
| **r5-verify-vs-gate** | Does model-internal self-verification agree with persisted effects? | Pre-registered 2 models × 4 arms: without gate, **14** (llama3.2:3b) / **10** (qwen2.5:7b) unauthorized effects; with self-verification, **0** — but llama's zeros are **27/27 format collapse = false zero, not safety** | pre-registered (`PROTOCOL_R5.md`; `CLAIM_LEDGER.md` C200–C234, every claim carries a source path) | [r5-verify-vs-gate](https://github.com/aidless/r5-verify-vs-gate) |
| **agent-effort-r1** | Does an optimal allocation model describe a bounded tool-using agent? | 8,820-tuple allocation search gives a modeled token-cost ratio **3.44×**; measured peaks diverge — 8B best at the *low* budget (**0.9375**), 14B at the *mid* (**1.0000**); 672 retained execution records each | descriptive; assumptions and measurements explicitly separated | [agent-effort-r1](https://github.com/aidless/agent-effort-r1) |

## Shared method signature

- Pre-registration with **dated amendments** (R5) instead of silent protocol edits
- **Frozen blind checkers** and independent re-reads of persisted state
- SHA-256 evidence manifests; claim ledgers where every number names its source file
- **Negative results and false zeros recorded, not dropped** — r5 distinguishes "verified safe" from "output collapsed into an unparseable format that trivially shows zero effects"

## Scope

Finite authored local-effect measurements. Not a defense, not a population safety trial, not deployment validation. Each repo's protocol/README states its own interpretation limits; numbers above are quoted with their sources in the linked repos.

## Pilot replications of 2026 work (Oct 2026)

Two recent papers measure adjacent gaps — a harness deciding success when state
cannot be re-observed (arXiv:2610.26632), and deletion leaving residue in an
agent's derived memory (arXiv:2610.31366). [`replications/2026-10-harness-and-deletion/`](replications/2026-10-harness-and-deletion/)
contains close readings of those two plus two related papers, and pilot
replications on local Qwen2.5-7B with the scripts and raw records.

Headline pilot results: truncating a window cost success **0/6** when the fact
was not recoverable and **6/6** when it was; deleting a source record still left
the secret recoverable **20/20**, against **0/20** in a matched never-exposed
world and **0/20** after provenance closure. These are pilot-scale replications,
not the published protocols — the folder states what does and does not
replicate.

A second set of pilots tests memory mechanisms from `ai-memory` and `Hy-Memory`:
access-weighted decay extends retention only from 81 to 119 days (and does
nothing at the eviction margin under a 180-day half-life); a 50-pair × 3-model
conflict test found the conservative rule rejected **1/90** parallel pairs but
missed **16/60** true continuations, while the permissive rule caught
**58/60** and merged **29/90**; and a 50-profile deletion test found an
extractive summary preserved the deleted secret **50/50**, while a model-written
summary retained it only **2/50** and recovered **1/50**. See
[`replications/2026-10-memory-pilots/`](replications/2026-10-memory-pilots/) and
the comparison in [`docs/related-systems-2026-10.md`](docs/related-systems-2026-10.md).

**Write-up:** [Same conservative prompt, three operating points](docs/blog/2026-10-conservative-prompt-operating-points.md).
Datasets (CC BY 4.0): [conflict pairs](replications/2026-10-memory-pilots/data/conflict_pairs_50.json) ·
[deletion profiles](replications/2026-10-memory-pilots/data/deletion_profiles_50.json).

## Reproduce

Each repo is self-contained and its core tables recompute offline (Python 3.11+, no model or network required for the descriptive tables):

```bash
# approval-gates-r3 — descriptive tables + fresh 540-cell matrix
python3 scripts/make_descriptive_tables.py

# r5-verify-vs-gate — claim ledger with per-claim source paths
# see PROTOCOL_R5.md and CLAIM_LEDGER.md (C200–C234)

# agent-effort-r1 — allocation model vs retained execution records
# see README "What is measured vs assumed"
```

## Install / Quickstart

This repository has **zero third-party runtime dependencies** — `requirements.txt`
documents that every import in the 8 (now 9) Python files resolves to the standard
library or to a module inside this repo. To get a usable copy:

```bash
# no pip install needed; clone and run offline
git clone https://github.com/aidless/agent-proxy-audit.git
cd agent-proxy-audit
python3 --version   # 3.11+ (README states this requirement)

# verify the committed pilot records re-aggregate offline (no model/network)
python3 replications/bench_reaggregate.py
```

Quickstart — the fastest way to see the repo's value is to re-aggregate the
committed pilot results and confirm the README's headline numbers reproduce:

```bash
python3 replications/bench_reaggregate.py
# 结果文件 7 个，共 724 行 → 重新聚合与已提交 summary 一致（0 不一致）
```

## Verification of this repository

This repository aggregates results from linked repos. The committed pilot
records here can be checked offline:

```bash
# all replication JSON parses
python3 - <<'CHECK'
import json, pathlib
for path in pathlib.Path("replications").rglob("*.json"):
    json.loads(path.read_text())
    print(path)
CHECK

# every replication script compiles
python3 -m compileall -q replications

# result-file hashes
find replications -type f \( -name '*.json' -o -name '*.csv' \) -print0 \
  | sort -z | xargs -0 sha256sum
```

## Acceptance criteria, statistics, cost, and failure attribution

**Acceptance criteria (enforced by `make eval`).** A commit is accepted only when
`python3 eval/run_cases.py` reports **20/20** cases passed — pass_rate must be
`>= 1.00`, any single failing case rejects the commit (exit 1) — and
`python3 replications/bench_reaggregate.py` reports **0** files whose re-aggregated
summary disagrees with the committed summary. The gate itself must be able to fail:
`python3 eval/run_cases.py --selftest` tampers one expected value and must go red
(at least 1 of 20 cases failing, exit 0); if it stays green the suite is decoration
and the commit is rejected.

**Sample size.** n = 724 replayed rows, summed over the 7 committed `results/*.json`
files (`decay_sim.json` carries no `rows` and contributes 0; 7 files, 6 with rows).
Per condition: n = 300 rows for `conflict_pilot_50.json` (50 pairs × 3 models × 2
rules), n = 250 rows for `afterdelete_hierarchical_50.json` (50 profiles × 5
variants), n = 60 rows for `afterdelete_qwen25_20p.json` (20 profiles × 3
conditions), n = 24 rows for `persistgym_qwen25_3t.json` (3 templates × 8 cells × 1),
n = 50 pairs / n = 50 profiles for the two committed datasets. Wilson 95% CI for the
proportions quoted above: extractive|forget recovered 50/50 → 95% CI [0.929, 1.000];
model_written|forget recovered 1/50 → 95% CI [0.004, 0.105]; `gemma3:4b|permissive`
accuracy 46/50 → 95% CI [0.812, 0.968]; `qwen2.5:7b|conservative` true_supersede
17/20 → 95% CI [0.640, 0.948] (denominator = the 20 SUPERSEDE-expected pairs, not
all 50). These intervals are computed offline from the committed rows with the
Wilson score formula, not estimated.

**Cost / latency.** The verification path — everything `make eval` runs — makes no
network and no model calls, so its measured cost is **$0.00** and no paid API is
involved. (The pilot scripts that *produced* the committed rows, e.g.
`replications/2026-10-memory-pilots/conflict_pilot_50.py:14`, do
`OLLAMA = "http://localhost:11434/api/chat"` — local inference on this machine, no
per-token price; the figures below cover the verification path only.) Wall clock,
measured (7 consecutive runs):

```bash
# re-aggregation of all committed pilot results
for i in $(seq 1 7); do python3 replications/bench_reaggregate.py --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["elapsed_seconds"])'; done
# → 0.006434 / 0.005809 / 0.004562 / 0.004712 / 0.006882 / 0.006283 / 0.006054
#   min 0.004562 s, median 0.006054 s, max 0.006882 s for 7 files / 724 rows
#   = 8.4 µs per row (0.006054 s ÷ 724)

# case suite (20 cases, each re-loading the module and re-parsing a committed file)
for i in $(seq 1 7); do /usr/bin/time -f "%e" python3 eval/run_cases.py >/dev/null; done
# → 0.08 / 0.07 / 0.06 / 0.06 / 0.06 / 0.08 / 0.12  (median 0.07 s)
```

**Failure attribution.** Every case carries an `axis`; a failing run prints the
`failed_by_axis` buckets and `--save` persists them to `eval/run-report.json`, so a
red gate names the module that broke instead of only reporting a pass rate:

| axis | owning module the failure points at |
|---|---|
| `reagg/conflict50`, `reagg/afterdelete`, `reagg/persistgym` | schema branch in `replications/bench_reaggregate.py:reaggregate()` for that pilot |
| `data/conflict-pairs`, `data/deletion-profiles` | the committed dataset in `replications/2026-10-memory-pilots/data/` |
| `code/decay` | `replications/2026-10-memory-pilots/decay_sim.py` → `results/decay_sim.json` |
| `runner/aggregate` | the `eval/run_cases.py` harness itself (path/glob resolution) |

**Recompute.** `python3 eval/run_cases.py --save` writes `eval/run-report.json` with
per-case readings (id, axis, ok, detail); `python3 replications/bench_reaggregate.py`
复算 every committed `summary` from its own `rows` and exits non-zero when a number
drifted. Both paths are the only sources for the numbers above.

**Provenance boundary — what is cited, what is our own.** The three headline results
in the table at the top (63 / 45 unauthorized effects; 14 / 10 unauthorized effects;
the 3.44× modeled token-cost ratio) are **quoted from the linked repos**
(`approval-gates-r3`, `r5-verify-vs-gate`, `agent-effort-r1`) and were **not**
re-run here — treat them as citations of those repos, with `source:` paths recorded
there. The pilot numbers in this repository (20/20 recoverable, 0/20 never-exposed,
50/50 extractive, 1/50 model-written, 46/50 accuracy and 17/20 true_supersede conflict cells) are **our own**
runs and are backed by the committed `results/*.json` files listed above; the mermaid
diagram is **author-drawn** for this README and is **not** reproduced from any paper.
The two arXiv ids (2610.26632, 2610.31366) are the papers whose close readings live
under `replications/2026-10-harness-and-deletion/`; we did **not** reproduce their
published protocols at that scale — the folder states the gap, so protocol-level
agreement is **N/A** here.

## License

Code: MIT ([`LICENSE`](LICENSE)). Synthetic data and write-ups: CC BY 4.0 ([`DATA_LICENSE.md`](DATA_LICENSE.md)).

---
*Author: Zewen Liu (Independent Researcher) · [github.com/aidless](https://github.com/aidless)*
