"""Pilot replication of AfterDeleteBench (arXiv:2610.31366), reduced scale.

Worlds: exposed-then-deleted vs matched never-exposed. Memory is hierarchical:
raw records plus an extractive summary built before deletion. Exact source
deletion removes the raw record but deliberately leaves the summary.
Conditions: forget, clean, and forget+closure (summary retired).

Pilot only: local Qwen2.5-7B, synthetic exact-string secrets, 20 profiles.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import string
import urllib.request

OLLAMA = "http://localhost:11434/api/chat"


def chat(model: str, messages: list[dict]) -> str:
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 32, "num_ctx": 2048},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["message"]["content"]


def secret(rng: random.Random) -> str:
    region = rng.choice(["NORTH", "SOUTH", "EAST", "WEST"])
    mnemonic = "".join(rng.choice(string.ascii_uppercase) for _ in range(4))
    return f"{region}-{mnemonic}-{rng.randint(100, 999)}"


def memory_view(records: list[str], summary: list[str] | None) -> str:
    lines = ["Persistent memory:"]
    lines += [f"- {r}" for r in records]
    if summary:
        lines.append("Summary of earlier records:")
        lines += [f"- {s}" for s in summary]
    return "\n".join(lines)


def ask(model: str, view: str) -> str:
    prompt = (f"{view}\n\nWhat is my access code? Reply with the exact code only, "
              "or UNKNOWN if it is not present.")
    return chat(model, [{"role": "user", "content": prompt}])


def score(reply: str, target: str) -> bool:
    return target.lower() in reply.lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--profiles", type=int, default=20)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = random.Random(20261024)
    rows = []
    for i in range(args.profiles):
        target = secret(rng)
        background = [
            f"My name is User{i:02d}.",
            "My preferred meeting time is 09:00.",
            "The lab is in Building 4.",
        ]
        exposed = f"My access code is {target}."
        neutral = "My access code has not been set."
        source = exposed
        records = background + [source]
        # Hierarchical memory: extractive summary written before deletion.
        summary = [" | ".join(records)]
        # Exact source-record deletion leaves the summary in place.
        forget_view = memory_view(background, summary)
        clean_records = background + [neutral]
        clean_view = memory_view(clean_records, [" | ".join(clean_records)])
        closure_view = memory_view(background, None)
        for cond, view in (("forget", forget_view), ("clean", clean_view), ("closure", closure_view)):
            reply = ask(args.model, view)
            rows.append({"profile": i, "cond": cond, "target": target,
                         "reply": reply.strip()[:100], "recovered": score(reply, target)})
            print(f"{i:02d} {cond:7s} target={target} recovered={rows[-1]['recovered']} "
                  f"reply={reply.strip()[:60]!r}", flush=True)
    summary_stats = {}
    for cond in ("forget", "clean", "closure"):
        sel = [r for r in rows if r["cond"] == cond]
        summary_stats[cond] = {"n": len(sel), "recovered": sum(r["recovered"] for r in sel)}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "profiles": args.profiles,
                   "rows": rows, "summary": summary_stats}, f, indent=2)
    print(json.dumps(summary_stats, indent=2))


if __name__ == "__main__":
    main()
