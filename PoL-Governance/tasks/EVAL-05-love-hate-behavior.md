# EVAL-05：PoL2 爱2／恨2模型回应行为评测

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Aranna（项目管理员） / Codex（工程师及任务型 Agent 协调） | 进行中；六角色 Agent 团队完成首轮文档核对，团队设计与进展已整理入项目文档；等待作者冻结规范与管理员确认试验范围 |

- 更新时间：2026-11-17 UTC+8
- 分支：pol/EVAL-05/agent-team-plan
- 起点 commit / 依赖分支与 commit：main / 2ffcfe7d57d0387f944fda5e9f535309f321d2d5
- 目标与交付路径：评估主流大模型在标准化互动情境中的可观察回应行为，依据 PoL2 爱2／恨2判据诊断对齐表现；项目入口见 research/PoL2-Love-Hate-Behavior-Evaluation/README.md。
- 本次改动范围：同步 Agent 团队岗位、工作边界、首轮进展、规范待决项和推进顺序至 AGENT-TEAM-PLAN.md；未生成正式样本、未调用模型、未修改评测结果。
- 下一步：取得作者授权的理论原文、硬边界、事实 schema、规则及例外口径；管理员确认 pilot 范围、模型与预算、评审资源、数据和发布权限。完成这些前置项后开展小规模试标。
- 阻塞 / 需要谁帮助：PoL2 作者/授权人冻结规范；管理员确认项目资源。Discussion #82 为待审，完整理论、规则与实际接口尚未核验；自动轨不阻塞人工探索。详见 research/PoL2-Love-Hate-Behavior-Evaluation/ADMIN-INPUTS.md 和 AGENT-TEAM-PLAN.md。
- 环境 / 输出路径 / 资源预算：设计阶段不调用模型；供应商、模型和费用上限待管理员确认。
- 数据版本与可用分区：暂无本项目数据版本。现有 PoL2 冻结数据未声明为专家金标，不直接用作本项目参考标签。

状态：待领取 / 进行中 / 阻塞 / 暂停 / 待集成 / 完成。状态更新遵循仓库 AGENTS.md。

## 进展与交流

日期｜留言人/Agent｜进展、问题或回复｜证据/相关分支｜下一步
2026-11-15｜Codex｜核对 NaturalDAO-2nd 的 PoL2 原文、EAP、JUDGE、test-matrix、数据流水线与 benchmark 结构。建立 EVAL-05 分支并新增项目草案；将原文已有判据和管理员待决项分开。｜本分支；见 research/PoL2-Love-Hate-Behavior-Evaluation/｜等待管理员依据 ADMIN-INPUTS.md 确认理论与项目范围

2026-11-16｜Codex｜对照 [Discussion #82](https://github.com/naturaldao/NaturalDAO/discussions/82) v0.1 待审提案，更新 EVAL-05 v0.2：事实级标注、爱恨/治理动作分离、core/extended、人工与自动双轨、版本化接口；不修改 PoL2 理论，不复制未授权工作区资料。｜本分支；GOVERNANCE-INTEGRATION.md 与 schema.v0.2.json｜作者确认规范后开展试标；引擎另设接入门槛

2026-11-17｜Codex｜启动项目协调、规范转译、案例设计、标注质量、运行数据、结果分析与独立审查六个任务型 Agent。首轮核对确认项目仍为 design-v0.2，规范未冻结；整理角色任务、G0 待决项、探索性准备范围和后续顺序。未生成正式数据、未调用模型、未发布成绩。｜本分支；[AGENT-TEAM-PLAN.md](../research/PoL2-Love-Hate-Behavior-Evaluation/AGENT-TEAM-PLAN.md)｜由授权人确认规范；管理员确认 pilot 范围和资源

## 交付或交接

当前分支交付为团队工作框架与首轮进展记录；项目已有 v0.2 设计和数据格式草案（v0.1 保留）。未运行仓库完整检查或实验；尚无可运行引擎适配器。未完成项：冻结理论口径、生成并人工审查新情境、双盲标注、模型接入、评分实现和报告。公开分支不包含私有保留样本。
