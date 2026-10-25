"""Scaled conflict pilot: 3 local models x 50 pairs (20 positives, 30 negatives).

Same two prompts as conflict_pilot.py. The expanded set adds parallel files,
unrelated features, different periods, uncertain cases and preference-domain
negatives. Local Ollama; report is directional, not a benchmark of Hy-Memory.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/chat"

# (id, old, new, expected, category)
PAIRS = [
    # ---- 20 positives: same subject, same goal, continuation/retry/update ----
    ("P01", "The CI fix in auth/session.py is in progress; retry the test job.",
     "The retry failed on the same test; add a fixture and rerun.", "SUPERSEDE", "continuation"),
    ("P02", "Deploying billing-api v2 to staging; waiting on the migration.",
     "Migration finished; canary deploy to staging next.", "SUPERSEDE", "continuation"),
    ("P03", "User prefers pytest for Python tests.",
     "User now prefers pytest with uv; keep the old preference superseded.", "SUPERSEDE", "preference_update"),
    ("P04", "Investigating a flaky test in orders_test.py; suspect the clock.",
     "Found the clock seed issue; fix it and verify the test.", "SUPERSEDE", "diagnosis_to_fix"),
    ("P05", "Refactor parse_config to remove globals; step 1 done.",
     "Step 2: move defaults into a dataclass.", "SUPERSEDE", "extension"),
    ("P06", "Rerunning experiment E7 after fixing the data split.",
     "E7 rerun finished with the same split; analysis pending.", "SUPERSEDE", "continuation"),
    ("P07", "Drafting the related-work section for paper X.",
     "Revised the related-work section after a reviewer comment.", "SUPERSEDE", "revision"),
    ("P08", "Debugging OOM in the training job on A100.",
     "OOM traced to batch size; retry with gradient accumulation.", "SUPERSEDE", "retry"),
    ("P09", "Fixing the login redirect bug in auth/session.py.",
     "Redirect fix works locally; add a regression test.", "SUPERSEDE", "verify"),
    ("P10", "Deploy billing-api v2 to staging; waiting on the migration.",
     "Staging deploy failed on the migration; retry after rollback.", "SUPERSEDE", "retry"),
    ("P11", "User prefers morning meetings.",
     "User now prefers afternoon meetings.", "SUPERSEDE", "preference_update"),
    ("P12", "Investigating a slow query in the orders API.",
     "Slow query traced to a missing index; add it.", "SUPERSEDE", "diagnosis_to_fix"),
    ("P13", "Drafting the abstract for paper X.",
     "Revised the abstract after feedback.", "SUPERSEDE", "revision"),
    ("P14", "Training run E12 stopped at epoch 3.",
     "Resumed E12 from the checkpoint and finished.", "SUPERSEDE", "continuation"),
    ("P15", "Refactor the config parser; step 1 removes globals.",
     "Step 2 removes the hidden defaults.", "SUPERSEDE", "extension"),
    ("P16", "Writing tests for the payment module.",
     "Payment tests pass; add edge cases for refunds.", "SUPERSEDE", "extension"),
    ("P17", "User's timezone is UTC+8.",
     "User moved to UTC+9; update the timezone.", "SUPERSEDE", "update"),
    ("P18", "Debugging a Docker build failure.",
     "Docker build fixed by pinning the base image.", "SUPERSEDE", "finish"),
    ("P19", "Planning the migration to Postgres.",
     "Migration plan approved; start the schema copy.", "SUPERSEDE", "continuation"),
    ("P20", "Drafting related work for paper X.",
     "Related work revised after a reviewer comment.", "SUPERSEDE", "revision"),

    # ---- 30 negatives: parallel, different goals, uncertain, different period ----
    ("N01", "Fixing CI in auth/session.py.",
     "Adding docstrings to auth/session.py.", "INSERT", "same_file_different_goal"),
    ("N02", "Optimizing performance in orders.py.",
     "Improving error handling in orders.py.", "INSERT", "same_file_different_goal"),
    ("N03", "Updating the README install section.",
     "Updating the README license section.", "INSERT", "same_file_different_goal"),
    ("N04", "Refactor billing/models.py.",
     "Refactor billing/views.py.", "INSERT", "different_files"),
    ("N05", "Refactor auth/session.py.",
     "Refactor auth/tokens.py.", "INSERT", "different_files"),
    ("N06", "Writing tests/test_api.py.",
     "Writing tests/test_db.py.", "INSERT", "different_files"),
    ("N07", "Alice prefers dark mode.",
     "Bob prefers dark mode.", "INSERT", "different_people"),
    ("N08", "Alice prefers pytest.",
     "Bob prefers pytest.", "INSERT", "different_people"),
    ("N09", "Team A uses Postgres.",
     "Team B uses Postgres.", "INSERT", "different_people"),
    ("N10", "Use pytest in project A.",
     "Use pytest in project B.", "INSERT", "different_projects"),
    ("N11", "Use Docker for local dev in project X.",
     "Use Docker for local dev in project Y.", "INSERT", "different_projects"),
    ("N12", "Use uv in repo A.",
     "Use uv in repo B.", "INSERT", "different_projects"),
    ("N13", "Use the retry helper from the CI fix.",
     "Write docs for the release process.", "INSERT", "context_only"),
    ("N14", "Use the schema from the migration plan.",
     "Write onboarding docs.", "INSERT", "context_only"),
    ("N15", "Reuse the fixture from the payment tests.",
     "Update the changelog.", "INSERT", "context_only"),
    ("N16", "OOM in job 42 due to batch size.",
     "OOM in job 77 due to a memory leak.", "INSERT", "different_cause"),
    ("N17", "500 error in checkout due to a null field.",
     "500 error in checkout due to a timeout.", "INSERT", "different_cause"),
    ("N18", "Flaky test due to the clock.",
     "Flaky test due to the network.", "INSERT", "different_cause"),
    ("N19", "Add a login page to repo X.",
     "Add a billing page to repo X.", "INSERT", "unrelated_feature"),
    ("N20", "Add dark mode to repo X.",
     "Add CSV export to repo X.", "INSERT", "unrelated_feature"),
    ("N21", "Build the search API for repo X.",
     "Build the audit log for repo X.", "INSERT", "unrelated_feature"),
    ("N22", "User prefers dark mode.",
     "User prefers tabs over spaces.", "INSERT", "different_preference_domain"),
    ("N23", "User prefers morning meetings.",
     "User prefers four-space indentation.", "INSERT", "different_preference_domain"),
    ("N24", "Meeting decided to use Postgres.",
     "Meeting decided to delay the launch.", "INSERT", "different_decisions"),
    ("N25", "Meeting decided to hire two engineers.",
     "Meeting decided to freeze hiring.", "INSERT", "different_decisions"),
    ("N26", "Maybe switch to Rust for the parser.",
     "Consider using Go for the parser.", "INSERT", "uncertain"),
    ("N27", "Consider adding caching.",
     "Consider adding batching.", "INSERT", "uncertain"),
    ("N28", "Q1 report used 2025 data.",
     "Q2 report uses 2026 data.", "INSERT", "different_period"),
    ("N29", "The 2024 migration plan targeted MySQL.",
     "The 2026 migration plan targets Postgres.", "INSERT", "different_period"),
    ("N30", "Use Docker for local development.",
     "Use Docker for production deployment.", "INSERT", "different_goal"),
]

CONSERVATIVE = """You maintain session-level working facts. Decide whether the NEW record
supersedes the OLD one.

