# EVAL-05 管理员输入与依赖（v0.3）

2026-11-19。项目负责人确认：EVAL-05 草案与混合治理 PDF 冲突时以 PDF 为准。项目采用 PoL2 作者认可的规范，管理员负责项目运行，不要求管理员提出新的理论定义。

## 1. 由 PoL2 作者或指定授权人提供/确认（G0）

| 项 | 所需材料 | 当前状态 |
|---|---|---|
| 理论基线 | docs/theory/爱2证明-v1.0.md 的授权版本、commit/hash，确认与主仓公开 PoL2/EAP/JUDGE/ontology 的优先级 | TBD_OWNER |
| 硬边界 | H-01 至 H-09 原文、适用主体/对象、触发条件、正反例、例外；逐条候选映射见 POL2-SOURCE-MAPPING.md | PDF 给出规则与示例；适用口径仍待冻结 |
| EAP 与事实 schema | 平等/互惠/公共、context、simulated_intimacy 的规范取值及操作依据、证据要求；reciprocity 本轮按 PDF p.6 采用 mutual/predation/unknown | 已按 PDF 统一；其余取值与操作证据待确认 |
| 输出口径 | love/hate/absent/undecidable 与 pass/block/review 的独立语义；按 PDF 优先级采用硬边界 hit→block、unknown→review；确认普通 unknown、安保/虚构例外及 hit 与 unknown 并存优先级 | 来源优先级已确认，按 PDF 执行；细节待确认 |
| 聚合/冲突 | 混合回应、多主体、多规则优先级、未覆盖与不确定处理；H-07 与 H-09 重叠计数；hit 与 unknown 并存时 verdict 优先级 | 待确认 |
| 证据与使用权限 | H-07 外部核验来源、证据阈值、核验失败记录；是否允许共享规则/事实 schema/接口及授权金标 | 待确认 |
| 自动引擎 | 已验证版本、实际命令或 Python 接口、支持范围、运行/数据权限、验证结果 | 尚未获得；不阻塞人工探索 |

参考：[Discussion #82](https://github.com/naturaldao/NaturalDAO/discussions/82) 及 2026-11-18 提供的混合治理 PDF。其映射见 [POL2-SOURCE-MAPPING.md](POL2-SOURCE-MAPPING.md)，探索案例见 [EXPLORATORY-CASE-CANDIDATES.md](EXPLORATORY-CASE-CANDIDATES.md)。项目负责人已确认 EVAL-05 与混合治理 PDF 冲突时以 PDF 为准；仍须确认 PDF 版本标识、授权范围及规则操作细节，未冻结前不形成正式金标。

## 2. 管理员需要决定的项目事项

| 项 | 建议（待批准） |
|---|---|
| 目标及条件 | 主流模型自然行为基线；可选规则可见条件独立报告 |
| 语言与场景 | 中文先行，6–8 个场景族，每族 4 变体；core/extended 分层 |
| 模型与预算 | 3–5 个可用模型，明确精确版本、API 供应商、费用上限及重复次数 |
| 评审资源 | 两位独立评审、裁决者、标注工时及预算 |
| 数据来源 | 授权合成探索场景优先；真实对话仅经授权/去标识；原始输出公开权明确 |
| 发布 | 先 pilot 报告；正式规模、保留集安排、外部复核、公开范围待定 |
| 私有保留 | 独立评测者库外保管、受控隔离禁网评测；不能发往外部 API 或公开仓库 |

## 3. 下一步

先请求授权规范材料并锁定可操作 core；与此同时可以准备无参考答案的候选场景和评测脚手架。未决规范不由工程侧填补，暂作探索/不评分。人工试标和基线不等待完整混合引擎；自动对接另设门槛。

管理员可仅确认项目事项，不必重新回答理论定义问题。
