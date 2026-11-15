# EVAL-05 数据契约草案

状态：draft-0.1，等待理论和标签冻结。文件结构先支持试标与运行追溯；枚举须随 rubric 版本冻结。只保存有权公开的数据。私有保留样本及可反推样本的信息不得进入公开分支。

数据按 UTF-8 JSONL 存储，每行一个对象。机器可读结构见 schema.v0.1.json；每行须带 record_type=\"scenario\"、\"response\" 或 \"annotation\"。该 schema 仍是草案。正式数据路径、划分和许可在数据门通过后确定。

## 1. 情境 scenarios.jsonl

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| scenario_id | string | 是 | 稳定唯一 ID |
| family_id | string | 是 | 场景族，用于族级切分和统计 |
| pair_id | string/null | 是 | 成对对照 ID |
| variant | string/null | 是 | 配对成员标识，如 a/b |
| changed_fact | string/null | 是 | 唯一关键事实变化 |
| language | string | 是 | 语言标记 |
| theme | string | 是 | 管理员冻结的主题键 |
| user_prompt | string | 是 | 实际提交给模型的用户消息 |
| conversation_context | string[] | 是 | 按时间排列的必要上下文 |
| policy_context | object/null | 是 | 可见规则条件的政策文本；基线为空 |
| source_refs | string[] | 是 | PoL2 条款锚点，不含参考标签 |
| provenance | object | 是 | 来源、改写人、版本、日期与许可状态 |
| split | enum | 是 | draft / pilot_public / public_test / private_holdout |

场景和提示不得包含参考标签、预期答案、模型身份或泄露场景族的文件名。

## 2. 模型回应 responses.jsonl

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| response_id | string | 是 | 唯一回应 ID |
| scenario_id | string | 是 | 对应情境 |
| model_key | string | 是 | 稳定内部代号；评审前移除映射 |
| provider | string | 是 | 供应方或本地引擎 |
| model_version | string | 是 | 精确版本、revision 或可获得的 API 标识 |
| system_prompt_version | string | 是 | 提示词版本或 hash |
| condition | string | 是 | baseline / pol2_rule_visible / other |
| generation_config | object | 是 | temperature、top_p、max_tokens 等配置 |
| run_at | string | 是 | ISO 8601 时间 |
| execution_status | enum | 是 | ok / timeout / error / invalid |
| response_text | string/null | 是 | 原始回应；失败时为空 |
| latency_ms | number/null | 是 | 客户端端到端耗时 |
| input_tokens | integer/null | 是 | 可取得时记录 |
| output_tokens | integer/null | 是 | 可取得时记录 |
| cost | number/null | 是 | 可可靠计算时记录并注明货币 |
| retry_count | integer | 是 | 重试次数；失败不得静默丢弃 |

## 3. 人工标注 annotations.jsonl

| 字段 | 类型 | 必需 | 说明 |
|---|---|---:|---|
| response_id | string | 是 | 对应一条回应 |
| blind_response_id | string | 是 | 去标识评审 ID |
| annotator_id | string | 是 | 评审代号 |
| rubric_version | string | 是 | 标注手册版本 |
| polarity | enum | 是 | love / hate / neither / unclear；待理论门冻结 |
| status | enum | 是 | conforming / violating / insufficient |
| observed_behaviors | string[] | 是 | 实际观察到的行为，可为空 |
| response_actions | string[] | 是 | help / refuse / clarify / repair / refer / other / none |
| evidence_spans | object[] | 是 | 回应片段及起止字符位置 |
| rationale | string | 是 | 简短判断依据及 PoL2 条款 |
| ambiguity_flags | string[] | 是 | 争议或待审边界；无则为空 |
| policy_dispute | boolean | 是 | 是否涉及理论或规则分歧 |
| created_at | string | 是 | ISO 8601 时间 |

双人原始标注各存一行，不互相覆盖。adjudications.jsonl 单独保存两份原始标签、裁决标签与理由、裁决者和 rubric 版本。模型身份映射表及私有保留材料不进入公开评审包。

## 4. 数据质量规则

- 成对情境共享 pair_id；changed_fact 指出单一变化；其余情节尽量保持一致。
- 同一场景族及翻译、改写、反事实版本不得跨数据分区。
- 评审输入不包含模型身份、场景族、参考标签或参考答案。
- 每个行为标签必须有回应证据；无证据推断不得支撑标签。
- polarity、status、行为标签和回应行动不得互相推导或合成单一分数。
- 失败回应计入运行完整性统计，不静默删除。
- 机器评审不得称作人工金标准。
- 本草案不是最终 JSON Schema；待理论和 rubric 冻结后再实现校验器与评分器。
