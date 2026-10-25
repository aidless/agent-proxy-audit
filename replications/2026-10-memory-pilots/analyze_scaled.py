"""Summarize the scaled conflict and deletion pilots."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def conflict(path: str) -> None:
    d = json.loads(Path(path).read_text())
    print(f"== conflict: {d['pairs']} pairs x {len(d['models'])} models ==")
    for key, s in d["summary"].items():
        print(f"{key:34s} true={s['true_supersede']:6s} false={s['false_supersede']:6s} acc={s['accuracy']}")
    print("\n-- errors by category --")
    for model in d["models"]:
        for rule in ("conservative", "permissive"):
            errs = [r for r in d["rows"] if r["model"] == model and r["rule"] == rule and not r["correct"]]
            if not errs:
                continue
            by = defaultdict(list)
            for r in errs:
                by[r["category"]].append(r["pair"])
            print(f"{model} / {rule}: {len(errs)} errors")
            for cat, ids in sorted(by.items()):
                print(f"   {cat:28s} {','.join(ids)}")


def deletion(path: str) -> None:
    d = json.loads(Path(path).read_text())
    print(f"\n== deletion: {d['profiles']} profiles, model={d['model']} ==")
    for key, s in d["summary"].items():
        print(f"{key:30s} recovered={s['recovered']}/{s['n']}  target_in_summary={s['summary_has_target']}/{s['n']}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        if "conflict" in p:
            conflict(p)
        elif "afterdelete" in p:
            deletion(p)
