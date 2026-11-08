# Research · 研究导航

这里收录 NaturalDAO / Proof of Love2 的研究综述、技术提案、外部论文与实验记录。先按主题进入，再按阅读目的选择材料。

## 从哪里开始

| 研究方向与问题 | 报告或阅读入口 | 材料状态 | 复现或核查入口 |
|---|---|---|---|
| 具身智能与治理 · 如何把授权、撤权与恢复落实到行动 | [具身研究索引](Embodied/README.md) | 框架草案与探索性仿真 | [具身评测代码与运行说明](../PoL-Governance/benchmark/embodied_reasoning/README.md) |
| 存储与数据基础设施 · 如何支撑检索、训练谱系与恢复 | [存储研究索引](Storage/README.md) | V2 技术提案，待工程验证 | [容量复算与假设](Storage/03-复算与支撑/README.md) |
| 软件工程与智能体记忆 · 如何设计治理服务并衡量记忆收益 | [工程设计与论文索引](Engineering/README.md) | 实现快照、调研笔记和外部论文 | [Steward 服务与运行说明](../POL2-Steward/README.md) |
| DAO 治理机制 · 如何将治理条款落实到投票、资源分配与申诉 | [治理实验室的实验结果](../PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md#结果) | 模拟实验与公开试例 | [运行示例与测试](../PoL-Governance/research/PoL2-DAO-Governance-Lab/README.md#快速开始) |
| 类型化决策模型 · 在什么条件下能承担治理判断 | [PoL2 × Jev 综述论文](../PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/paper/main.pdf) · [在线附录](../PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/paper/online_appendix.pdf) | 研究稿，结论基于早期证据 | [文献编码与构建方法](../PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/README.md#复现) |

首次阅读具身方向，建议先看主题页的结论边界，再选择框架、方法或实验主线，无需逐篇阅读全部实验。

## 目录结构

```text
Research/
├── README.md
├── Embodied/       # 具身智能与治理
├── Storage/        # 存储与数据基础设施
├── Engineering/    # 软件工程设计与智能体记忆论文
└── figures/        # 实验共用图件与重绘脚本
```

实验代码和逐轨迹数据仍在[具身评测目录](../PoL-Governance/benchmark/embodied_reasoning/README.md)。Research 保存研究叙述和图件；[共用图件](figures/README.md)保留原输出位置，方便现有脚本继续使用。

## 后续如何维护

提交新研究时参照[研究提交清单](../CONTRIBUTING.md#提交研究--submit-research)。

- **先归主题，再建文档。** 新材料放入相应分组，在主题 README 增加研究问题、报告入口和结论边界；总 README 只保留主题入口。
- **同一问题接续更新。** 参数重跑通常更新原报告和结果索引；研究问题或方法变化时再新建报告，避免每轮运行都新增顶层文件。
- **分别标明材料状态。** 提案不等于已实现能力，探索性仿真不等于通用安全结论，适用范围以报告为准。
- **保留历史与失败证据。** 明确被替代的旧版放入主题内 `99-归档/` 并注明替代入口；失败实验仍按研究问题保留。
- **维护可追溯链接。** 正文使用相对链接，图件指向具体版本，数据留在评测目录；搬迁时同步更新引用。
- **来源按原文核对。** AI 辅助综述与实测结果应区分，外部论文按原文引用。

第一方标识为 **Proof of Love2**；第三方材料保留原许可，此前已授予的 CC0 权限不因标识更新撤销。
