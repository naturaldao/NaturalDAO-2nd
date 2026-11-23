# EVAL-05 离线 JSONL 校验器

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Codex | 进行中，搭建独立的 EVAL-05 草案数据校验器 |

- 更新时间：2026-11-24 UTC+8
- 分支：`pol/EVAL-05/jsonl-validator`
- 起点 commit：`e7d1e714fb3abf206fd3ea5af08f1bb8005ded6a`
- 目标与交付路径：[数据契约](../benchmark/love_hate_behavior/SCHEMA.md)下的离线校验入口。
- 本次改动范围：校验 v0.2 JSONL 结构、记录引用、证据跨度及场景切分。
- 下一步：用公开合成样本验证通过和失败路径。
- 环境 / 输出路径 / 资源预算：本地 Python，临时数据留在工作区，无模型调用。
- 数据版本与可用分区：仅用于验证工具的合成数据，无正式数据版本。
