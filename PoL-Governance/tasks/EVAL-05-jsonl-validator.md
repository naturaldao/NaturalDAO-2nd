# EVAL-05 离线 JSONL 校验器

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Codex | 待集成，离线校验入口已实现并通过合成数据冒烟验证 |

- 更新时间：2026-11-24 UTC+8
- 分支：`pol/EVAL-05/jsonl-validator`
- 起点 commit：`e7d1e714fb3abf206fd3ea5af08f1bb8005ded6a`
- 目标与交付路径：[数据契约](../benchmark/love_hate_behavior/SCHEMA.md)下的离线校验入口。
- 本次改动范围：校验 v0.2 JSONL 结构、记录引用、证据跨度及场景切分。
- 下一步：用合成样本进行离线回放和盲标交接设计。
- 环境 / 输出路径 / 资源预算：本地 Python，临时数据留在工作区，无模型调用。
- 数据版本与可用分区：仅用于验证工具的合成数据，无正式数据版本。

## 交付与验证

- 入口：[validate.py](../benchmark/love_hate_behavior/validate.py) · [用法](../benchmark/love_hate_behavior/SCHEMA.md#6-离线校验)。
- 合成数据完成 11 项 CLI 冒烟检查，覆盖五类记录混合、中文与 emoji 引文、外键、重复 ID、场景跨分区、失败回应、裁决独立性、时间格式、动作互斥和空输入。
- 校验直接读取当前主分支的 v0.2 schema。待 [PR #25](https://github.com/naturaldao/NaturalDAO-2nd/pull/25) 更新 schema 后，字段枚举随契约更新。
- 后续工程为模型运行器的离线回放和盲标导出。正式试跑依赖规则与手册冻结、模型配置、预算、人员和发布权限确认。
