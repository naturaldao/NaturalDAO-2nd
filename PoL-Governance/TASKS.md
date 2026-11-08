# 任务表

本表是 [NaturalDAO-2nd](https://github.com/naturaldao/NaturalDAO-2nd) 的研究任务目录。领取方式见 [AGENTS](AGENTS.md)，实时进度以副仓任务分支里的任务页为准。[浏览任务分支](https://github.com/naturaldao/NaturalDAO-2nd/branches)

## 刷新看板

在副仓克隆的根目录执行以下命令。先用 `git remote get-url origin` 确认 `origin` 指向 `naturaldao/NaturalDAO-2nd`。

```sh
git fetch --prune origin "refs/heads/main:refs/remotes/origin/main" "refs/heads/pol/*:refs/remotes/origin/pol/*"
python PoL-Governance/tools/board.py --remote origin
```

如果 `origin` 是自己的 fork，可添加副仓为 `upstream`（`git remote add upstream https://github.com/naturaldao/NaturalDAO-2nd.git`），再把上述命令中的 `origin` 都换成 `upstream`。任务分支尚未合并时，也可以协作并更新任务页。

看板的 `status` 来自任务页。`tip_in_baseline` 单独表示分支头提交是否在已拉取的默认分支历史中。找不到基线时返回 `null`。压缩合并或变基会生成新提交，原分支头可能仍显示 `false`，此时通过 PR 核对是否已集成。

看板显示 `task_file_missing` 时，先到对应分支核对任务页，再确认是否有人领取。

## 任务目录

| ID | 做什么 | 交付入口 |
|---|---|---|
| DATA-01 | 独立试标注与分歧整理 | [数据索引](datasets/README.md) · [标注工具](benchmark/annotations.py) |
| DATA-02 | 生成正式 PoL 数据与 70/20/5/5 划分 | [PoL2 数据集](datasets/pol2/README.md) |
| DATA-03 | 通用决策底座：10k+ 覆盖全面问题集、HF 抓取转换与 Jev 就绪作答 harness | [通用决策数据](datasets/general/README.md) |
| MODEL-01 | 深入调研并更新候选清单 | [候选模型清单](models/CATALOG.md) |
| MODEL-02 | 自选模型适配与控制遗忘（可多队） | [模型目录](models/README.md) · [结果索引](results/README.md) |
| EVAL-01 | 正式 benchmark、通用及主流安全对照 | [评测工具](benchmark/README.md) · [结果索引](results/README.md) |
| EVAL-02 | PoL2 × 类型决策模型的具身任务执行验证（Kev + VirtualHome 单场景闭环；16 案例三条件长度匹配筛查，扩展可执行基准） | [具身评测](benchmark/embodied_reasoning/README.md) · [先导报告](../Research/Embodied/03-策略与决策实验/PoL2具身推理过程初步验证.md) |
| EVAL-03 | 完整 PoL2 理论内在化验证：建立全章节、可失败的挑战评测与训练对照 | [PoL2 评测](benchmark/pol2/README.md) · [挑战集生成先导](../Research/Embodied/02-实验设计与审计/PoL2完整理论内在化挑战集生成质量先导.md) |
| EVAL-04 | 按知识类型构建独立评测任务：概念/关系、公理/命题、爱语、明确规则、研究者解释；比较闭卷与理论可见条件 | [分类型知识评测](benchmark/pol2/typed_knowledge/) · [先导报告](../Research/Embodied/02-实验设计与审计/PoL2分类型知识评测先导.md) |
| APP-01 | 插件接入、试运行与端到端验证 | [接入与试运行](integrations/README.md) |
| OPS-01 | 协作工具、任务看板与贡献导航维护 | [协作工具](tools/) · [贡献指南](../CONTRIBUTING.md) |
| LIT-01 | Jev 类型化决策模型文献综述，对照 PoL2 治理条款 | [综述与复现](research/PoL2-Jev-Typed-Literature-Survey/README.md) |
| GOV-01 | PoL2 × DAO 治理机制实验室：条款落地、模拟、反事实与基线筛查评测 | [治理机制实验室](research/PoL2-DAO-Governance-Lab/README.md) |

DATA-01 可由两名独立标注者分别领取后缀 A/B，完成前不互看标签。MODEL-02 用模型名后缀区分实验。模型调研、数据准备、接口开发可并行；不同数据版本的结果分开比较。

新任务直接加一行。暂停/转交/完成更新任务分支里的任务页；本表仅在增加/调整任务范围时修改。日常进度不用等合并。
