"""Freeze the synthetic datasets used by the memory pilots.

Run from this directory. Writes:
  data/conflict_pairs_50.json      20 positives + 30 negatives
  data/deletion_profiles_50.json   50 deterministic profiles (seed 20261024)

The deletion profiles are regenerated with the same generator and seed as the
experiment; the targets are checked against the recorded results before writing.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import afterdelete_hierarchical as ad
import conflict_pilot_50 as cp

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

conflict = {
    "name": "memory-conflict-pairs",
    "version": 1,
    "license": "CC BY 4.0",
    "description": "Synthetic fact pairs for supersede-vs-insert judging: 20 continuations, 30 negatives.",
    "pairs": [
        {"id": pid, "old": old, "new": new, "expected": expected, "category": cat}
        for pid, old, new, expected, cat in cp.PAIRS
    ],
}
(OUT / "conflict_pairs_50.json").write_text(json.dumps(conflict, indent=2), encoding="utf-8")

rng = random.Random(20261024)
profiles = []
for i in range(50):
    target, background, distractors = ad.build_profile(rng, i)
    profiles.append({
        "id": f"P{i:02d}",
        "target": target,
        "background": background,
        "distractors": distractors,
        "exposed_record": f"My access code is {target}.",
        "neutral_record": "My access code has not been set.",
    })

# Check the frozen profiles against the recorded targets.
result_file = ROOT / "results" / "afterdelete_hierarchical_50.json"
if result_file.exists():
    rows = json.loads(result_file.read_text(encoding="utf-8"))["rows"]
    recorded = {r["profile"]: r["target"] for r in rows if r["variant"] == "extractive" and r["cond"] == "forget"}
    mismatches = [p["id"] for i, p in enumerate(profiles) if recorded.get(i) != p["target"]]
    if mismatches:
        raise SystemExit(f"profile/target mismatch vs recorded results: {mismatches}")
    print(f"targets match recorded results for {len(profiles)} profiles")

deletion = {
    "name": "memory-deletion-profiles",
    "version": 1,
    "license": "CC BY 4.0",
    "seed": 20261024,
    "description": "Synthetic persistent-memory profiles with a target secret, background records and distractors.",
    "query_template": "What is my access code? Reply with the exact code only, or UNKNOWN if it is not present.",
    "profiles": profiles,
}
(OUT / "deletion_profiles_50.json").write_text(json.dumps(deletion, indent=2), encoding="utf-8")
print("wrote", OUT / "conflict_pairs_50.json", OUT / "deletion_profiles_50.json")
