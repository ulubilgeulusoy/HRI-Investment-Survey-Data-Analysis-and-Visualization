from __future__ import annotations

from typing import Dict, Iterable


def compute_investment_score(values: Iterable[float]) -> Dict[str, float]:
    numeric = [float(v) for v in values]
    if len(numeric) != 6:
        raise ValueError(f"Expected 6 investment items, received {len(numeric)}")

    avg = sum(numeric) / 6.0
    out = {"investment_score_0_to_100": round(avg, 4)}
    for i, value in enumerate(numeric, start=1):
        out[f"investment_item_{i}"] = value
    return out
