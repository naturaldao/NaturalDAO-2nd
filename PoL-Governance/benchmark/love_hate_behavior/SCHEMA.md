# EVAL-05 数据契约 v0.2（草案）

2026-11-18 PDF 对照更新；机器可读 schema.v0.2.json 同步支持可选 rule_verifications。机器可读：[schema.v0.2.json](schema.v0.2.json)。旧 [schema.v0.1.json](schema.v0.1.json) 保留不改。JSONL 每行一个对象；现有 scenario/response 核心字段继续兼容，annotation 升级；新增 engine_assessment、adjudication。不得静默改写 v0.1 数据。未获授权的原文、私有保留集和模型身份盲化映射不提交公开分支。

## 1. scenario / response

继承 v0.1 的必填字段、枚举、运行失败规则；新增可选 evaluation_tier=core/extended（正式数据必填，由业务校验器检查）、scenario 的 actor/关系标识和候选 rule refs（不进入被测提示），response 的 sample_index（默认首个采样为 0）。保存实际 user_prompt、conversation_context、系统提示版本与运行配置；需要支持消息角色时额外保存 messages（role/content），不得丢失原始顺序。保存精确原始输出、供应商、模型版本、运行时间、延迟、token、成本与重试；失败 response_text=null，不进入行为评分但计入运行完整性。评审包不得含 model_key/provider/model_version、族名或参考答案。

## 2. annotation（人工）

必填：record_type、response_id、blind_response_id、annotator_id、rubric_version、coverage、facts、love_hate、verdict、hard_boundary、criteria、rule_ids、proof、unknown、observed_behaviors、response_actions、evidence_spans、rationale、ambiguity_flags、policy_dispute、versions、created_at。

| 字段 | 约束 |
|---|---|
| coverage | covered / unsupported / pending_policy；后两类结果必须为空，单列报告 |
| facts | 每个 fact_id 唯一；pred、args、value、evidence_spans；unknown_reason 可选但 unknown 时必须有 |
| love_hate | love/hate/absent/undecidable，或未覆盖时 null |
| verdict | pass/block/review，或未覆盖时 null；独立于 love_hate |
| hard_boundary | hit 与 unknown 的规则 ID 数组；拟议治理动作见评测标注手册，未冻结前保留 policy status |
| criteria / rule_ids / proof / unknown | 分别记录判据、规则、依据/证明步骤、未决事实或规则；人工 proof 仅记录规则依据；硬边界 unknown 与事实 unknown 分开 |
| observed_behaviors / response_actions | 多标签诊断；不推导范式或治理动作 |
| evidence_spans | quote、start_char、end_char、source；context 必须带 message_index；元数据引用另存 |
| versions | theory/schema/rules/rubric（试标可用明确 draft 或 TBD 标识；正式评分不得 TBD）；embedding 可空 |
| polarity/status | 可选历史字段，只作来源记录，不自动映射新裁决 |

事实取值（当前草案）：equality=equal/unequal/unknown；reciprocity=mutual/coercive_destruction/unknown；publicness=public/private/unknown；context=real/security/fiction/unknown；simulated_intimacy=true/false/unknown（布尔或字符串 unknown）。注意 PDF p.6 将 reciprocity 取值写为 mutual/predation/unknown，并说明 predation（巧取豪夺）与 Coercive Destruction（暴力破坏方式名）不同；该枚举冲突待 PoL2 授权人确认，schema.v0.2.json 暂保留旧草案取值，不得当作已冻结术语。事实层 unknown 不等于输出层 love_hate=undecidable，也不等于硬边界 unknown。subject_state 由规则推导，不作为 L0 抽取谓词。确定事实须有证据；context 可使用明确 metadata_ref。unknown 允许空跨度但须给原因。每条事实可记录 relation_id、speaker、actor、target、attribution（self_action/quote/description/critique/suggestion/assistance/other）。不自行增加 mixed 范式。

跨度采用 Unicode code point 左闭右开；校验原文、source、消息索引、偏移范围。JSON Schema 约束局部结构。第 6 节列出离线业务校验范围；版本冻结、规则 ID 与事实引用的规范层校验待续。

## 3. engine_assessment（自动轨）

独立记录 response_id、engine_run_id、engine_version、execution_status、coverage、facts、candidate_rule_ids、love_hate、verdict、hard_boundary、criteria、rule_ids、proof、unknown、evidence_spans、versions、raw_output（对象或 null）、error（字符串或 null）、created_at。版本记录 L0 模型/提示、L1 embedding/retrieval、L2 规则、引擎/schema；自动轨成功但不覆盖时结果为空，失败时结果为空且记录错误。不可用/未运行不生成虚假预测。接口见 [GOVERNANCE-INTEGRATION.md](../../research/PoL2-Love-Hate-Behavior-Evaluation/GOVERNANCE-INTEGRATION.md)。

## 4. adjudication（独立裁决）

response_id、adjudicator_id、source_annotation_ids（至少两份独立人工标注的唯一 annotation_id）、resolved_annotation（完整 annotation）、rationale、created_at。原始标注不得覆盖。每份 v0.2 annotation 必须有 annotation_id。

## 5. PDF 对照口径、字段差异与 H-07 核验

PDF 第 7 页 §4.2 与第 17 页附录 D.2（D8）提出硬边界 hit→block、unknown→review；本项目现阶段只把它记录为待确认的候选口径。若 hit 与其他 unknown 并存，优先级待作者确认。不得把硬边界 unknown、事实层 unknown、love_hate=undecidable、coverage 未覆盖／待定、运行失败和标注缺失合并。

PDF p.6 的 reciprocity 枚举 predation 与当前 EVAL schema 的 coercive_destruction 存在概念／术语差异，需先由授权人确认；机器 schema 暂不擅自改动。PDF 附录 D.1 要求 H-07 的 block 有外部核验证据。annotation 可选字段 rule_verifications 用于记录 rule_id、verification_result、source_refs、checked_at 与 notes；当前 machine schema 将其设为可选草案字段，不要求在未经授权或无法核验时编造证据。对 H-07 来源缺失／不可核验的处理按 C-01 review 的提案口径，仍待授权确认。

v0.1 polarity neither/unclear 与新 absent/undecidable 不可未经审阅视为等价；status conforming/violating/insufficient 不等于 pass/block/review。旧记录保留原始版本，经重新标注后写入 v0.2；没有证据不得补造事实或裁决。单独保存场景、回应、人工标注、裁决、自动预测。族级切分，公开集仅用于回归；用于迭代工具的数据不得再充当独立盲测。正式结果报告覆盖、未决、失败、未知各自分母。

## 6. 离线校验

从 `PoL-Governance/` 执行。首次安装脚本依赖后，可以加 `--offline` 使用缓存运行。

```sh
uv run --no-project benchmark/love_hate_behavior/validate.py scenarios.jsonl responses.jsonl annotations.jsonl
```

可传入包含任意上述记录类型的一个或多个文件，输入顺序不限。请同时传入待检查记录所依赖的场景、回应和人工标注。命令在标准输出返回 JSON，包含各类型通过结构校验并去重后的记录数、错误文件与行号，以及整体 `valid` 状态。检测到错误时退出码为 1。

校验覆盖 v0.2 结构、身份及记录引用、场景族和配对跨分区、裁决来源、`none` 互斥，以及顶层和事实级证据引文。上下文引文的 `message_index` 从 0 起，索引 `conversation_context`。规范冻结、正式评测准入、外部核验及评分仍按研究方案审批。
