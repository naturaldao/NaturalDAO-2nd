# 调查方法、核读范围与局限

## 1. 调查设计

调查日期及文献截止日期为2026-11-17（UTC+8）。本工作是围绕机制的结构化专题调研，采用主题检索、经典原始研究追踪、近年更新与相反证据核查。没有预注册检索协议，没有对全部数据库结果进行去重筛选，也不声称完成PRISMA系统综述或元分析。

范围包括：果蝇及线虫的小神经系统；蚂蚁个体导航与群体决策；细菌趋化、草履虫回避、喇叭虫层级行为、黏菌流动与记忆、变形细胞可兴奋网络。果蝇主要指黑腹果蝇，不把结果泛化到家蝇或全部昆虫。

交付清单记录47条领域来源，其中一条是喇叭虫论文勘误。数量按唯一DOI计，不是独立实验数，也不是检索命中数。下述写作流程参考文献单列，不计入47条。

## 2. 检索与原文获取

使用公开网页检索、Parallel Search/Fetch与Exa检索/抽取寻找出版者原始论文、PubMed、PMC、Europe PMC及作者学术托管稿。Parallel Research在本次调用中返回未授权，未产生可用深度研究报告；实际结论来自后续公开检索及原始文献阅读，没有将失败调用算作证据。

本次主检索实际使用的部分查询如下；这是可核对的检索片段，不是完整的穷尽日志：

```text
site.nature.com 2024 2025 2026 Drosophila brain connectome action selection descending neurons
site.nature.com connectome constrained networks predict neural activity Drosophila 2024
site.nature.com 2025 2026 fly brain walking whole brain emulation
Distributed control circuits brain-and-cord 2026 172433
site.cell.com male central nervous system connectome 2026 166000 2026.08.015
BANC distributed control circuits 2026
MaleCNS connectome sexual dimorphism 2026
Connectome simulations central pattern generator walking
Pugliese 2026 walking inhibitory excitatory circuit
```

蚂蚁、细胞及经典回路的并行主题核查，按物种、作者、论文题目与DOI进一步定位原始来源。复查时可用`sources.json`逐条DOI检索，直接打开记录的`accessed_url`，按`locator`核对对应命题；无需依赖搜索排序。

部分Nature页面直接访问跳转登录，部分PMC页面返回验证码，部分出版者页面受CDN限制。遇到此情况，使用同一原始论文的公开抽取、作者稿、原始摘要或Europe PMC正文；未把新闻评论替代成论文证据。不同入口的摘要、正文和出版年份可能有差别，按具体版本核对。例如A08的DOI中含2025，但正式记录是2026年。

没有把“搜索结果提到这篇论文”视为完整核验。各来源的`reading_scope`记录实际读到原始摘要、图说明或正文相关段落；未通读全文的记录不标为全文阅读。网络抽取可能来自缓存，访问日期是本次核读日期，不保证每页在当日完成了实时刷新。

## 3. 来源选择与证据处理

优先纳入能直接回答机制问题的原始研究，包括行为干预、电生理、成像、解剖重建与明确提出并检验机制的模型论文。新闻用于发现线索，不用于支撑正文科学结论。未核清的数量、无来源的能耗比和泛化智能分数不写入结论。

具体处理规则：

- 数量保留物种、性别、阶段、脑或中枢范围，以及细胞/神经元/突触/图边的计数区别。
- 观察、编码相关、干预、模型内必要充分性分别描述；不把一个层级提升为另一个层级。
- 模型解释按其假设限定。BANC的简化影响指标不是完整生理因果图；CPG的三细胞核主要是仿真机制，部分下降通路预测另有实测。
- 将生理适应、结构记忆、习惯化和联想学习分开，不由适应性行为推出意识。
- 核查争议与勘误：包含FoxP定位的相反研究E03、Stentor勘误C08c，以及蚂蚁最优整合的代理变量解释A04。
- 工程启发单列为本报告推论；不把现有NaturalDAO人工仿真当成生物机制验证。

## 4. 核读与审阅的实际状态

Codex分别对神经系统、蚂蚁与细胞主题进行并行机器辅助核查，再对完成的正文交叉审阅。审阅后收窄了证据积累所涉及的Kenyon细胞亚群，补充判别速度提升的准确率代价，并删除排他性过强的感知表述。

来源记录的`verification`统一为`AI-assisted source check; no independent human review`。它不等于人工核验签字、期刊审稿或独立实验复现。公开版本保留这一状态，不虚构人类审校者、伦理审批或研究作者身份。

提交前核对47个来源ID及引用锚、DOI重复、全部本地链接、公式分隔符及文档结构；仓库入口链接检查亦通过。47条DOI、题名和年份的元数据比对均匹配，其中46条由Crossref返回，一条E03遇限流后改用PLOS原始页面核实，未反复重试。逐项结果见[元数据核查记录](METADATA_CHECK.json)。

这些检查确认可追溯性、注册元数据和内部一致性，不证明每项科学结论无误；也没有逐一测试47个DOI出版者落地页的网络可用性。外部页面之后仍可能改变。文档不是新模型的评测交付，因此不把通过软件检查当作科学真实性证明。

## 5. 仍未解决的局限

本次选文以有代表性的可解释机制为主，存在数据库、语言、可访问性和研究物种偏差；未估计发表偏差。不同研究任务、样本与刺激条件异质，没有合并效应量。较新的连接组论文仍缺少充分的长期独立检验。

一部分细胞机制来源仅核读原始摘要，不能声称已重审其全部方法与原始数据；精确读取范围见每条来源。跨物种的统一状态空间表达式是解释工具，不是证明自然界共享同一算法。关于意识的问题只报告这些实验能够与不能确立什么，不作本体论结论。

## 6. 写作流程来源与材料权利

证据与不确定性记录参考了Scientific Writing技能。其流程出处为：Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. [arXiv:2609.00065](https://arxiv.org/abs/2609.00065)，[DOI](https://doi.org/10.48550/arXiv.2609.00065)。本次已读取arXiv题名、作者、摘要和版本信息；这是写作工具来源，不是生物学证据。

仅公开本次为报告生成的第一方文字、文献元数据与关系说明，不上传论文全文、原始生物数据或他人图像。第一方材料沿用仓库Proof of Love2声明，第三方引用保留原权利；不改变历史已有授权。
