# GOV-02 · Kev POL2 Governance Hybrid v2+v4 Unknown Gate

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| w609641894 / Codex | 进行中；模型卡、结果卡、数据卡和报告已准备，正在集成到 main |

- 更新时间：2026-11-25 12:00 Asia/Shanghai
- 分支：main
- 目标与交付路径：models/kev-pol2-governance-hybrid-v2-v4-gate/；results/GOV-02-kev-pol2-governance-hybrid-20261125/；datasets/pol2/governance-v2/
- 本次改动范围：新增 governance hybrid 模型卡、结果卡、数据卡、报告；更新 registry 和 README
- 下一步：发布 GitHub Release 资产；跑 tools/check.py；owner 复核
- 阻塞 / 需要谁帮助：无
- 环境 / 输出路径 / 资源预算：NVIDIA GB10；两个 adapter；1896 steps；约 3 小时
- 数据版本与可用分区：pol2-governance-v2；train/validation/calibration/holdout；sealed blind 未读

状态：进行中。

## 进展与交流

2026-11-25｜w609641894 / Codex｜完成 v2/v3a/v3b/v4/v5/v6 对比，确定 hybrid-v2 为 pilot candidate pending blind｜release/pol2-governance-hybrid-v2-v4-gate-v1｜发布 Release 并集成

## 交付或交接

- 模型卡：models/kev-pol2-governance-hybrid-v2-v4-gate/README.md
- 结果卡：results/GOV-02-kev-pol2-governance-hybrid-20261125/README.md
- 数据卡：datasets/pol2/governance-v2/README.md
- 报告：docs/reports/2026-11-25-governance-hybrid-v2-v4-gate.md
- 限制：不是 production approved；sealed blind 未读；unknown 仍低于 0.80。
