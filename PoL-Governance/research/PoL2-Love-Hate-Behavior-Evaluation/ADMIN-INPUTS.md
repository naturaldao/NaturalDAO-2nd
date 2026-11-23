# EVAL-05 管理员输入与依赖（v0.3）

更新于 2026-11-24。PoL2 作者或指定授权人提供规范依据，项目管理员决定试标范围、资源与发布权限。各项材料如何进入工作流程，见[工作推进表](WORKPLAN.md)。

## 1. 由 PoL2 作者或指定授权人提供/确认（G0）

| 项 | 所需材料 | 当前状态 |
|---|---|---|
| 理论基线 | docs/theory/爱2证明-v1.0.md 的授权版本、commit/hash，确认与主仓公开 PoL2/EAP/JUDGE/ontology 的优先级 | TBD_OWNER |
| 硬边界 | H-01 至 H-09 原文、适用主体/对象、触发条件、正反例、例外；逐条候选映射见 POL2-SOURCE-MAPPING.md | PDF 给出规则与示例；适用口径仍待冻结 |
| EAP 与事实 schema | 平等/互惠/公共、context、simulated_intimacy 的规范取值及操作依据、证据要求；尤其裁定 EVAL 草案 reciprocity=coercive_destruction 与 PDF p.6 predation 的差异 | [PR #25](https://github.com/naturaldao/NaturalDAO-2nd/pull/25) 采用 `predation`，主分支草案仍保留旧枚举。需发布冻结版本并确认历史记录处理。 |
| 输出口径 | love/hate/absent/undecidable 与 pass/block/review 的独立语义；确认 PDF 候选规则：硬边界 hit→block、unknown→review；确认普通 unknown、安保/虚构例外及 hit 与 unknown 并存优先级 | PR #25 记录依 PDF 采用 hit→block、unknown→review。并存优先级与例外仍待确认。 |
| 聚合/冲突 | 混合回应、多主体、多规则优先级、未覆盖与不确定处理；H-07 与 H-09 重叠计数；hit 与 unknown 并存时 verdict 优先级 | 待确认 |
| 证据与使用权限 | H-07 外部核验来源、证据阈值、核验失败记录；是否允许共享规则/事实 schema/接口及授权金标 | 待确认 |
| 自动引擎 | 已验证版本、实际命令或 Python 接口、支持范围、运行/数据权限、验证结果 | 尚未获得；不阻塞人工探索 |

参考：[Discussion #82](https://github.com/naturaldao/NaturalDAO/discussions/82) 及 2026-11-18 提供的混合治理 PDF。其映射见 [POL2-SOURCE-MAPPING.md](POL2-SOURCE-MAPPING.md)，探索案例见 [EXPLORATORY-CASE-CANDIDATES.md](EXPLORATORY-CASE-CANDIDATES.md)。PR #25 记录了本轮 PDF 优先的决定，仍待合并。正式评分需要附带出处和版本的可操作规则，以及独立人工标注与裁决。

## 2. 管理员需要决定的项目事项

| 项 | 请补充或确认的材料 |
|---|---|
| 目标及条件 | 首轮规则及场景覆盖表、统一系统提示、是否另设规则可见条件 |
| 语言与场景 | 确认先行试标的场景及配对；中文 6–8 族、每族 4 变体为现有规模建议 |
| 模型与预算 | 模型及精确版本、供应商、采样参数、重复次数、失败与重试口径、费用上限；现有建议为 3–5 个模型 |
| 评审资源 | 两位独立评审及裁决者、可用工时和预算、双盲交接与分歧处理约定 |
| 数据来源 | 授权合成探索场景优先；真实对话仅经授权/去标识；原始输出公开权明确 |
| 发布 | 明确可公开的场景、模型原文、标注和结果范围；确认外部复核、正式规模与保留集安排 |
| 私有保留 | 独立评测者库外保管、受控隔离禁网评测；不能发往外部 API 或公开仓库 |

## 3. 收齐材料后如何推进

先将已确认的规则、版本及例外记录到规则映射和手册，再由管理员确认首批授权场景与试标人员。按工作推进表保留独立试标、分歧及裁决证据。定义仍未决的情形继续做非评分探索；自动引擎材料可独立补齐。

管理员可仅确认项目事项，不必重新回答理论定义问题。
