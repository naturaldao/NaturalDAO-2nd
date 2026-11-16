# [EVAL-05] 果蝇连接模板与动态撤权

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Shenton YAN / OpenAI Codex | 进行中；已核验上游模板，正在冻结扩展实验协议。 |

- 更新时间：2026-11-17 Asia/Hong_Kong
- 分支：pol/EVAL-05/flybrain-revocation
- 起点 commit / 依赖分支与 commit：2ffcfe7d57d0387f944fda5e9f535309f321d2d5（origin/main）
- 目标与交付路径：PoL-Governance/benchmark/fly_brain/；Research/Brain/
- 本次改动范围：公开合成接口测试，以及双线索人工递归记忆的撤销/恢复实验。真实来源只指 FlyVis 平均连接模板；不称预训练模型或全脑复现。
- 下一步：先完成开发集冒烟与方法审查，提交冻结代码和协议，再运行公开保留评估。
- 阻塞 / 需要谁帮助：无。
- 环境 / 输出路径 / 资源预算：显式 Python 3.12.10、NumPy 2.5.3，CPU 单进程，预计 RAM < 1 GB；输出为本任务 results/，不覆盖旧结果。
- 数据版本与可用分区：FlyVis 0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa；自生成 train/calibration/dev/public evaluation，互不重叠的种子。无私有数据或私有保留集。

## 进展与交流

2026-11-17｜OpenAI Codex｜用户明确授权继续实验并上传本仓。已从最新 main 创建任务分支；独立方法审查正在核查选择性干预、数据泄漏与结构对照。｜本任务分支｜先推送领取记录，再执行扩展实验。

## 交付或交接

协议、结果卡、可复算代码和检查记录完成后在本页登记。零收益和负结果一并发布；上传任务分支并提交 PR，不直接合并 main。
