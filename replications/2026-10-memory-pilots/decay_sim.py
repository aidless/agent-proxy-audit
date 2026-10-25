"""Deterministic simulation of ai-memory's retention formula.

Formula (crates/ai-memory-store/src/decay.rs:196-202):

    score = salience * exp(-lambda * age_days)
          + sigma * ln(1 + access_count) * exp(-mu * days_since_access) * breadth

Defaults: lambda=0.02 (~35-day half-life), sigma=0.6, mu=0.04,
salience=1.0, cold_threshold=0.20 (decay.rs:92-103).

The simulation answers two questions without an LLM:
1. How many days until a page crosses the cold threshold under pure-age vs
   access-weighted retention?
2. Does one old access keep a page alive longer than a newer unused page?
"""
from __future__ import annotations

import json
import math
from pathlib import Path

SALIENCE = 1.0
SIGMA = 0.6
MU = 0.04
THRESHOLD = 0.20


def score(age: float, access_count: int, days_since_access: float | None,
          lam: float, sigma: float = SIGMA, mu: float = MU) -> float:
    time_term = SALIENCE * math.exp(-lam * age)
    access_term = 0.0
    if days_since_access is not None:
        access_term = sigma * math.log1p(access_count) * math.exp(-mu * days_since_access)
    return time_term + access_term


def days_until_cold(access_count: int, access_day: float | None,
                    lam: float, sigma: float = SIGMA, mu: float = MU,
                    cap: int = 3650) -> int | None:
    """First integer day (age since update) at which score < threshold.

    A page updated at t=0 and last accessed at `access_day` has
    days_since_access = max(0, age - access_day); after that access it is not
    touched again. `None` means never accessed.
    """
    for d in range(0, cap + 1):
        dsa = None if access_day is None else max(0.0, float(d) - access_day)
        if score(float(d), access_count, dsa, lam, sigma, mu) < THRESHOLD:
            return d
    return None


def main() -> None:
    lam_default = 0.02          # ~35-day half-life
    lam_180 = math.log(2) / 180  # episodic 180-day half-life (design-decisions.md:140)
    rows = []
    for label, lam in (("default_35d", lam_default), ("episodic_180d", lam_180)):
        for ac, access_day in ((0, None), (1, 0.0), (5, 0.0), (20, 0.0), (5, 60.0)):
            rows.append({
                "lambda": label,
                "lambda_value": round(lam, 6),
                "access_count": ac,
                "last_access_day": access_day,
                "retention_days": days_until_cold(ac, access_day, lam),
            })
    # Pure age (sigma=0) vs access-weighted, for a page accessed 5x at day 60.
    pure = days_until_cold(5, 60.0, lam_default, sigma=0.0)
    weighted = days_until_cold(5, 60.0, lam_default, sigma=SIGMA)
    ratio = (weighted / pure) if pure and weighted else None

    # Concrete comparison: old-but-used vs new-but-unused at age 120 and 10.
    comparison = {
        "old_but_used_120d_3access_30d_ago": round(score(120, 3, 30, lam_default), 4),
        "new_but_unused_10d": round(score(10, 0, None, lam_default), 4),
        "old_and_unused_180d": round(score(180, 0, None, lam_default), 4),
    }
    out = {
        "formula": "salience*exp(-lambda*age)+sigma*ln(1+access)*exp(-mu*days_since_access)",
        "parameters": {"salience": SALIENCE, "sigma": SIGMA, "mu": MU,
                       "threshold": THRESHOLD},
        "threshold_days": rows,
        "pure_age_vs_access_weighted": {
            "pure_age_days": pure,
            "access_weighted_days": weighted,
            "ratio": round(ratio, 2) if ratio else None,
            "note": "page with 5 accesses, last access 60 days before update",
        },
        "comparison_at_fixed_age": comparison,
    }
    Path("results").mkdir(exist_ok=True)
    Path("results/decay_sim.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
