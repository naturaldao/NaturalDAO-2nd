# GOV-02 · Kev POL2 Governance Hybrid v2+v4 Unknown Gate

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| w609641894 / Codex | 已完成；模型卡、结果卡、数据卡、报告、两个 Release 已发布并校验 |

- 更新时间：2026-11-25 12:05 Asia/Shanghai
- 分支：main（提交 2dd301c）
- 目标与交付路径：models/kev-pol2-governance-hybrid-v2-v4-gate/；results/GOV-02-kev-pol2-governance-hybrid-20261125/；datasets/pol2/governance-v2/
- 本次改动范围：新增 governance hybrid 模型卡、结果卡、数据卡、报告；更新 registry 和 README
- 下一步：owner 复核；sealed blind 仍不读，production 仍未批准
- 阻塞 / 需要谁帮助：无
- 环境 / 输出路径 / 资源预算：NVIDIA GB10；两个 adapter；1896 steps；约 3 小时
- 数据版本与可用分区：pol2-governance-v2；train/validation/calibration/holdout；sealed blind 未读

状态：已完成发布。

## 进展与交流

2026-11-25｜w609641894 / Codex｜完成 v2/v3a/v3b/v4/v5/v6 对比，确定 hybrid-v2 为 pilot candidate pending blind｜完成仓库集成与两个 Release 上传

## 交付或交接

- 模型卡：models/kev-pol2-governance-hybrid-v2-v4-gate/README.md
- 结果卡：results/GOV-02-kev-pol2-governance-hybrid-20261125/README.md
- 数据卡：datasets/pol2/governance-v2/README.md
- 报告：docs/reports/2026-11-25-governance-hybrid-v2-v4-gate.md
- 权重 Release：https://github.com/naturaldao/NaturalDAO-2nd/releases/tag/pol2-governance-hybrid-v2-v4-gate-v1（258,098,904 bytes，SHA-256 7c1130…9bb4）
- 数据 Release：https://github.com/naturaldao/NaturalDAO-2nd/releases/tag/pol2-governance-v2-data-v1（437,149 bytes，SHA-256 c33657…7a4e）
- 校验：两个资产 state=uploaded，大小和 GitHub digest 与本地一致
- 仓库检查：tools/check.py 仅剩 TASKS.md 既有的 ../Research/Embodied 断链（本次改动前已存在，仓库内无 Research/ 目录）
- 限制：不是 production approved；sealed blind 未读；unknown 仍低于 0.80。
