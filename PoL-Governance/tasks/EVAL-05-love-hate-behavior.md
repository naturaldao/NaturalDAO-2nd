# EVAL-05：PoL2 爱2／恨2模型回应行为评测

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Aranna（项目管理员） / Codex（工程师及任务型 Agent 协调） | 进行中；六岗位 Agent 完成 PDF 对照审阅；项目负责人已确认 PDF 优先级，映射表及草案更新已提交待审；仍待规则细节与项目设置 |

- 更新时间：2026-11-18 UTC+8
- 分支：pol/EVAL-05/pdf-alignment-review
- 起点 commit / 依赖分支与 commit：main / 2ffcfe7d57d0387f944fda5e9f535309f321d2d5
- 目标与交付路径：评估主流大模型在标准化互动情境中的可观察回应行为，依据 PoL2 爱2／恨2判据诊断对齐表现；项目入口见 research/PoL2-Love-Hate-Behavior-Evaluation/README.md。
- 本次改动范围：依据 2026-11-18 提供的 PoL2 混合治理 PDF，新增 H-01–H-09 规则映射审阅稿及无金标探索性候选场景；同步更新 README、标注手册、数据契约、machine schema、管理员待决项、Agent 团队进展和运行状态。记录按 PDF 优先级采用 hit→block、unknown→review 及 reciprocity=mutual/predation/unknown；更新与旧草案的冲突。规则操作化仍未冻结；未调用模型、未生成正式评分。
- 当前执行阻塞：仓库没有 EVAL-05 专用 runner/validator、正式场景集或人工标注；只有 v0.2 格式草案。旧 benchmark 的 20 条 pilot 和 DATA-02 数据不属于本项目金标，不直接复用。启动模型前需先冻结 G0 规范并实现/验证执行脚手架。
- 下一步：请 PoL2 作者/授权人确认 PDF 版本标识与授权范围、H-01–H-09 触发/例外/证据要求、H-07 外部核验，以及 H-07/H-09 重叠和 hit+unknown 冲突优先级；管理员确认 pilot 范围、模型与预算、评审资源、数据和发布权限。确认后冻结 rubric/schema，完成专用运行与标注工具，再开展试标及模型运行。
- 阻塞 / 需要谁帮助：PoL2 作者/授权人确认本轮 PDF 的规范地位及规则裁定；管理员确认项目资源。PDF 优先级已确认，硬边界 unknown 按 PDF 进入 review；规则的具体操作化仍待确认。自动轨不阻塞人工探索。详见 ADMIN-INPUTS.md、POL2-SOURCE-MAPPING.md 和 AGENT-TEAM-PLAN.md。
- 环境 / 输出路径 / 资源预算：设计阶段不调用模型；供应商、模型和费用上限待管理员确认。
- 数据版本与可用分区：暂无本项目数据版本。现有 PoL2 冻结数据未声明为专家金标，不直接用作本项目参考标签。

状态：待领取 / 进行中 / 阻塞 / 暂停 / 待集成 / 完成。状态更新遵循仓库 AGENTS.md。

## 进展与交流
\n2026-11-19｜Codex + 三岗位 Agent｜从评测效度、理论覆盖和运行可行性独立评议首轮范围，三方一致建议正式范围限于 H-01 至 H-09 硬边界子集；同步开展不计分的 PoL2/EAP 理论覆盖审计与探索性案例准备。未操作化的正向关系构念不纳入首轮分数；未冻结 H1–H9 逐条触发、例外与证据要求前仅能试标，不能发布正式成绩。报告不得称为完整 PoL2 对齐评测，不将 pass=爱或 block=恨。｜PR #25；README、ADMIN-INPUTS.md｜后续冻结 H1–H9 操作标准，确定 pilot 模型/预算/评审资源；另行设计扩展评测\n\n
日期｜留言人/Agent｜进展、问题或回复｜证据/相关分支｜下一步
2026-11-15｜Codex｜核对 NaturalDAO-2nd 的 PoL2 原文、EAP、JUDGE、test-matrix、数据流水线与 benchmark 结构。建立 EVAL-05 分支并新增项目草案；将原文已有判据和管理员待决项分开。｜本分支；见 research/PoL2-Love-Hate-Behavior-Evaluation/｜等待管理员依据 ADMIN-INPUTS.md 确认理论与项目范围

2026-11-16｜Codex｜对照 [Discussion #82](https://github.com/naturaldao/NaturalDAO/discussions/82) v0.1 待审提案，更新 EVAL-05 v0.2：事实级标注、爱恨/治理动作分离、core/extended、人工与自动双轨、版本化接口；不修改 PoL2 理论，不复制未授权工作区资料。｜本分支；GOVERNANCE-INTEGRATION.md 与 schema.v0.2.json｜作者确认规范后开展试标；引擎另设接入门槛

2026-11-17｜Codex｜启动项目协调、规范转译、案例设计、标注质量、运行数据、结果分析与独立审查六个任务型 Agent。首轮核对确认项目仍为 design-v0.2，规范未冻结；整理角色任务、G0 待决项、探索性准备范围和后续顺序。未生成正式数据、未调用模型、未发布成绩。｜上一工作分支；[AGENT-TEAM-PLAN.md](../research/PoL2-Love-Hate-Behavior-Evaluation/AGENT-TEAM-PLAN.md)｜由授权人确认规范；管理员确认 pilot 范围和资源

2026-11-18｜Codex + 六岗位 Agent｜对照混合治理 PDF，确认 EVAL-05 与 L0–L4 治理系统是独立评测对象；完成 H-01–H-09 规则映射和无金标候选场景。记录 hit→block、unknown→review 与 reciprocity=mutual/predation/unknown；项目负责人确认 PDF 与 EVAL-05 草案冲突时以 PDF 为准。H-07 外部核验、H-07/H-09 重叠及 hit+unknown 优先级仍待确认。仓库核查确认无 EVAL-05 runner/validator、正式场景集或标注；现有 pilot/DATA-02 数据不直接复用。未调用模型、未产生正式成绩。｜本分支；[规则映射表](../research/PoL2-Love-Hate-Behavior-Evaluation/POL2-SOURCE-MAPPING.md)、[探索性场景](../research/PoL2-Love-Hate-Behavior-Evaluation/EXPLORATORY-CASE-CANDIDATES.md)｜作者确认规范与字段；管理员确认模型、预算、人员、授权｜本分支；[规则映射表](../research/PoL2-Love-Hate-Behavior-Evaluation/POL2-SOURCE-MAPPING.md)｜请授权人确认规范，项目管理员审阅映射与 pilot 设置

## 交付或交接

当前分支交付为团队工作框架、PDF 对照更新和规则映射审阅稿；项目有 design-v0.3 兼容性文档草案，旧数据契约保留。未运行仓库完整检查或实验；尚无可运行引擎适配器。未完成项：冻结理论口径、生成并人工审查新情境、双盲标注、模型接入、评分实现和报告。公开分支不包含私有保留样本。
