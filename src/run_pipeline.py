from __future__ import annotations

import argparse
from pathlib import Path

from pipeline import combine_and_export


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute experiment scores and export a combined CSV.")
    parser.add_argument("--break-csv", type=Path, required=True, help="Path to break-condition Qualtrics CSV")
    parser.add_argument("--baseline-csv", type=Path, default=None, help="Path to baseline-condition Qualtrics CSV")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/scores_combined.csv"),
        help="Output path for combined score CSV",
    )

    args = parser.parse_args()
    records = combine_and_export(args.break_csv, args.baseline_csv, args.out)
    print(f"Wrote {len(records)} records to {args.out}")


if __name__ == "__main__":
    main()
