# [EVAL-05] 果蝇连接模板与动态撤权

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Shenton YAN / OpenAI Codex | 待集成；两项公开合成评估各运行一次，代码、完整结果、图与负结果报告已交付。 |

- 更新时间：2026-11-17 Asia/Hong_Kong
- 分支：pol/EVAL-05/flybrain-revocation
- 起点 commit / 依赖分支与 commit：2ffcfe7d57d0387f944fda5e9f535309f321d2d5（origin/main）
- 目标与交付路径：PoL-Governance/benchmark/fly_brain/；Research/Brain/
- 本次改动范围：公开合成接口测试，以及双线索人工递归记忆的撤销/恢复实验。真实来源只指 FlyVis 平均连接模板；不称预训练模型或全脑复现。
- 下一步：审阅 [PR #14](https://github.com/naturaldao/NaturalDAO-2nd/pull/14)；先增加持续有效的 B 行动任务，再考虑官方模型或身体闭环。
- 阻塞 / 需要谁帮助：无。
- 环境 / 输出路径 / 资源预算：显式 Python 3.12.10、NumPy 2.5.3，CPU 单进程，预计 RAM < 1 GB；输出为本任务 results/，不覆盖旧结果。
- 数据版本与可用分区：FlyVis 0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa；自生成 train/calibration/dev/public evaluation，互不重叠的种子。无私有数据或私有保留集。

## 进展与交流

2026-11-17｜OpenAI Codex｜用户明确授权继续实验并上传本仓。已从最新 main 创建任务分支；独立方法审查正在核查选择性干预、数据泄漏与结构对照。｜本任务分支｜先推送领取记录，再执行扩展实验。

2026-11-17｜OpenAI Codex｜冻结协议与实验代码为 `981bb4b`；开发集已验证0.94收缩系统在预设窗口可解码双线索。审查后修正重连权重归属、配对噪声与指标命名，已记录开发版本；4项记忆机制与5项接口测试通过。公开评估还未运行。｜[冻结协议](../benchmark/fly_brain/PROTOCOL.md)｜推送冻结记录后开始公开eval。

## 交付或交接

- [协议与复算](../benchmark/fly_brain/README.md)、[中文结果卡](../../Research/Brain/Experiments/01-Revocation-and-State.md)、[公开接口结果](../benchmark/fly_brain/interface/results/eval-20261117/summary.csv)、[记忆逐种子结果](../benchmark/fly_brain/results/memory-eval-20261117/per_seed.csv)。
- 公开记录 `77304dc` 推送后各运行一次eval。接口1024场景：raw/physical/start-only违规9688/7127/1007，full与同规则generic均0，合法执行5527/5733。人工记忆12种子×3图：36模型均满足记忆前提；选择性状态干预降低A线性可解码性并保留B，但普通图可重现，固定主读出远期失败。
- 4项记忆机制测试、5项接口测试、最终source SHA与结果记录一致性检查通过；图已实际渲染检查。仓库总检查 `uv run --no-project --offline python tools/check.py` 通过（1055项调度测试，12项条件跳过；716本地链接、19仓库内跨目录链接）；另497入口链接通过。新增实验在提交 `b73d014` 的Windows/Linux GitHub CI均通过。PR #14未自动合并。
- 未测试：官方预训练FlyVis、真实全脑、身体闭环、B行动任务、非线性最强探针、原子动作期间撤权。没有神经层伦理/授权内化结论，没有果蝇图特异收益结论。
- AI辅助：OpenAI Codex进行实现、方法交叉审查与报告整理；未声称专家标注或独立人工裁定。
