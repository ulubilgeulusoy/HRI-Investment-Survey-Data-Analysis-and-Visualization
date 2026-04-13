from __future__ import annotations

from typing import Dict


def compute_psychometrics(respect: float, self_confidence: float, perception: float) -> Dict[str, float]:
    return {
        "respect_0_to_100": float(respect),
        "self_confidence_0_to_100": float(self_confidence),
        "perception_autonomy_0_to_100": float(perception),
    }
