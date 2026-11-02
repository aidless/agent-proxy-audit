#!/usr/bin/env python3
"""基准：重新聚合已提交的 pilot 结果，验证"离线可复算"声明并测量成本。

agent-proxy-audit 的 README 声明所有描述性表格**离线可复算**（Python 3.11+，
无需模型或网络）。本基准测量一个真实可复现的属性：把仓库里**已提交**的
pilot 结果 JSON 全部加载、逐条重新聚合出 summary 表，耗时多少、是否与已提交
的 summary 一致。

这不是性能优化型基准——本仓是审计/复现仓库，吞吐不是目标。它回答：
**已提交的 pilot 结果是否真的可以离线重新聚合，且重新聚合与已提交 summary
逐字段一致**（防"结果文件与 README 声称的表格不同步"的静默漂移），以及
重聚合的成本是否低到可作为每次验证的门禁。

用法：
    python3 replications/bench_reaggregate.py [--json]
    # --json: 输出 JSON（默认打印可读行）

退出码：0 = 全部重新聚合一致；1 = 任一结果与已提交 summary 不一致（fail-closed）。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent


def reaggregate(path: pathlib.Path) -> dict:
    """对单个已提交结果文件重新聚合，返回 (verdict, summary, n_rows)。

    只做**确定性重聚合**：从 rows 重新数出 summary 的各个计数，不调用模型、
    不联网、不依赖被测量对象的内部实现。每个结果文件按**它自己的 schema**
    重聚合（结果文件来自不同的 pilot，字段名/分组键不同），不假设统一格式。
    若结果文件本身没有 rows（如 decay_sim.json 只有 threshold_days），则视为
    无可重聚合内容。
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if "rows" not in data or "summary" not in data:
        return {"verdict": "no_rows", "summary": None, "n_rows": 0}
    rows = data["rows"]
    if not rows:
        return {"verdict": "no_rows", "summary": None, "n_rows": 0}

    r0 = rows[0]
    summary = {}
    # ---- conflict 类：rule 分组（或 model|rule 分组），expected/got/correct 字段 ----
    if "expected" in r0 and "got" in r0 and "correct" in r0:
        if "model" in r0:
            # 50-pair 版本：每行带 model，summary 键为 "model|rule"
            groups: dict[str, list] = {}
            for r in rows:
                key = f"{r.get('model')}|{r.get('rule', '?')}"
                groups.setdefault(key, []).append(r)
            for key, sel in sorted(groups.items()):
                pos = [r for r in sel if r.get("expected") == "SUPERSEDE"]
                neg = [r for r in sel if r.get("expected") == "INSERT"]
                summary[key] = {
                    "n": len(sel),
                    "true_supersede": f"{sum(1 for r in pos if r.get('got') == 'SUPERSEDE')}/{len(pos)}",
                    "false_supersede": f"{sum(1 for r in neg if r.get('got') == 'SUPERSEDE')}/{len(neg)}",
                    "accuracy": f"{sum(1 for r in sel if r.get('correct'))}/{len(sel)}",
                }
            return {"verdict": "rows", "summary": summary, "n_rows": len(rows)}
        groups = {}
        for r in rows:
            groups.setdefault(r.get("rule", "?"), []).append(r)
        for rule, sel in sorted(groups.items()):
            pos = [r for r in sel if r.get("expected") == "SUPERSEDE"]
            neg = [r for r in sel if r.get("expected") == "INSERT"]
            summary[rule] = {
                "n": len(sel),
                "true_supersede": f"{sum(1 for r in pos if r.get('got') == 'SUPERSEDE')}/{len(pos)}",
                "false_supersede": f"{sum(1 for r in neg if r.get('got') == 'SUPERSEDE')}/{len(neg)}",
                "accuracy": f"{sum(1 for r in sel if r.get('correct'))}/{len(sel)}",
            }
        return {"verdict": "rows", "summary": summary, "n_rows": len(rows)}

    # ---- afterdelete 类：cond/variant 分组，recovered 字段 ----
    if "recovered" in r0 and ("cond" in r0 or "variant" in r0):
        groups = {}
        for r in rows:
            key = r.get("variant", r.get("cond", "?")) if r.get("variant") else r.get("cond", "?")
            # 有 variant 时键为 "variant|cond"，否则为 "cond"
            if r.get("variant"):
                key = f"{r['variant']}|{r.get('cond', '?')}"
            else:
                key = r.get("cond", "?")
            groups.setdefault(key, []).append(r)
        for key, sel in sorted(groups.items()):
            entry = {"n": len(sel),
                     "recovered": sum(1 for r in sel if r.get("recovered"))}
            if "summary_has_target" in r0:
                entry["summary_has_target"] = sum(1 for r in sel if r.get("summary_has_target"))
            summary[key] = entry
        return {"verdict": "rows", "summary": summary, "n_rows": len(rows)}

    # ---- persistgym 类：fact|rec|harness 分组，success/looked_up ----
    if "success" in r0 and "looked_up" in r0 and "fact" in r0:
        groups = {}
        for r in rows:
            key = f"{r.get('fact')}|rec={r.get('recoverable')}|{r.get('harness')}"
            groups.setdefault(key, []).append(r)
        for key, sel in sorted(groups.items()):
            summary[key] = {
                "n": len(sel),
                "success": sum(1 for r in sel if r.get("success")),
                "lookups": sum(1 for r in sel if r.get("looked_up")),
            }
        return {"verdict": "rows", "summary": summary, "n_rows": len(rows)}

    # ---- 未知 schema：不硬判，标记为无法重聚合（诚实，不猜测）----
    return {"verdict": "unknown_schema", "summary": None, "n_rows": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    result_files = sorted(
        p for p in (ROOT / "replications").rglob("results/*.json")
    )
    if not result_files:
        print("FAIL: 未找到 results/*.json", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    checks = []
    all_ok = True
    for path in result_files:
        rel = path.relative_to(ROOT).as_posix()
        t_start = time.perf_counter()
        agg = reaggregate(path)
        t_elapsed = time.perf_counter() - t_start
        if agg["verdict"] == "no_rows":
            checks.append({"file": rel, "verdict": "no_rows",
                           "elapsed_ms": round(t_elapsed * 1000, 3),
                           "consistent": None})
            continue
        committed = json.loads(path.read_text(encoding="utf-8")).get("summary")
        consistent = committed == agg["summary"]
        if not consistent:
            all_ok = False
        checks.append({
            "file": rel,
            "verdict": "rows",
            "n_rows": agg["n_rows"],
            "elapsed_ms": round(t_elapsed * 1000, 3),
            "consistent": consistent,
        })
    t1 = time.perf_counter()
    elapsed = t1 - t0

    n_files = len(result_files)
    n_rows = sum(c.get("n_rows", 0) for c in checks)
    n_no_rows = sum(1 for c in checks if c["verdict"] == "no_rows")
    n_inconsistent = sum(1 for c in checks if c.get("consistent") is False)

    if args.json:
        print(json.dumps({
            "n_files": n_files,
            "n_rows": n_rows,
            "n_no_rows": n_no_rows,
            "n_inconsistent": n_inconsistent,
            "elapsed_seconds": round(elapsed, 6),
            "checks": checks,
        }, ensure_ascii=False, indent=1))
    else:
        print(f"结果文件 {n_files} 个，共 {n_rows} 行，耗时 {elapsed:.4f}s")
        for c in checks:
            flag = "一致" if c.get("consistent") else ("无行" if c["verdict"] == "no_rows" else "不一致")
            print(f"  {c['file']:<58} {c.get('n_rows', '-'):>5} 行  {c['elapsed_ms']:>8.3f}ms  {flag}")
        print(f"重新聚合与已提交 summary 不一致的文件：{n_inconsistent}")
        if n_inconsistent:
            for c in checks:
                if c.get("consistent") is False:
                    print(f"  ✗ {c['file']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
