from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from scoring.investment import compute_investment_score
from scoring.psychometrics import compute_psychometrics
from scoring.tlx import TLX_DIMENSIONS, compute_weighted_tlx
from scoring.trust import TRUST_ITEMS, compute_trust_score


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_CSV = REPO_ROOT / "outputs" / "scores_combined.csv"


# 1-based column mapping converted to 0-based indexes here.
@dataclass(frozen=True)
class BreakMapping:
    participant_id: int = 17
    phase: int = 18
    tlx_pairwise_start: int = 19
    tlx_pairwise_end: int = 33
    tlx_ratings_start: int = 34
    tlx_ratings_end: int = 39
    investment_start: int = 40
    investment_end: int = 45
    actions_performed: int = 46
    why_actions_selected: int = 47
    why_not_other_actions: int = 48
    additional_comments: int = 49
    respect: int = 50
    self_confidence: int = 51
    perception: int = 52
    trust_start: int = 53
    trust_end: int = 62
    finished: int = 6
    progress: int = 4


@dataclass(frozen=True)
class BaselineMapping:
    participant_id: int = 17
    respect: int = 18
    self_confidence: int = 19
    perception: int = 20
    trust_start: int = 21
    trust_end: int = 30
    finished: int = 6
    progress: int = 4


def _read_qualtrics_rows(csv_path: Path) -> Iterable[List[str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # export header
        next(reader, None)  # question text
        next(reader, None)  # import ids
        for row in reader:
            if any(cell.strip() for cell in row):
                yield row


def _safe_float(value: str) -> Optional[float]:
    value = value.strip()
    if value == "":
        return None
    return float(value)


def _keep_row(row: List[str], finished_idx: int, progress_idx: int) -> bool:
    finished = row[finished_idx].strip().lower() if finished_idx < len(row) else ""
    progress = row[progress_idx].strip() if progress_idx < len(row) else ""
    if finished in {"true", "1"}:
        return True
    try:
        return float(progress) >= 100
    except ValueError:
        return False


def load_break_rows(csv_path: Path, mapping: BreakMapping = BreakMapping()) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for row in _read_qualtrics_rows(csv_path):
        if not _keep_row(row, mapping.finished, mapping.progress):
            continue

        participant_id = row[mapping.participant_id].strip()
        phase = row[mapping.phase].strip()
        if not participant_id or not phase:
            continue

        tlx_choices = [row[i].strip() for i in range(mapping.tlx_pairwise_start, mapping.tlx_pairwise_end + 1)]
        tlx_values = [float(row[i].strip()) for i in range(mapping.tlx_ratings_start, mapping.tlx_ratings_end + 1)]
        tlx_ratings = {TLX_DIMENSIONS[i]: tlx_values[i] for i in range(6)}

        investment_values = [float(row[i].strip()) for i in range(mapping.investment_start, mapping.investment_end + 1)]

        trust_values = {
            TRUST_ITEMS[i]: row[mapping.trust_start + i].strip()
            for i in range(10)
        }

        psychometrics = compute_psychometrics(
            respect=float(row[mapping.respect].strip()),
            self_confidence=float(row[mapping.self_confidence].strip()),
            perception=float(row[mapping.perception].strip()),
        )

        record: Dict[str, object] = {
            "participant_id": participant_id,
            "phase": phase,
            "condition": "Break",
            "source_file": str(csv_path),
            "actions_performed": row[mapping.actions_performed].strip(),
            "why_actions_selected": row[mapping.why_actions_selected].strip(),
            "why_not_other_actions": row[mapping.why_not_other_actions].strip(),
            "additional_comments": row[mapping.additional_comments].strip(),
            **compute_weighted_tlx(tlx_choices, tlx_ratings),
            **compute_investment_score(investment_values),
            **compute_trust_score(trust_values),
            **psychometrics,
        }
        records.append(record)

    return records


def load_baseline_rows(
    csv_path: Path,
    phase_label: str = "Baseline",
    mapping: BaselineMapping = BaselineMapping(),
) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for row in _read_qualtrics_rows(csv_path):
        if not _keep_row(row, mapping.finished, mapping.progress):
            continue

        participant_id = row[mapping.participant_id].strip()
        if not participant_id:
            continue

        trust_values = {
            TRUST_ITEMS[i]: row[mapping.trust_start + i].strip()
            for i in range(10)
        }

        psychometrics = compute_psychometrics(
            respect=float(row[mapping.respect].strip()),
            self_confidence=float(row[mapping.self_confidence].strip()),
            perception=float(row[mapping.perception].strip()),
        )

        record: Dict[str, object] = {
            "participant_id": participant_id,
            "phase": phase_label,
            "condition": "Baseline",
            "source_file": str(csv_path),
            "actions_performed": None,
            "why_actions_selected": None,
            "why_not_other_actions": None,
            "additional_comments": None,
            "tlx_weighted_score": None,
            "investment_score_0_to_100": None,
            **compute_trust_score(trust_values),
            **psychometrics,
        }
        records.append(record)

    return records


def combine_and_export(
    break_csv_path: Path,
    baseline_csv_path: Optional[Path] = None,
    output_csv_path: Path = DEFAULT_OUTPUT_CSV,
) -> List[Dict[str, object]]:
    records = load_break_rows(break_csv_path)
    if baseline_csv_path is not None:
        records.extend(load_baseline_rows(baseline_csv_path))

    records.sort(key=lambda r: (str(r["participant_id"]), str(r["phase"])))

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({k for record in records for k in record.keys()})
    with output_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return records
