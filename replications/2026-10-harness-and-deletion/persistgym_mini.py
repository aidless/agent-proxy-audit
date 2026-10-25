"""Pilot replication of PersistGym-lite (arXiv:2610.26632), reduced scale.

Cells: observed/derived fact x recoverable/not, far distance only.
Harnesses: full history vs a truncated window. A fact that is dropped and
cannot be looked up should cost success; if it can be looked up, it should not.

This is a pilot, not the paper's 200-template sweep. It uses local Ollama
models and a much smaller context window. Report it as such.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import string
import urllib.request

OLLAMA = "http://localhost:11434/api/chat"


def chat(model: str, messages: list[dict], num_predict: int = 8) -> str:
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0, "num_predict": num_predict, "num_ctx": 2048},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["message"]["content"]


def visible(messages: list[dict], mode: str, window: int) -> list[dict]:
    """Full history, or the current request plus as much recent history as fits.

    The current request must always be sent; a window that drops it is not a
    context policy, it is a broken harness. The budget applies to history only.
    """
    if mode == "full":
        return messages
    head, current, history = messages[0], messages[-1], messages[1:-1]
    kept, budget = [], window
    for m in reversed(history):
        if len(m["content"]) > budget:
            break
        kept.append(m)
        budget -= len(m["content"])
    return [head] + list(reversed(kept)) + [current]


def make_code(rng: random.Random) -> str:
    return "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def options(rng: random.Random, code: str) -> tuple[list[str], str]:
    pool = {code}
    while len(pool) < 10:
        pool.add(make_code(rng))
    opts = sorted(pool)
    rng.shuffle(opts)
    correct = string.ascii_uppercase[opts.index(code)]
    return opts, correct


def episode(model: str, mode: str, cell: dict, rng: random.Random, window: int) -> dict:
    code = make_code(rng)
    opts, correct = options(rng, code)
    system = {"role": "system", "content": "You are an agent working through a session. Follow each instruction."}
    if cell["fact"] == "observed":
        reveal = f"Session fact: the access code for this session is {code}."
    else:
        part_a, part_b = code[:3], code[3:]
        reveal = (f"Session facts: part A is {part_a}; part B is {part_b}; "
                  f"the access code is part A followed by part B.")
    msgs = [system, {"role": "user", "content": reveal}]
    chat(model, msgs, 4)
    msgs.append({"role": "assistant", "content": "OK"})
    for i in range(4):
        msgs.append({"role": "user", "content": f"Routine step {i+1}: reply with only OK."})
        out = chat(model, visible(msgs, mode, window), 4)
        msgs.append({"role": "assistant", "content": out.strip()[:40]})
    listing = "\n".join(f"{string.ascii_uppercase[i]}) {o}" for i, o in enumerate(opts))
    affordance = (" If you cannot see the session fact, reply LOOKUP."
                  if cell["recoverable"] else "")
    need = (f"What is the access code?\n{listing}\n"
            f"Reply with only the option letter.{affordance}")
    msgs.append({"role": "user", "content": need})
    out = chat(model, visible(msgs, mode, window), 8).strip().upper()
    looked_up = "LOOKUP" in out
    if looked_up and cell["recoverable"]:
        msgs.append({"role": "assistant", "content": out[:40]})
        msgs.append({"role": "user", "content": (
            f"The access code is {code}.\n{listing}\n"
            "Reply with only the option letter.")})
        out = chat(model, visible(msgs, mode, window), 8).strip().upper()
    letters = re.findall(r"\b([A-J])\b", out)
    picked = letters[-1] if letters else ""
    return {
        "fact": cell["fact"], "recoverable": cell["recoverable"], "harness": mode,
        "code": code, "correct": correct, "reply": out[:80],
        "looked_up": looked_up, "success": picked == correct or code in out,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--templates", type=int, default=5)
    ap.add_argument("--window", type=int, default=180)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = random.Random(20261024)
    cells = [{"fact": f, "recoverable": r} for f in ("observed", "derived") for r in (False, True)]
    rows = []
    for t in range(args.templates):
        for cell in cells:
            for mode in ("full", "window"):
                row = episode(args.model, mode, cell, rng, args.window)
                row["template"] = t
                rows.append(row)
                print(f"{t} {cell['fact']:8s} rec={cell['recoverable']} {mode:6s} -> "
                      f"success={row['success']} lookup={row['looked_up']} reply={row['reply']!r}", flush=True)
    summary = {}
    for fact in ("observed", "derived"):
        for rec in (False, True):
            for mode in ("full", "window"):
                sel = [r for r in rows if r["fact"] == fact and r["recoverable"] == rec and r["harness"] == mode]
                summary[f"{fact}|rec={rec}|{mode}"] = {
                    "n": len(sel), "success": sum(r["success"] for r in sel),
                    "lookups": sum(r["looked_up"] for r in sel),
                }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "templates": args.templates, "window": args.window,
                   "rows": rows, "summary": summary}, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
