from __future__ import annotations

from typing import Dict

LIKERT_MAP = {
    "strongly agree": 5,
    "agree": 4,
    "neutral": 3,
    "disagree": 2,
    "strongly disagree": 1,
    "somewhat disagree": 2,
    "neither agree nor disagree": 3,
    "somewhat agree": 4,
}

REVERSE_CODED = {"A", "C", "G"}
TRUST_ITEMS = list("ABCDEFGHIJ")
COMPONENT_X_ITEMS = ["A", "C"]  # Perceived robot motion and pick-up speed
COMPONENT_Y_ITEMS = ["D", "F", "H", "I"]  # Perceived safe co-operation
COMPONENT_Z_ITEMS = ["B", "E", "G", "J"]  # Perceived robot and gripper reliability


def _map_likert(value: str) -> int:
    key = value.strip().lower()
    if key not in LIKERT_MAP:
        raise ValueError(f"Unsupported Likert response: {value!r}")
    return LIKERT_MAP[key]


def compute_trust_score(item_values: Dict[str, str]) -> Dict[str, float]:
    missing = [k for k in TRUST_ITEMS if k not in item_values]
    if missing:
        raise ValueError(f"Missing trust items: {missing}")

    scored = {}
    for item in TRUST_ITEMS:
        raw_numeric = _map_likert(item_values[item])
        if item in REVERSE_CODED:
            raw_numeric = 6 - raw_numeric
        scored[item] = raw_numeric

    component_x = sum(scored[i] for i in COMPONENT_X_ITEMS)
    component_y = sum(scored[i] for i in COMPONENT_Y_ITEMS)
    component_z = sum(scored[i] for i in COMPONENT_Z_ITEMS)
    total_10_to_50 = component_x + component_y + component_z

    mean_1_to_5 = total_10_to_50 / len(TRUST_ITEMS)
    score_0_to_100 = ((mean_1_to_5 - 1) / 4) * 100

    if total_10_to_50 < 25:
        interpretation = "Low trust: participant may not trust the robot to collaborate."
    elif total_10_to_50 >= 45:
        interpretation = "Very high trust: monitor for potential over-reliance/complacency."
    else:
        interpretation = "Moderate trust: review component scores for specific weak areas."

    out: Dict[str, float] = {
        "trust_component_x_motion_pickup_2_to_10": component_x,
        "trust_component_y_safe_cooperation_4_to_20": component_y,
        "trust_component_z_reliability_4_to_20": component_z,
        "trust_total_10_to_50": total_10_to_50,
        "trust_mean_1_to_5": round(mean_1_to_5, 4),
        "trust_score_0_to_100": round(score_0_to_100, 4),
        "trust_interpretation": interpretation,
    }
    for item in TRUST_ITEMS:
        out[f"trust_item_{item}"] = scored[item]
    return out
