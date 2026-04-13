from __future__ import annotations

from collections import Counter
from typing import Dict, List

TLX_DIMENSIONS = [
    "Mental Demand",
    "Physical Demand",
    "Temporal Demand",
    "Performance",
    "Effort",
    "Frustration",
]


def _normalize_dimension_name(name: str) -> str:
    normalized = name.strip().lower()
    aliases = {
        "mental demand": "Mental Demand",
        "physical demand": "Physical Demand",
        "temporal demand": "Temporal Demand",
        "performance": "Performance",
        "effort": "Effort",
        "frustration": "Frustration",
    }
    if normalized not in aliases:
        raise ValueError(f"Unsupported TLX dimension name in pairwise response: {name!r}")
    return aliases[normalized]


def compute_weighted_tlx(pairwise_choices: List[str], ratings: Dict[str, float]) -> Dict[str, float]:
    if len(pairwise_choices) != 15:
        raise ValueError(f"Expected 15 pairwise choices, received {len(pairwise_choices)}")

    missing = [d for d in TLX_DIMENSIONS if d not in ratings]
    if missing:
        raise ValueError(f"Missing TLX ratings for dimensions: {missing}")

    weights = Counter(_normalize_dimension_name(choice) for choice in pairwise_choices)

    weighted_sum = 0.0
    for dim in TLX_DIMENSIONS:
        weighted_sum += float(ratings[dim]) * float(weights.get(dim, 0))

    weighted_tlx = weighted_sum / 15.0

    out = {
        "tlx_weighted_score": round(weighted_tlx, 4),
        "tlx_weighted_sum": round(weighted_sum, 4),
    }
    for dim in TLX_DIMENSIONS:
        key = dim.lower().replace(" ", "_")
        out[f"tlx_{key}_rating"] = float(ratings[dim])
        out[f"tlx_{key}_weight"] = int(weights.get(dim, 0))

    return out
