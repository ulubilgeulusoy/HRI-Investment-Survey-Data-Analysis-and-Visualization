# HRI Investment Experiment Data Analysis Pipeline (NOT VALIDATED)

This repo computes scores from Qualtrics exports and provides a GUI for inspection by participant and phase.

## Implemented Scales
- NASA TLX (weighted TLX from 15 pairwise comparisons + 6 ratings)
- Trust scale (A-J items, reverse coding for A/C/G, component and total scoring)
- Investment scale (6 items, averaged, 0-100)
- Respect / Self-confidence / Perception (already 0-100)

## Files
- `src/scoring/tlx.py`: weighted TLX scoring
- `src/scoring/trust.py`: trust scoring and reverse coding
- `src/scoring/investment.py`: investment averaging
- `src/scoring/psychometrics.py`: direct psychometric exports
- `src/pipeline.py`: CSV loaders, mapping, combined export
- `src/gui.py`: Tkinter GUI to inspect/filter/export scores
- `run_gui.py`: single launcher for GUI use
- `COLUMN_MAPPING.md`: source column mapping (1-based)

## Run GUI
```powershell
python run_gui.py
```

In GUI:
1. Load Break CSV.
2. Optionally load Baseline CSV.
3. Click `Compute Scores` to generate combined results CSV automatically.
4. Filter by participant/phase.
5. Select survey view (`Overview`, `Trust`, `NASA TLX`, `Investment`, `Self/Perception/Respect`) for detailed inspection.
6. Optionally export filtered rows.

## Notes
- The parser skips the first 3 Qualtrics metadata rows.
- Rows are kept when `Finished=True` or `Progress>=100`.
- Baseline rows are assigned phase label `Baseline`.
- Baseline has no TLX or Investment; these remain empty in output.
- Combined results are always written to repo-root `outputs/scores_combined.csv`.
- Trust outputs include:
  - Component X (A+C): perceived motion and pick-up speed, range 2-10
  - Component Y (D+F+H+I): perceived safe co-operation, range 4-20
  - Component Z (B+E+G+J): perceived robot and gripper reliability, range 4-20
  - Total trust score (X+Y+Z), range 10-50
  - Interpretation guidance: low (`<25`), moderate, very high (`>=45`)
