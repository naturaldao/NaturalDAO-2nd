# [EVAL-06] 官方预训练视觉模型与完整果蝇全脑加载

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Shenton YAN / OpenAI Codex | 进行中；已下载并校验官方FlyVis权重，准备真实加载与全脑后端。 |

- 更新时间：2026-11-17 Asia/Hong_Kong
- 分支：pol/EVAL-06/flyvis-official-weights
- 起点 commit / 依赖分支与 commit：0024aa5（副仓 origin/main；包含已合并 EVAL-05）
- 目标与交付路径：benchmark/fly_brain/official/；Research/Brain/
- 本次改动范围：严格加载官方参数，先复现发布模型的原始功能，再做明确标注的PoL2适配；另核验Eon公开全脑后端与连接数据，不能用类型代理替代。
- 下一步：逐张量校验官方checkpoint，运行完整空间视觉网络的原始刺激；下载Eon全脑源代码与数据并检查实际运行入口。
- 阻塞 / 需要谁帮助：无。
- 环境 / 输出路径 / 资源预算：D:/Codebase/PoL2-FlyVis-Official独立工作区；Python3.10专用venv，只读复用已验证CUDA torch库；不改已有项目环境。RTX5070空闲约9.7GB，RAM空闲约15GB，D盘空闲约260GB（本轮启动快照）。先单批量短刺激，测峰值后扩大。
- 数据版本与可用分区：FlyVis源码0a69fa2fc8e1bfe1d837d722c252ab5f5d6fcbfa；官方results_pretrained_models.zip 3417042字节，SHA256 71c78d4070556a536b13b23ee3139cd2788aa2a9d07d430a223b4edead281db1。全脑数据版本另记。

## 进展与交流

2026-11-17｜OpenAI Codex｜用户明确要求加载官方权重，并允许下载较大的完整果蝇全脑数据。官方视觉权重已下载且匹配官方下载器校验值。大文件放独立D盘目录，实验后用户可单独清理，代码/校验/结果保留。｜本任务分支｜先推领取记录，再运行官方模型。

## 交付或交接

须提交加载manifest、参数逐项验证、实际forward证据、原始功能复现结果、活动图和资源测量。官方权重、源码与全脑数据保留各自许可；仅登记下载链接/哈希，不上传本机缓存或整套大数据。
