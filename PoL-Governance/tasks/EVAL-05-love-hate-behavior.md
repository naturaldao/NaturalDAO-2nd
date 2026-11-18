# EVAL-05：PoL2 爱2／恨2模型回应行为评测

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Aranna（项目管理员） / Codex（工程师及任务型 Agent 协调） | 进行中；六岗位 Agent 完成 PDF 对照审阅，映射表和 design-v0.3 兼容更新已提交待审；等待授权人确认规范来源及项目设置 |

- 更新时间：2026-11-18 UTC+8
- 分支：pol/EVAL-05/pdf-alignment-review
- 起点 commit / 依赖分支与 commit：main / 2ffcfe7d57d0387f944fda5e9f535309f321d2d5
- 目标与交付路径：评估主流大模型在标准化互动情境中的可观察回应行为，依据 PoL2 爱2／恨2判据诊断对齐表现；项目入口见 research/PoL2-Love-Hate-Behavior-Evaluation/README.md。
- 本次改动范围：依据 2026-11-18 提供的 PoL2 混合治理 PDF，增加 H-01–H-09 到 EVAL-05 的规则映射审阅稿；同步更新 README、标注手册、数据契约、管理员待决项及 Agent 团队进展。将 hit→block、unknown→review 标作 PDF 候选口径，等待授权人冻结；未生成正式样本、未调用模型、未修改评测结果。
- 下一步：请 PoL2 作者/授权人确认 PDF 的规范版本与优先级、H-01–H-09 触发/例外/证据要求、unknown→review 与 H-07 外部核验口径，以及 H-07/H-09 重叠和 hit+unknown 冲突优先级；管理员确认 pilot 范围、模型与预算、评审资源、数据和发布权限。确认后更新 rubric/schema 并开展小规模试标。
- 阻塞 / 需要谁帮助：PoL2 作者/授权人确认本轮 PDF 的规范地位及规则裁定；管理员确认项目资源。PDF 与旧草案的硬边界 unknown 口径冲突，现仅记录候选修订。自动轨不阻塞人工探索。详见 ADMIN-INPUTS.md、POL2-SOURCE-MAPPING.md 和 AGENT-TEAM-PLAN.md。
- 环境 / 输出路径 / 资源预算：设计阶段不调用模型；供应商、模型和费用上限待管理员确认。
- 数据版本与可用分区：暂无本项目数据版本。现有 PoL2 冻结数据未声明为专家金标，不直接用作本项目参考标签。

状态：待领取 / 进行中 / 阻塞 / 暂停 / 待集成 / 完成。状态更新遵循仓库 AGENTS.md。

## 进展与交流

日期｜留言人/Agent｜进展、问题或回复｜证据/相关分支｜下一步
2026-11-15｜Codex｜核对 NaturalDAO-2nd 的 PoL2 原文、EAP、JUDGE、test-matrix、数据流水线与 benchmark 结构。建立 EVAL-05 分支并新增项目草案；将原文已有判据和管理员待决项分开。｜本分支；见 research/PoL2-Love-Hate-Behavior-Evaluation/｜等待管理员依据 ADMIN-INPUTS.md 确认理论与项目范围

2026-11-16｜Codex｜对照 [Discussion #82](https://github.com/naturaldao/NaturalDAO/discussions/82) v0.1 待审提案，更新 EVAL-05 v0.2：事实级标注、爱恨/治理动作分离、core/extended、人工与自动双轨、版本化接口；不修改 PoL2 理论，不复制未授权工作区资料。｜本分支；GOVERNANCE-INTEGRATION.md 与 schema.v0.2.json｜作者确认规范后开展试标；引擎另设接入门槛

2026-11-17｜Codex｜启动项目协调、规范转译、案例设计、标注质量、运行数据、结果分析与独立审查六个任务型 Agent。首轮核对确认项目仍为 design-v0.2，规范未冻结；整理角色任务、G0 待决项、探索性准备范围和后续顺序。未生成正式数据、未调用模型、未发布成绩。｜上一工作分支；[AGENT-TEAM-PLAN.md](../research/PoL2-Love-Hate-Behavior-Evaluation/AGENT-TEAM-PLAN.md)｜由授权人确认规范；管理员确认 pilot 范围和资源

2026-11-18｜Codex + 六岗位 Agent｜对照老板提供的混合治理 PDF，确认 EVAL-05 与 L0–L4 治理系统是独立评测对象；提出硬边界 hit→block、unknown→review 的候选修订，标记与旧草案冲突并待授权人确认；完成 H-01–H-09 规则映射审阅稿，记录 H-07 外部核验、H-07/H-09 重叠及 hit+unknown 优先级待决项。同步更新项目 README、标注手册、数据契约、管理员输入和团队计划。未生成正式样本、未调用模型、未发布成绩。｜本分支；[规则映射表](../research/PoL2-Love-Hate-Behavior-Evaluation/POL2-SOURCE-MAPPING.md)｜请授权人确认规范，项目管理员审阅映射与 pilot 设置

## 交付或交接

当前分支交付为团队工作框架、PDF 对照更新和规则映射审阅稿；项目有 design-v0.3 兼容性文档草案，旧数据契约保留。未运行仓库完整检查或实验；尚无可运行引擎适配器。未完成项：冻结理论口径、生成并人工审查新情境、双盲标注、模型接入、评分实现和报告。公开分支不包含私有保留样本。
