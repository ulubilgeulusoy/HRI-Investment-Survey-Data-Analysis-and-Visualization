# Column Mapping (1-based)

## Break CSV (`Break_April 13, 2026_13.46.csv`)
- Participant ID: 18 (`ID`)
- Phase: 19 (`Phase`)
- TLX pairwise choices: 20-34 (`Q1..Q15`)
- TLX ratings: 35-40 (`NASA TLX_1..NASA TLX_6`)
- Investment items: 41-46 (`QID1721042963_1..QID1721042968_1`)
- Respect/Self-confidence/Perception: 51,52,53 (`Q2_1,Q3_1,Q4_1`)
- Trust items: 54-63 (`A..J`)
- Quality filters: 7 (`Finished`), 5 (`Progress`)

## Baseline CSV (`Baseline_April 13, 2026_13.51.csv`)
- Participant ID: 18 (`Q1`)
- Phase: injected constant value `Baseline`
- Respect/Self-confidence/Perception: 19,20,21 (`Q2_1,Q3_1,Q4_1`)
- Trust items: 22-31 (`A..J`)
- Quality filters: 7 (`Finished`), 5 (`Progress`)
- TLX and Investment: not present

## Trust Scoring
- Likert map: `Strongly disagree=1`, `Somewhat disagree=2`, `Neither=3`, `Somewhat agree=4`, `Strongly agree=5`
- Reverse-coded items: `A`, `C`, `G`
- Output: mean (1-5) and normalized score (0-100)

## Weighted TLX
- Uses 15 pairwise choices to form weights across dimensions.
- Weighted TLX = `sum(weight_i * rating_i) / 15`
