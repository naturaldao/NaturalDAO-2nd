# Comparison to v2 seed17 and the 2026-11-16 success report

## Overall accuracy

The 2026-11-16 report established the v2 seed17 gain: original base ~57% -> v2 78.97/82.73/78.13 (validation/calibration/holdout).

Hybrid-v2 does **not** raise that overall level:

- Original gold: 78.62/83.27/78.27 (-0.35/+0.54/+0.14 vs v2).
- Clean eval: 79.48/83.45/77.56 (0.00/+0.54/-0.14 vs v2).

The report's headline 57% -> 79-83% remains true; hybrid-v2 is an incremental safety upgrade, not a new accuracy tier.

## Unknown

This is the real gain:

| split | v2 original | hybrid original | v2 clean | hybrid clean |
|---|---:|---:|---:|---:|
| validation | 38.89 | 44.44 | 29.17 | 37.50 |
| calibration | 11.11 | 25.93 | 13.64 | 31.82 |
| holdout | 16.00 | 28.00 | 19.23 | 26.92 |

Still below 0.80. The hybrid improves the safety signal but does not solve the unknown gate.

## High-risk

Unchanged by hybrid-v2:

- Original: 44.44/88.89/75.00.
- Clean: 57.14/80.00/75.00.

v6 (risk_yes_weight=2.0) improves the standalone high-risk labels to 57.14/90.00/91.67, but its policy drops to 3/96 and unknown falls. It is a safety-focused alternative, not the default.

## Case exact

Unchanged: 0/32 (validation), 6/32 (calibration), 2/32 (holdout).

## ECE

Unchanged for hybrid-v2 (v2 probabilities): 8.50/7.89/8.18.

v5 has ECE 6.13/5.79/7.29 and v6 has 6.38/4.26/7.09, but both trade away unknown/high-risk/coverage.

## Weak axes from the report

The report named validation violence 0.667, retaliatory 0.542, discrimination 0.786, life 0.679; calibration life 0.667, public 0.438, autonomy 0.750.

Hybrid-v2 changes only the unknown decision. On the original eval:

- validation retaliatory 0.542 -> 0.583 (+4.2pp), discrimination 0.786 -> 0.750 (-3.6pp), violence/life/public/autonomy unchanged.
- calibration life 0.667 -> 0.708 (+4.2pp), public 0.438 -> 0.563 (+12.5pp), autonomy/violence/retaliatory/discrimination unchanged.
- holdout life 0.821 -> 0.786 (-3.6pp), other weak axes unchanged.

These are gate side effects on individual items, not systematic axis repair.

## Bottom line

Hybrid-v2 is the current best **coverage-preserving** candidate:

- auto-clear 5/96, critical 5/5, high-risk false allow 0.
- unknown improved.
- high-risk, case exact, ECE, and most weak axes are still open.
