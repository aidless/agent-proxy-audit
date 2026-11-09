#!/usr/bin/env python3
"""Offline check for this index repository.

Standard library only. No network and no model calls.

What it does:
- compile every Python file
- parse every JSON file
- recount committed pilot rows and require their summary blocks to match
- recompute decay_sim.build_report and require it to match the committed JSON
- require every headline cell to match that local evidence, or to name a
  sister repo, commit, path, and locator without claiming a re-run
- require the README problem statement to be at most three lines, the status
  line to stay WORK-IN-PROGRESS, and the quoted-cell block to match the ledger

Sibling numbers are not fetched. A dated commit pin is not a live binding.
See FAILURE_MODES.md.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
LEDGER_PATH = ROOT / "quotes" / "headline_quotes.json"
README_PATH = ROOT / "README.md"
PROBLEM_BEGIN = "<!-- BEGIN PROBLEM -->"
PROBLEM_END = "<!-- END PROBLEM -->"
QUOTES_BEGIN = "<!-- BEGIN QUOTED CELLS -->"
QUOTES_END = "<!-- END QUOTED CELLS -->"


def fail(messages: list[str]) -> None:
    for message in messages:
        print(message, file=sys.stderr)
    sys.exit(1)


def compile_python() -> None:
    bad: list[str] = []
    n = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            path = Path(dirpath) / filename
            n += 1
            try:
                source = path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError as exc:
                bad.append(f"{path}: {exc}")
                continue
            try:
                compile(source, str(path), "exec")
            except SyntaxError as exc:
                bad.append(f"{path}: {exc.msg} (line {exc.lineno})")
    print(f"compiled {n} python files")
    if bad:
        fail(bad)


def parse_json_files() -> None:
    bad: list[str] = []
    n = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            if not filename.endswith(".json"):
                continue
            path = Path(dirpath) / filename
            if path.stat().st_size > 50 * 1024 * 1024:
                continue
            n += 1
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError, OSError) as exc:
                bad.append(f"{path}: {exc}")
    print(f"parsed {n} json files")
    if bad:
        fail(bad)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_decay():
    path = ROOT / "replications" / "2026-10-memory-pilots" / "decay_sim.py"
    spec = importlib.util.spec_from_file_location("decay_sim_index", path)
    if spec is None or spec.loader is None:
        fail([f"could not load {path}"])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reconcile_persistgym(doc: dict) -> None:
    summary = {}
    for fact in ("observed", "derived"):
        for recoverable in (False, True):
            for mode in ("full", "window"):
                selected = [
                    row for row in doc["rows"]
                    if row["fact"] == fact
                    and row["recoverable"] is recoverable
                    and row["harness"] == mode
                ]
                summary[f"{fact}|rec={recoverable}|{mode}"] = {
                    "n": len(selected),
                    "success": sum(bool(row["success"]) for row in selected),
                    "lookups": sum(bool(row["looked_up"]) for row in selected),
                }
    if summary != doc["summary"]:
        fail(["persistgym summary does not match rows"])


def reconcile_afterdelete(doc: dict) -> None:
    summary = {}
    for cond in ("forget", "clean", "closure"):
        selected = [row for row in doc["rows"] if row["cond"] == cond]
        summary[cond] = {
            "n": len(selected),
            "recovered": sum(bool(row["recovered"]) for row in selected),
        }
    if summary != doc["summary"]:
        fail(["afterdelete_qwen25_20p summary does not match rows"])


def reconcile_conflict(doc: dict, scaled: bool) -> None:
    summary = {}
    if scaled:
        groups = [(model, rule) for model in doc["models"] for rule in ("conservative", "permissive")]
    else:
        groups = [(None, rule) for rule in ("conservative", "permissive")]
    for model, rule in groups:
        selected = [
            row for row in doc["rows"]
            if row["rule"] == rule and (model is None or row["model"] == model)
        ]
        positives = [row for row in selected if row["expected"] == "SUPERSEDE"]
        negatives = [row for row in selected if row["expected"] == "INSERT"]
        key = rule if model is None else f"{model}|{rule}"
        summary[key] = {
            "n": len(selected),
            "true_supersede": (
                f"{sum(row['got'] == 'SUPERSEDE' for row in positives)}/{len(positives)}"
            ),
            "false_supersede": (
                f"{sum(row['got'] == 'SUPERSEDE' for row in negatives)}/{len(negatives)}"
            ),
            "accuracy": f"{sum(bool(row['correct']) for row in selected)}/{len(selected)}",
        }
    if summary != doc["summary"]:
        fail([f"conflict summary does not match rows ({'scaled' if scaled else 'pilot'})"])


def reconcile_hierarchical(doc: dict) -> None:
    summary = {}
    for variant in ("extractive", "model_written"):
        for cond in ("forget", "clean", "closure"):
            selected = [
                row for row in doc["rows"]
                if row["variant"] == variant and row["cond"] == cond
            ]
            if not selected:
                continue
            summary[f"{variant}|{cond}"] = {
                "n": len(selected),
                "recovered": sum(bool(row["recovered"]) for row in selected),
                "summary_has_target": sum(bool(row.get("summary_has_target", False)) for row in selected),
            }
    if summary != doc["summary"]:
        fail(["hierarchical deletion summary does not match rows"])


def reconcile_pilot_summaries() -> None:
    base = ROOT / "replications"
    reconcile_persistgym(load_json(
        base / "2026-10-harness-and-deletion" / "results" / "persistgym_qwen25_3t.json"
    ))
    reconcile_afterdelete(load_json(
        base / "2026-10-harness-and-deletion" / "results" / "afterdelete_qwen25_20p.json"
    ))
    reconcile_conflict(load_json(
        base / "2026-10-memory-pilots" / "results" / "conflict_pilot.json"
    ), scaled=False)
    reconcile_conflict(load_json(
        base / "2026-10-memory-pilots" / "results" / "conflict_pilot_50.json"
    ), scaled=True)
    reconcile_hierarchical(load_json(
        base / "2026-10-memory-pilots" / "results" / "afterdelete_hierarchical.json"
    ))
    reconcile_hierarchical(load_json(
        base / "2026-10-memory-pilots" / "results" / "afterdelete_hierarchical_50.json"
    ))
    print("pilot summaries match recounted rows")


def recompute_decay(decay_module) -> dict:
    report = decay_module.build_report()
    committed = load_json(
        ROOT / "replications" / "2026-10-memory-pilots" / "results" / "decay_sim.json"
    )
    if report != committed:
        fail(["decay_sim.build_report() does not match results/decay_sim.json"])
    print("decay report matches committed json")
    return report


def fraction(rows: list[dict], count_field: str) -> str:
    return f"{sum(bool(row[count_field]) for row in rows)}/{len(rows)}"


def pilot_value(cell: dict) -> str:
    doc = load_json(ROOT / cell["path"])
    aggregate = cell["aggregate"]
    if aggregate.get("type") == "conflict":
        selected = [
            row for row in doc["rows"]
            if row["rule"] == aggregate["rule"] and row["expected"] == aggregate["expected"]
        ]
        if aggregate["count"] == "got_supersede":
            hits = [row for row in selected if row["got"] == "SUPERSEDE"]
        elif aggregate["count"] == "not_got":
            hits = [row for row in selected if row["got"] != "SUPERSEDE"]
        else:
            fail([f"{cell['id']}: unknown conflict count {aggregate['count']}"])
        if "expect_rows" in aggregate:
            found = [
                {"model": row["model"], "pair": row["pair"], "category": row["category"]}
                for row in hits
            ]
            if found != aggregate["expect_rows"]:
                fail([
                    f"{cell['id']}: false-merge rows are {found}, "
                    f"ledger expects {aggregate['expect_rows']}"
                ])
        return f"{len(hits)}/{len(selected)}"
    selected = [
        row for row in doc["rows"]
        if all(row.get(key) == value for key, value in aggregate["match"].items())
    ]
    if not selected:
        fail([f"{cell['id']}: no rows matched {aggregate['match']}"])
    return fraction(selected, aggregate["count_field"])


def decay_value(cell: dict, report: dict) -> str:
    aggregate = cell["aggregate"]
    kind = aggregate["type"]
    if kind == "retention":
        matches = [
            row for row in report["threshold_days"]
            if row["lambda"] == aggregate["lambda"]
            and row["access_count"] == aggregate["access_count"]
            and row["last_access_day"] == aggregate["last_access_day"]
        ]
        if len(matches) != 1:
            fail([f"{cell['id']}: expected one decay row, found {len(matches)}"])
        return str(matches[0]["retention_days"])
    if kind == "retention_all":
        days = {
            row["retention_days"]
            for row in report["threshold_days"]
            if row["lambda"] == aggregate["lambda"]
        }
        if len(days) != 1:
            fail([f"{cell['id']}: retention days differ across patterns: {sorted(days)}"])
        return str(next(iter(days)))
    if kind == "ratio":
        return str(report["pure_age_vs_access_weighted"]["ratio"])
    fail([f"{cell['id']}: unknown decay aggregate {kind}"])
    return ""


def check_sibling(cell: dict, ledger: dict) -> None:
    sister = ledger["sisters"].get(cell.get("sister"))
    missing = [
        field for field in ("sister", "path", "locator", "statement", "value")
        if not cell.get(field)
    ]
    if sister is None:
        missing.append("known sister")
    if missing:
        fail([f"{cell['id']}: sibling quote missing {missing}"])
    commit = sister["commit"]
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        fail([f"{cell['id']}: sister commit is not a 40-char sha: {commit}"])
    if cell.get("rerun_here") not in (None, False):
        fail([f"{cell['id']}: a sibling quote cannot set rerun_here"])
    factors = cell.get("factors")
    if factors is not None:
        product = 1
        for factor in factors:
            product *= factor
        if str(product) != cell["value"]:
            fail([f"{cell['id']}: factors {factors} multiply to {product}, value is {cell['value']}"])


def source_text(cell: dict, ledger: dict) -> str:
    if cell["kind"] == "sibling_quote":
        sister = ledger["sisters"][cell["sister"]]
        return (
            f"sibling quote observed {ledger['observed_on']}; "
            f"{sister['repo']}@{sister['commit']} {cell['path']} — {cell['locator']}; "
            "not recomputed in this clone"
        )
    if cell["kind"] == "pilot_rows":
        return f"pilot rows recounted from committed JSON; {cell['path']}"
    if cell["kind"] == "offline_recompute":
        return f"recomputed by decay_sim.build_report each check; {cell['path']}"
    return cell["kind"]


def render_quoted_cells(ledger: dict) -> str:
    lines = [
        "| Cell | Value | What it is | Source |",
        "|---|---|---|---|",
    ]
    for cell in ledger["cells"]:
        statement = " ".join(cell["statement"].split())
        source = " ".join(source_text(cell, ledger).split())
        if "|" in statement or "|" in source or "|" in cell["value"]:
            fail([f"{cell['id']}: table cell contains a pipe"])
        lines.append(f"| {cell['id']} | {cell['value']} | {statement} | {source} |")
    return "\n".join(lines)


def between(text: str, begin: str, end: str) -> str:
    if begin not in text or end not in text:
        fail([f"README is missing markers {begin} ... {end}"])
    start = text.index(begin) + len(begin)
    stop = text.index(end, start)
    return text[start:stop].strip("\n")


def check_readme(ledger: dict) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    problem = between(text, PROBLEM_BEGIN, PROBLEM_END)
    problem_lines = [line for line in problem.splitlines() if line.strip()]
    if len(problem_lines) > 3:
        fail([f"problem statement is {len(problem_lines)} lines; the maximum is 3"])
    if "catalog" not in problem.lower():
        fail(["problem statement does not say this repository is a catalog"])
    if "STATUS: WORK-IN-PROGRESS" not in text:
        fail(["README status line must stay STATUS: WORK-IN-PROGRESS"])
    if "FAILURE_MODES.md" not in text:
        fail(["README must link FAILURE_MODES.md"])
    if "parallel pairs" in text.lower():
        fail([
            "README still calls the conservative 1/90 cell parallel pairs; "
            "the recounted row is category different_decisions"
        ])
    quoted = between(text, QUOTES_BEGIN, QUOTES_END).strip()
    expected = render_quoted_cells(ledger).strip()
    if quoted != expected:
        fail([
            "README quoted-cell block does not match quotes/headline_quotes.json.",
            "Expected block:",
            expected,
        ])
    print(f"readme problem lines: {len(problem_lines)}; quoted cells match")


def check_failure_modes() -> None:
    path = ROOT / "FAILURE_MODES.md"
    if not path.is_file():
        fail(["FAILURE_MODES.md is missing"])
    text = path.read_text(encoding="utf-8").lower()
    for needle in ("stale", "pilot", "sister", "false zero", "not a safety"):
        if needle not in text:
            fail([f"FAILURE_MODES.md is missing a required topic: {needle}"])
    print("failure modes file present")


def check_cells(ledger: dict, decay_report: dict) -> None:
    seen: set[str] = set()
    for cell in ledger["cells"]:
        if cell["id"] in seen:
            fail([f"duplicate cell id {cell['id']}"])
        seen.add(cell["id"])
        kind = cell["kind"]
        if kind == "sibling_quote":
            check_sibling(cell, ledger)
            print(f"pinned {cell['id']}={cell['value']} (sibling quote, not recomputed)")
            continue
        if kind == "pilot_rows":
            actual = pilot_value(cell)
        elif kind == "offline_recompute":
            actual = decay_value(cell, decay_report)
        elif kind == "unknown":
            if cell["value"] != "UNKNOWN":
                fail([f"{cell['id']}: unknown cells must use value UNKNOWN"])
            print(f"unknown {cell['id']}")
            continue
        else:
            fail([f"{cell['id']}: unknown kind {kind}"])
        if actual != cell["value"]:
            fail([f"{cell['id']}: ledger says {cell['value']}, evidence says {actual}"])
        print(f"matched {cell['id']}={actual}")


def main() -> None:
    os.chdir(ROOT)
    compile_python()
    parse_json_files()
    ledger = load_json(LEDGER_PATH)
    if ledger.get("status") != "WORK-IN-PROGRESS":
        fail(["headline ledger status must stay WORK-IN-PROGRESS while this repo is an index"])
    if ledger.get("role") != "index-satellite":
        fail(["headline ledger role must stay index-satellite"])
    reconcile_pilot_summaries()
    decay_report = recompute_decay(load_decay())
    check_cells(ledger, decay_report)
    check_readme(ledger)
    check_failure_modes()
    print("offline index check passed")


if __name__ == "__main__":
    main()
