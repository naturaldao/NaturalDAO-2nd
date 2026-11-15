# EVAL-05：PoL2 爱2／恨2模型回应行为评测

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Aranna（项目管理员） / Codex（工程师） | 进行中；已完成项目入口、回应标注草案和数据契约草案，等待管理员冻结理论边界 |

- 更新时间：2026-11-15 UTC+8
- 分支：pol/EVAL-05/love-hate-behavior
- 起点 commit / 依赖分支与 commit：main / 2ffcfe7d57d0387f944fda5e9f535309f321d2d5
- 目标与交付路径：评估主流大模型在标准化互动情境中的可观察回应行为，依据 PoL2 爱2／恨2判据诊断对齐表现；项目入口见 research/PoL2-Love-Hate-Behavior-Evaluation/README.md。
- 本次改动范围：新增项目方案、管理员材料清单、回应标注草案和 JSONL 数据契约；未生成评测样本、未调用模型、未发布成绩。
- 下一步：管理员确认理论基线、极性与 status 的关系、混合回应及安全守护边界、首轮场景和语言范围；随后完成小样本试标。
- 阻塞 / 需要谁帮助：需要项目管理员补充或确认，详见 research/PoL2-Love-Hate-Behavior-Evaluation/ADMIN-INPUTS.md。
- 环境 / 输出路径 / 资源预算：设计阶段不调用模型；供应商、模型和费用上限待管理员确认。
- 数据版本与可用分区：暂无本项目数据版本。现有 PoL2 冻结数据未声明为专家金标，不直接用作本项目参考标签。

状态：待领取 / 进行中 / 阻塞 / 暂停 / 待集成 / 完成。状态更新遵循仓库 AGENTS.md。

## 进展与交流

日期｜留言人/Agent｜进展、问题或回复｜证据/相关分支｜下一步
2026-11-15｜Codex｜核对 NaturalDAO-2nd 的 PoL2 原文、EAP、JUDGE、test-matrix、数据流水线与 benchmark 结构。建立 EVAL-05 分支并新增项目草案；将原文已有判据和管理员待决项分开。｜本分支；见 research/PoL2-Love-Hate-Behavior-Evaluation/｜等待管理员依据 ADMIN-INPUTS.md 确认理论与项目范围

## 交付或交接

当前交付为可审阅的设计和数据格式草案。未完成项：冻结理论口径、生成并人工审查新情境、双盲标注、模型接入、评分实现和报告。公开分支不包含私有保留样本。