SUPERSEDE only when all three hold:
1. the subjects match (same person/file/module/host/service);
2. the user goal is materially the same, not merely the same topic or project;
3. the new trace continues, retries, extends, verifies, or finishes the old one.

Do NOT supersede when the records name different subjects, pursue different
goals in the same area, only share a technology or file mention, one supplies
context for the other, or the relationship is uncertain. INSERT is the safe
default; merging unrelated sessions destroys their separate task history.

Reply with only JSON: {"decision":"SUPERSEDE"} or {"decision":"INSERT"}."""

PERMISSIVE = """You maintain session-level working facts. Decide whether the NEW record
supersedes the OLD one. SUPERSEDE if the two records concern the same subject or
topic; otherwise INSERT.

Reply with only JSON: {"decision":"SUPERSEDE"} or {"decision":"INSERT"}."""


def ask(model: str, system: str, old: str, new: str) -> str:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"OLD: {old}\nNEW: {new}"},
        ],
        "stream": False,
        "options": {"temperature": 0, "num_predict": 16, "num_ctx": 1536},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.load(r)["message"]["content"]


def parse(reply: str) -> str:
    import re
    m = re.search(r'"decision"\s*:\s*"(SUPERSEDE|INSERT)"', reply, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    u = reply.upper()
    return "SUPERSEDE" if "SUPERSEDE" in u else "INSERT"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="qwen2.5:7b,llama3.1:8b,gemma3:4b")
    ap.add_argument("--out", default="results/conflict_pilot_50.json")
    args = ap.parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    rows = []
    for model in models:
        for label, system in (("conservative", CONSERVATIVE), ("permissive", PERMISSIVE)):
            for pid, old, new, expected, cat in PAIRS:
                reply = ask(model, system, old, new)
                got = parse(reply)
                rows.append({"model": model, "rule": label, "pair": pid,
                             "category": cat, "expected": expected, "got": got,
                             "correct": got == expected, "reply": reply.strip()[:80]})
                print(f"{model:14s} {label:12s} {pid} {cat:26s} "
                      f"exp={expected:9s} got={got:9s} "
                      f"{'OK' if got == expected else 'MISS'}", flush=True)
    summary = {}
    for model in models:
        for label in ("conservative", "permissive"):
            sel = [r for r in rows if r["model"] == model and r["rule"] == label]
            pos = [r for r in sel if r["expected"] == "SUPERSEDE"]
            neg = [r for r in sel if r["expected"] == "INSERT"]
            summary[f"{model}|{label}"] = {
                "n": len(sel),
                "true_supersede": f"{sum(r['got'] == 'SUPERSEDE' for r in pos)}/{len(pos)}",
                "false_supersede": f"{sum(r['got'] == 'SUPERSEDE' for r in neg)}/{len(neg)}",
                "accuracy": f"{sum(r['correct'] for r in sel)}/{len(sel)}",
            }
    out = {"models": models, "pairs": len(PAIRS), "rows": rows, "summary": summary}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
