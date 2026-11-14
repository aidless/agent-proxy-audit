# agent-proxy-audit — offline verification entry point.
#
# `make eval` is the single gate the acceptance criteria in README name:
#   1) every committed JSON parses and every script compiles (no network, no model)
#   2) eval/run_cases.py           -> must be 20/20 (exit 1 on any failed case)
#   3) eval/run_cases.py --selftest -> must go red (19/20, exit 0); green here = decoration
#   4) replications/bench_reaggregate.py -> 0 files inconsistent with their committed summary
PY ?= python3

.PHONY: eval verify cases selftest reaggregate

eval: verify
	$(PY) eval/run_cases.py
	$(PY) eval/run_cases.py --selftest
	$(PY) replications/bench_reaggregate.py

verify:
	$(PY) -m compileall -q replications eval
	$(PY) -c "import json,pathlib; fs=sorted(pathlib.Path('replications').rglob('*.json')); [json.loads(p.read_text(encoding='utf-8')) for p in fs]; print(f'{len(fs)} json files parse')"
	$(PY) -c "import json,pathlib; rows=[json.loads(l) for l in pathlib.Path('eval/cases.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]; assert len(rows)==20, len(rows); assert all(isinstance(r,dict) for r in rows); print(f'{len(rows)} cases, shape ok')"

cases:
	$(PY) eval/run_cases.py

selftest:
	$(PY) eval/run_cases.py --selftest

reaggregate:
	$(PY) replications/bench_reaggregate.py
