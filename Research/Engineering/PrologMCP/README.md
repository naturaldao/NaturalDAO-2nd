# PrologMCP 能为 NaturalDAO 的 PoL 判断什么？

调研日期为 2026 年 11 月 19 日。**建议先把 PrologMCP 用作 PoL Gate 的只读规则复核器。** 例如，智能体报告“所有测试都通过了”，同一任务的上下文却写着“只做了静态检查”。NaturalDAO 的 Proof of Love2（PoL2）治理服务已有要求改写这类输出的规则。本次调研把这一条冲突条件写成 Prolog，通过作者的 MCP 服务实际查到了命中它的两项事实。这个结果支持将工具用于核对规则、解释命中原因。至于记录是否可信、当事人是否真正同意、某项行动能否放行，分别需要证据核验、情境判断和治理服务授权。[NaturalDAO 现有回归用例](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/POL2-Steward/pol2-service/tests/test_governance.py#L148-L187)

**同题对照实测**　[PrologMCP、Euclid-MCP、Llama 与本地 Kev M10](comparison/README.md) 在 20 道合成题上分别检验从原文判断、抽取事实和执行规则，并回放 Euclid 论文表 2 五道原题。[逐题输出](comparison/predictions.csv) · [复验方法](comparison/RUN.md)

## 从一句话到一次可检查的推导

本文讨论的是 Agnieszka Mensfelt 等人论文对应的开源项目 **dicelab-rhul/PrologMCP**。Prolog 让开发者写下事实和“满足哪些条件就能推出什么”的规则，再用查询询问某项结论能否成立。SWI-Prolog 是实际执行这些查询的软件。MCP（Model Context Protocol，模型上下文协议）规定应用如何发现和调用工具。PrologMCP 把这三件事连起来：客户端提交程序，服务器为它保留独立的运行会话，后续查询可以沿用同一套事实和规则。自然语言翻译由调用方完成。论文中的 **MCPFormalizer** 是使用这个服务解题的智能体，也是独立的评测项目。[论文](https://arxiv.org/abs/2606.14935) · [MCP 官方架构](https://modelcontextprotocol.io/docs/learn/architecture) · [MCPFormalizer 代码与日志](https://github.com/dicelab-rhul/MCPFormalizer)

![论文图 1：智能体通过 MCP 客户端连接 PrologMCP 服务，由独立的 Prolog 运行环境处理查询](assets/PrologMCP_arch.svg)

**图 1　作者的 PrologMCP 架构原图。** 从客户端沿请求方向读，先找到 MCP 服务，再找到持有程序状态的 Prolog 进程；沿相反方向返回的是执行结果。转载自 Agnieszka Mensfelt、Adarsh Prabhakaran、Adrian Haret、Vince Trencsenyi、Kostas Stathis，*PrologMCP: A Standardized Prolog Tool Interface for LLM Agents*（2026），图 1，原图未改动。该图沿用论文标注的 CC BY 4.0 许可。[原文图 1](https://arxiv.org/html/2606.14935v2#S2.F1) · [原文许可声明](https://arxiv.org/pdf/2606.14935v2#page=1) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

论文将程序装载写作 `consult_text`。复验时固定的作者代码版本提供十个工具，首次装载应调用 **`create_session`**。应用拿到 `load_id` 后，可用 `run_goal` 询问结论，用 `trace_goal` 查看有限深度的调用树，用 `close_session` 结束会话。开发者还可补充源码、检查谓词、读取诊断或运行 PlUnit 测试。规则写错时，这套接口便于定位错误；进入治理判断时，则应锁定已审核的版本，以免同一申请在查询中途换了判断依据。会话可以回收，长期复核需要另存规则版本、证据引用、查询和响应。[论文 §4.1](https://arxiv.org/html/2606.14935v2#S4.SS1) · [固定版本的工具定义](https://github.com/dicelab-rhul/PrologMCP/blob/4ae536fd9b1cef8419d1798b5d4cb1569cba3cae/src/prolog_mcp/server.py#L71-L273)

## 论文中的满分适用于什么任务？

作者使用 PARARULE-Plus 合成演绎题。每道题给出事实、规则和一个真假问题，形式化智能体需要将三者译为程序和查询。常规组 400 题覆盖 2 至 5 层推导。下表是论文表 3 的结果，本次调研未复跑这一基准。[实验设计](https://arxiv.org/html/2606.14935v2#S4.SS2) · [论文表 3](https://arxiv.org/html/2606.14935v2#S5.T3)

| 常规组指标 | 直接回答 | 推理模型或思考模式 | 形式化后调用 Prolog |
|---|---:|---:|---:|
| Claude Sonnet 4.6 准确率 | 98.8% | 100% | 100% |
| Claude 平均耗时 | 3.57 秒 | 4.64 秒 | 5.11 秒 |
| OpenAI 组准确率 | 76.2% | 99.8% | 100% |
| OpenAI 组平均耗时 | 0.98 秒 | 11.27 秒 | 4.23 秒 |

OpenAI 组直接回答及形式化均用 GPT-4.1，推理组用 o4-mini。Claude 两种高准确率配置同获满分，Prolog 路径平均多花 0.47 秒。论文另选了 200 道容易因否定语义而误判的题，Claude 与 OpenAI 形式化组分别为 100% 和 99%，对应推理组为 95% 和 94%。**这 200 题的标准答案全为假**，恒答“假”也能满分。这组题适合诊断特定推理错误，不能估计真实审批中误放和误拦各有多少。作者还指出，实验中的首次形式化均成功，因此这批结果也不足以衡量自动修错的作用。[论文表 7](https://arxiv.org/html/2606.14935v2#S5.T7) · [作者对局限的说明](https://arxiv.org/html/2606.14935v2#S7)

## 用 NaturalDAO 的“测试通过”用例走一次

仓库的 PoL 治理规范覆盖输入、输出和工具行动。这里选择输出环节，因为它已有清晰的实现和测试预期。现有 Python 检查匹配两组文字，一组来自智能体的输出，另一组来自上下文。出现“全量通过”与“仅静态检查”的组合时，服务返回 `revise`，关联 `POL2-R011`（结果责任与核验）及 `POL2-R012`（诚实表达），测试同时要求 `release is None`。面向使用者的改写可以很简单：“我只做了静态检查，全量测试结果尚未验证。” [治理规范](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/PoL-Governance/SPEC.md) · [规则映射](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/POL2-Steward/pol2-service/packages/pol2-runtime-2026.10.21.1/knowledge/rule-mapping.jsonl) · [Python 实现](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/POL2-Steward/pol2-service/service/governance.py#L182-L207)

以下是**本次实际通过 MCP 调用**的完整小程序。两案的输出都声称全量测试通过，只有第一案带有“仅做了静态检查”的事实。逗号表示两个条件须同时成立，变量 `C` 约束它们属于同一案件。这里的 `revise(C)` 仅表示这条冲突规则命中。

```prolog
claims_all_tests_passed(case1).
claims_all_tests_passed(case2).
reports_static_only(case1).
revise(C) :- claims_all_tests_passed(C), reports_static_only(C).
```

Windows x64 本地复验使用 Python 3.13.15、MCP Python SDK 1.30.0、SWI-Prolog 10.0.2 和作者仓库提交 `4ae536f`。客户端通过标准输入输出连接原版服务器，`create_session` 装载上述程序，返回 `ok=true` 和空诊断列表。随后在同一会话中调用两次 `run_goal`。[上游固定版本](https://github.com/dicelab-rhul/PrologMCP/tree/4ae536fd9b1cef8419d1798b5d4cb1569cba3cae)

| 查询 | 实际返回的主要字段 | 对案件的解读 |
|---|---|---|
| `revise(case1)` | `ok=true, outcome=success, answers=[], truncated=false` | 两项前提齐全，命中改写条件。 |
| `revise(case2)` | `ok=true, outcome=failure, answers=[], truncated=false` | 此快照推不出改写条件；还需核实测试状态。 |

两次调用都被工具正常处理。查询中没有待求值的变量，所以成功时也可以有空的 `answers`。对第一案调用 `trace_goal`，得到一条成功路径，其叶节点分别是该案的两项事实。最后 `close_session` 返回 `closed=true`。这次测试覆盖客户端、传输、服务器、求解器和追踪；事实由调研者手工提供，未测试日志鉴真、模型抽取或线上治理。若另一案确有同一提交的全量测试通过记录，冲突查询同样会返回 `failure`，但可以继续其他检查。区分这两种“未命中”，必须回到证据状态。[作者的查询测试](https://github.com/dicelab-rhul/PrologMCP/blob/4ae536fd9b1cef8419d1798b5d4cb1569cba3cae/tests/test_goal.py)

## PoL 可以怎样接入这项检查？

下图是**拟议的只读旁路**。现有 PoL Gate 照常判断，旁路只提供规则命中或推导未完成的说明。第一步应确定证据属于哪一次运行、哪一个提交、哪一套测试。即使记录本身真实，把昨天的测试结果配给今天的提交，也会让正确的推理得出不适用的结论。

```mermaid
flowchart TD
    A["智能体输出、上下文和运行记录"] --> B["现有 PoL Gate 审查"]
    A --> C["拟议旁路：绑定案件、提交、测试范围和出处"]
    C --> D{"输入证据状态"}
    D -->|"缺少运行记录"| E["标记待补证"]
    D -->|"来源或范围有冲突"| F["列出冲突，交人工复核"]
    D -->|"可核对"| G["为该案装载已审核规则与事实快照"]
    G --> H{"PrologMCP 查询结果"}
    H -->|"命中"| I["记录 R011、R012 及两项前提"]
    H -->|"未命中"| J["记录此项无命中，继续其他检查"]
    H -->|"超时、错误或结果不完整"| K["标记技术未完成"]
    E --> L["旁路记录：证据引用、规则版本、查询与结果"]
    F --> L
    I --> L
    J --> L
    K --> L
    B --> M["现有治理服务处理改写、复核或放行"]
    B --> N["离线逐案比较"]
    L --> N
```

**图 2　PoL 影子接入流程（本报告设计）。** [下载高清流程图](assets/pol-flow.png) 右侧复核结果与原判断逐案比较，不向执行端签发许可。通过追踪得到的是“程序用了哪条子句”；要回答“这项事实来自哪里”，应用还需保留原输出片段、执行记录引用和版本化的子句到政策编号映射。需区分加载诊断、查询状态、超时和答案截断。特别是枚举所有命中规则时，截断会破坏结果的完整性。作者将服务定位于本地开发，名称过滤只能提供有限保护；试点宜装载固定规则、将外部文本作为受限事实输入，并隔离执行进程。[上游服务说明与限制](https://github.com/dicelab-rhul/PrologMCP/blob/4ae536fd9b1cef8419d1798b5d4cb1569cba3cae/README.md)

**对“同意”也只能做条件判断。** 以候选运行包的 R024 为例，共享资源分配涉及当事人的权益，可以检查记录中的人、授权事项、时间和撤回状态是否覆盖本次行动。某人没有记录，应标为未知；同意和撤回记录并存，应先复核时间与范围。普通研究报告只是提及多人，则要先判断该授权规则是否适用。实际同意是否出于自由意愿、受影响者名单是否完整，都需要调查或当事人确认。尤其不能把 Prolog 的“暂时找不到反例”写成“全体已同意”。[项目规则映射](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/POL2-Steward/pol2-service/packages/pol2-runtime-2026.10.21.1/knowledge/rule-mapping.jsonl) · [SWI-Prolog 否定语义](https://www.swi-prolog.org/pldoc/doc_for?object=%28%5C%2B%29%2F1)

## 哪些结果足以支持继续接入？

单条 Python 条件已经能处理上面的回归用例，增加 MCP 的理由要靠比较来建立。建议冻结同一版政策，由独立复核人员给六类案例标注预期和依据：仅静态检查、全量通过、记录缺失、记录矛盾、记录来自另一提交、输出仅引用他人说法。首先给 Python 规则、直接调用的 SWI-Prolog、经 MCP 调用的同一程序喂入相同事实，比较规则命中、解释完整度和耗时。然后从原文重新抽取事实，再做一次端到端比较。前后两轮的差异可以定位翻译错误，直接 SWI 与 MCP 的对照则可测出接口成本。

试点应分别报告违规漏判、正常输出误拦、缺证误放、转人工比例、可追溯到原文的命中比例及 p95 延迟，按场景族隔离开发样本与保留集。最值得扩展的场景，是同一项已核实的证据需要被多条规则共用、且复核者需要逐步解释结论的场景。当前已有一条规则的真实 MCP 通路验证；对 PoL 的判断质量和运行成本，仍需在上述对照中实测。[项目评测规范](https://github.com/naturaldao/NaturalDAO-2nd/blob/b075616aa4e59eeed59d2bd603bf5f6aa53f80fa/PoL-Governance/SPEC.md)
