# PoL2 governance-v2 决策数据

- ID / 版本：pol2-governance-v2 / v2.0.0
- 许可：POL2 原创内容遵循 PoL-Governance 当前许可
- 标注：独立 A/B + AI 第三裁决；不是人类专家金标
- training_approved：true（owner 授权）
- sealed blind：未包含、未读取
- holdout：按 owner 决定公开

# Data freeze and adjudication lineage

## Training data

| item | value |
|---|---|
| v3b train cases | 192 |
| v3b train families | 48 |
| v3b train qids | 3424 |
| v3b train SHA-256 | 25ee567b59b76f2b3bf01823f6bea798040e576b1cfdbb84291eaa5235a93d3f |
| v5 clean train cases | 192 |
| v5 clean train qids | 3424 |
| v5 clean train SHA-256 | a4d012543f69ba5f020416cffd48b655a9953260bf3fdc4efb64416ed18b3126 |
| v5 clean base (160 cases) SHA-256 | e549729ea0ce7c2da80a3c46f88353b5efc084ac1afefbfcae8f8d254cd7df14 |
| v5 repeat4 mix rows | 7595 |
| v5 repeat4 mix SHA-256 (remote) | d88974d1eaf900c5d324b467d9d30e53fcff8932e1037d9e10f1293f03805eeb |

## Adjudication

| item | value |
|---|---|
| eval disagreements adjudicated | 376 |
| eval adjudication file SHA-256 | f0545b0000c3da19a17664e41bc9ec630adac2de3d354694a9c768f83233107b |
| train disagreements adjudicated | 584 |
| train labels changed | 202 |
| train adjudication file SHA-256 | 66fb64e786f68161c446d459605b586368a1e5fca9cca8e224bfae04789ea212 |
| train adjudication chosen | A 322 / B 241 / NEITHER 21 |

The 144-case train split has 2640 qids. 202 changed labels are 7.65% of the train qids.

## Eval sets

- validation: 32 cases, 580 qids.
- calibration: 32 cases, 556 qids.
- holdout: 32 cases, 704 qids.
- Focused 4/5-qid cases remain in the payload but are never auto-clear eligible.

## Boundaries

- sealed blind is not frozen or read.
- v3a/v3b/v4 standalone/v5/v6 are research runs; only hybrid-v2 is the current pilot candidate.
