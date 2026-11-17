# [VIS-01] 完整果蝇脑网络视觉呈现

| 领取人 / Agent | 状态 / 最近进展（Agent 更新） |
|---|---|
| Shenton YAN / OpenAI Codex | 待集成；905个真实神经元骨架与78脑区参考图谱已绘制、看图并核验，原模型结果保持原样。 |

- 更新时间：2026-11-17 Asia/Hong_Kong
- 分支：pol/VIS-01/whole-brain-network
- 起点 commit / 依赖分支与 commit：b47a430；已包含 EVAL-06 与 PR #15 的官方模型和图件。
- 目标与交付路径：Research/Brain/figures/；benchmark/fly_brain/official/
- 本次改动范围：根据用户反馈重新设计脑网络可视化；保留已有实验输出，使用真实坐标、连接或可核验神经形态。不创造生物解剖数据。
- 下一步：审阅神经形态主图与来源记录，通过 PR 纳入公共基线。
- 阻塞 / 需要谁帮助：无。
- 环境 / 输出路径 / 资源预算：D:/Codebase/PoL2-FlyVis-Official/brain-visual-refinement 独立 worktree；原 Python3.10 项目解释器，CPU 绘图；RAM 空闲约14GB、D盘空闲约240GB（启动快照）。先小预览，形态数据只按需要下载，保留用户其他环境与进程。
- 数据版本与可用分区：FlyWire v783 坐标、Eon a3db62f 官方连接表及已公开的1秒糖刺激输出；无需重新运行模型。

## 进展与交流

2026-11-17｜OpenAI Codex｜用户认为当前脑网络图仍不美观。原 PR #15 已合并，故从最新公共基线另开视觉修订分支。研究真实神经形态获取途径，并检查如何让真实连接清楚呈现。｜本任务分支｜先推领取记录，再制作预览。

## 交付或交接

- [神经形态主图及复算](../../Research/Brain/Morphology-View.md)：905个真实骨架，完整包含393个本次模拟放电神经元和512个空间分层背景样本，保留4862272条原始骨架线段；线段数不等于突触数。
- 背景为78个配准JFRC2参考脑区，非该模型标本的EM表面。数据按精确root ID取得，原始点、边和半径与缓存逐项核对；无合成分支、无重跑模型。17个已有实验数据/运行证据通过核验，二进制逐字节一致，JSON按仓库LF文本规范比较。
- 已打开PNG与PDF重渲染预览，确认无裁切；183×110mm、600dpi、嵌入Arial，SVG有8个可编辑文字对象。[导出核验](../../Research/Brain/figures/export-quality-20261117.json)与原保存结果检查通过；仓库总检查通过。
- 完整输入缓存约182MiB，仍在D:/Codebase/PoL2-FlyVis-Official/downloads/morphology-v783，未上传或删除。原四幅实验图继续保留；未采用的锚点直线连接预览留在本机runlogs中。
- OpenAI Codex实现、运行及AI交叉检查，不声称独立人工专家审核。
