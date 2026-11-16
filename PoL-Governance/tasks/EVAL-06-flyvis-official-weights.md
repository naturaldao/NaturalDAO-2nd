# [EVAL-06] 官方预训练视觉模型与完整果蝇全脑加载

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Shenton YAN / OpenAI Codex | 待集成；官方视觉权重与完整全脑真实运行，原始功能、PoL2外部适配及空间活动图已交付。 |

- 更新时间：2026-11-17 Asia/Hong_Kong
- 分支：pol/EVAL-06/flyvis-official-weights
- 起点 commit / 依赖分支与 commit：0024aa5（副仓 origin/main；包含已合并 EVAL-05）
- 目标与交付路径：benchmark/fly_brain/official/；Research/Brain/
- 本次改动范围：严格加载官方参数，先复现发布模型的原始功能，再做明确标注的PoL2适配；另核验Eon公开全脑后端与连接数据，不能用类型代理替代。
- 下一步：审阅结果与运行记录；在更多配对种子/任务上评估，不把外部门控称为神经内化或身体行为。
- 阻塞 / 需要谁帮助：无。
- 环境 / 输出路径 / 资源预算：D:/Codebase/PoL2-FlyVis-Official独立工作区；Python3.10专用venv，只读复用已验证CUDA torch库；不改已有项目环境。RTX5070空闲约9.7GB，RAM空闲约15GB，D盘空闲约260GB（本轮启动快照）。先单批量短刺激，测峰值后扩大。
- 数据版本与可用分区：FlyVis源码0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa；官方results_pretrained_models.zip 3417042字节，SHA256 71c78d4070556a536b13b23ee3139cd2788aa2a9d07d430a223b4edead281db1。全脑数据版本另记。

## 进展与交流

2026-11-17｜OpenAI Codex｜用户明确要求加载官方权重，并允许下载较大的完整果蝇全脑数据。官方视觉权重已下载且匹配官方下载器校验值。大文件放独立D盘目录，实验后用户可单独清理，代码/校验/结果保留。｜本任务分支｜先推领取记录，再运行官方模型。

## 交付或交接

- [结果报告](../../Research/Brain/Official-Models-Results-20261117.md)、[下载与复算](../benchmark/fly_brain/official/README.md)、[官方视觉加载manifest](../benchmark/fly_brain/official/results/flyvis-moving-edge-20261117/manifest.json)、[全脑在线适配manifest](../benchmark/fly_brain/official/results/eon-pol2-20261117-v3/manifest.json)。
- FlyVis官方5组checkpoint逐张量相等，extent15完整45669节点/1513231边；50次实际forward、16660积分帧，24移动边缘刺激，T4c ON90峰值1.032089>ON270 .024330，弱方向选择与角度偏差保留。
- Eon全脑138639神经元/15091983权重，原始parquet独立SciPy构造CSR与官方缓存逐项精确一致。原CLI 1秒17520spikes，MN9左右104/65；PoL2配对2条神经轨迹共20000forward，输入停后8残留MN9 spikes，在线虚拟输出门0未授权请求。无身体控制、无内化结论。
- 真FlyWire v783坐标按ID匹配138639/138639，图为首个人工锚点非胞体或形态mesh。保留原CC BY-NC许可、原模型GPL及MIT。
- 验证：GPU forward/backward/optimizer烟测通过；公开结果检查脚本通过；v2/v3全部保存的神经轨迹和全神经元计数一致；独立AI agent代码/数据审查通过。仓库总检查通过（758本地链接、23跨目录链接）；图已实际打开查看。初次HDF5/稀疏inference_mode失败与修正全部保留。
- 大输入、虚拟环境与模型缓存留D盘独立目录，未删除；不会上传到Git。仅发布可复算代码、来源/哈希、紧凑输出和图。
- AI辅助：OpenAI Codex实现、运行和交叉检查，未声称独立人工专家审核。
