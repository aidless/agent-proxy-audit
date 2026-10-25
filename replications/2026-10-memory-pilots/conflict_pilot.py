"""Pilot: conservative vs permissive supersede rules for session facts.

The conservative prompt is paraphrased from Hy-Memory's fact reconciler
(hy_memory/coding/fact_reconciler.py:214-237): supersede only when the subject
matches, the user goal is materially the same, and the new trace continues,
retries, extends, verifies or finishes the old one. The permissive prompt is a
strawman: supersede if the two records share a subject or topic.

20 synthetic pairs: 8 positives (a continuation that should supersede) and 12
negatives (parallel work, different goals, different subjects, uncertain).
The pilot measures the tradeoff; it does not validate Hy-Memory's model.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

OLLAMA = "http://localhost:11434/api/chat"

PAIRS = [
    # (old, new, expected)
    ("The CI fix in auth/session.py is in progress; retry the test job.",
     "The retry failed on the same test; add a fixture and rerun.", "SUPERSEDE"),
    ("Deploying billing-api v2 to staging; waiting on the migration.",
     "Migration finished; canary deploy to staging next.", "SUPERSEDE"),
    ("User prefers pytest for Python tests.",
     "User now prefers pytest with uv; keep the old preference superseded.", "SUPERSEDE"),
    ("Investigating a flaky test in orders_test.py; suspect the clock.",
     "Found the clock seed issue; fix it and verify the test.", "SUPERSEDE"),
    ("Refactor parse_config to remove globals; step 1 done.",
     "Step 2: move defaults into a dataclass.", "SUPERSEDE"),
    ("Rerunning experiment E7 after fixing the data split.",
     "E7 rerun finished with the same split; analysis pending.", "SUPERSEDE"),
    ("Drafting the related-work section for paper X.",
     "Revised the related-work section after a reviewer comment.", "SUPERSEDE"),
    ("Debugging OOM in the training job on A100.",
     "OOM traced to batch size; retry with gradient accumulation.", "SUPERSEDE"),

    ("Fixing CI in auth/session.py.",
     "Adding docstrings to auth/session.py.", "INSERT"),
    ("Refactor billing/models.py.",
     "Refactor billing/views.py.", "INSERT"),
    ("Alice prefers dark mode.",
     "Bob prefers dark mode.", "INSERT"),
    ("Use pytest in project A.",
     "Use pytest in project B.", "INSERT"),
    ("Use the retry helper from the CI fix.",
     "Write docs for the release process.", "INSERT"),
    ("OOM in job 42 due to batch size.",
     "OOM in job 77 due to a memory leak.", "INSERT"),
    ("Add a login page to repo X.",
     "Add a billing page to repo X.", "INSERT"),
    ("User prefers dark mode.",
     "User prefers tabs over spaces.", "INSERT"),
    ("Meeting decided to use Postgres.",
     "Meeting decided to delay the launch.", "INSERT"),
    ("Maybe switch to Rust for the parser.",
     "Consider using Go for the parser.", "INSERT"),
    ("Q1 report used 2025 data.",
     "Q2 report uses 2026 data.", "INSERT"),
    ("Use Docker for local development.",
     "Use Docker for production deployment.", "INSERT"),
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
        "options": {"temperature": 0, "num_predict": 24, "num_ctx": 2048},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["message"]["content"]


def parse(reply: str) -> str:
    u = reply.upper()
    return "SUPERSEDE" if "SUPERSEDE" in u else "INSERT"


def main() -> None:
    model = "qwen2.5:7b"
    rows = []
    for label, system in (("conservative", CONSERVATIVE), ("permissive", PERMISSIVE)):
        for i, (old, new, expected) in enumerate(PAIRS):
            reply = ask(model, system, old, new)
            got = parse(reply)
            rows.append({"rule": label, "pair": i, "expected": expected,
                         "got": got, "correct": got == expected, "reply": reply.strip()[:60]})
            print(f"{label:12s} {i:02d} exp={expected:9s} got={got:9s} "
                  f"{'OK' if got == expected else 'MISS'} {reply.strip()[:40]!r}", flush=True)
    summary = {}
    for label in ("conservative", "permissive"):
        sel = [r for r in rows if r["rule"] == label]
        pos = [r for r in sel if r["expected"] == "SUPERSEDE"]
        neg = [r for r in sel if r["expected"] == "INSERT"]
        summary[label] = {
            "n": len(sel),
            "true_supersede": f"{sum(r['got'] == 'SUPERSEDE' for r in pos)}/{len(pos)}",
            "false_supersede": f"{sum(r['got'] == 'SUPERSEDE' for r in neg)}/{len(neg)}",
            "accuracy": f"{sum(r['correct'] for r in sel)}/{len(sel)}",
        }
    out = {"model": model, "pairs": len(PAIRS), "rows": rows, "summary": summary}
    Path("results").mkdir(exist_ok=True)
    Path("results/conflict_pilot.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
