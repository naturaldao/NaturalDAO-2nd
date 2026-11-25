# GOV-02 · Kev POL2 Governance Hybrid v2+v4 Unknown Gate

- 任务 / 分支 / 领取人：GOV-02 / main / w609641894 + Codex
- 模型：kev-4b-pol2-governance-hybrid-v2-v4-gate
- 数据：pol2-governance-v2；train 192 / 3424 qids；validation 32 / 580；calibration 32 / 556；holdout 32 / 704
- 硬件：NVIDIA GB10；1896 steps；约 3 小时；两个 adapter
- 状态：pilot candidate pending blind；不是 production approved

# POL2 Governance Hybrid v2+v4 Unknown Gate v1

Status: **PILOT_PRODUCTION_CANDIDATE_PENDING_BLIND**

- production_approved: false
- sealed_blind_read: false
- training: stopped at this stage

## What this version is

Two adapters and one decision rule:

1. **Label model**: v2 seed17 (stage1-v2) produces the normal label for every qid.
2. **Unknown detector**: v4 seed17 (stage1-v4-unknown3, unknown_weight=3.0) produces p_unknown.
3. **Gate**: if v4 p_unknown > 0.60, the final label becomes unknown; otherwise the v2 label stands.
4. **Policy**: confidence >= 0.70, high-risk p_yes <= 0.20, full 18/27-qid cases only.

This is a fail-closed routing candidate, not a production approval.

## Accuracy: original gold (report-compatible)

| set | v2 seed17 | hybrid-v2 | delta |
|---|---:|---:|---:|
| validation | 78.97 | 78.62 | -0.35pp |
| calibration | 82.73 | 83.27 | +0.54pp |
| holdout | 78.13 | 78.27 | +0.14pp |

## Accuracy: 376-adjudicated clean eval

| set | v2 seed17 | hybrid-v2 | delta |
|---|---:|---:|---:|
| validation | 79.48 | 79.48 | 0.00pp |
| calibration | 82.91 | 83.45 | +0.54pp |
| holdout | 77.70 | 77.56 | -0.14pp |

## What actually improved

Unknown recall is the only stable gain:

| unknown recall | v2 | hybrid |
|---|---:|---:|
| validation (original) | 38.89 | 44.44 |
| calibration (original) | 11.11 | 25.93 |
| holdout (original) | 16.00 | 28.00 |
| validation (clean) | 29.17 | 37.50 |
| calibration (clean) | 13.64 | 31.82 |
| holdout (clean) | 19.23 | 26.92 |

It is still below the 0.80 production gate.

## What did not improve

- Overall accuracy is flat within noise.
- High-risk yes recall is unchanged: 44.44/88.89/75.00 (original) and 57.14/80.00/75.00 (clean).
- Case exact is unchanged: 0/32, 6/32, 2/32.
- ECE is unchanged: 8.50/7.89/8.18 (v2 probabilities).
- Most weak axes from the 2026-11-16 report are unchanged; small +/-4-12pp moves are gate artifacts, not systematic fixes.

## Artifacts

- VERSION-MANIFEST.json: component and data hashes.
- METRICS.json: machine-readable metrics.
- COMPARISON-TO-V2.md: detailed comparison against v2 and the 2026-11-16 success report.
- INFERENCE-CONTRACT.md: exact two-adapter inference and policy.
- DATA-FREEZE.md: data and adjudication lineage.
- GITHUB-UPDATE-PLAN.md: what to commit, what not to commit.
- GITHUB-UPLOAD-MAPPING-v1.md: verified repo inventory and target paths.
- artifacts/: small JSON/Markdown evidence files.
- CHECKSUMS.sha256: checksums of this bundle.

## Boundaries

- Do not commit the 129MB adapters to Git; use Git LFS or GitHub Releases.
- Do not commit credentials, SSH material, sealed blind, or session logs.
- Do not claim production approval or full automation.
