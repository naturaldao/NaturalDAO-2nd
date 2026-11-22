# 研究与文献阅读指南

[返回治理层首页](../README.md)

本页按研究问题组织材料。先读综述与问题定义，再查原始证据，最后进入实验与工程。各项目的结论只适用于其注明的时间、模型、数据和假设。

## 建议阅读顺序

1. **了解目标**：[研究规范](../SPEC.md)。明确治理层要改善什么、如何评估。
2. **了解已有证据**：[类型化决策模型综述](PoL2-Jev-Typed-Literature-Survey/README.md)。先读主要发现，再读英文论文与附录。
3. **了解制度机制**：[DAO 治理实验室](PoL2-DAO-Governance-Lab/README.md)。观察投票、资源分配、申诉和复核的机制与条件。
4. **了解怎样验证**：[评测不确定性](PoL2-Eval-Uncertainty/README.md)与[爱2／恨2行为评测设计](PoL2-Love-Hate-Behavior-Evaluation/README.md)。区分统计方法研究与尚未冻结的评测方案。
5. **参与实现**：[数据](../datasets/README.md) → [评估](../benchmark/README.md) → [结果](../results/README.md)。任务进度以[任务页](../TASKS.md)为准。

## 按问题查资料

| 研究问题 | 首选材料 | 证据与使用边界 |
|---|---|---|
| 类型化模型能否做治理检测或裁决？ | [Jev 综述](PoL2-Jev-Typed-Literature-Survey/README.md) | 文献综合；证据截至 2026-10-08，不能直接代表后来模型 |
| 如何追溯一项综述结论？ | [文献与证据索引](LITERATURE.md) | 从论文结论追到编码、研究记录和原文 |
| 投票、短缺分配和申诉规则如何影响结果？ | [DAO 实验设计](PoL2-DAO-Governance-Lab/docs/experiment-design.md)与[结果](PoL2-DAO-Governance-Lab/docs/results.md) | 含合成模拟、模型计算及公开数据复算；分别解读 |
| 样本相关性与标签噪声如何影响模型比较？ | [不确定性研究](PoL2-Eval-Uncertainty/README.md) | 模拟与闭式计算；假设参数不是真实模型测量 |
| 如何评价模型回应中的爱2／恨2行为？ | [行为评测方案](PoL2-Love-Hate-Behavior-Evaluation/README.md) | design-v0.3 尚未冻结；该版声明尚未生成正式数据或运行模型 |
| 如何调研和筛选模型？ | [模型目录](../models/CATALOG.md)与[调研模板](model-research-example.md) | 模型选型材料，与文献证据分开使用 |
| 协作者的补充调研在哪里？ | [Wenbo 调研](Wenbo/deep-research-report.md)、[数据笔记](Wenbo/data.md)、[Chun 实施路径](Chun/实施路径说明.md) | 补充材料；引用前核对其来源、日期及适用范围 |

## 文档如何维护

- 新研究材料先在本页增加“问题、入口、证据边界”，再在所属项目内维护详细目录。
- 正文、原始来源、数据、实验结果、工作笔记分别说明用途；计划不能作为实验结果引用。
- 被新版本取代的材料标明替代入口和版本差异。保留可复查的原路径，避免已有引用失效。
- 综述引用具体研究时回到原论文；引用项目结果时注明数据版本、配置及结果文件。
- 本页负责阅读导航，不复制任务状态，也不代替各项目的来源核验。
