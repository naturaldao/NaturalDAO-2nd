# 两套 Prolog 接口和 Jev 分别能检验什么

## 同一条动物分类题

“鹰有毛皮吗？”是 Euclid-MCP 作者的小规模测试 Q3。题目给出鹰属于猛禽、猛禽属于鸟等事实，属性沿类别关系继承。第一个检查点是翻译后的知识库有没有擅加事实，第二个才是从这些事实能否推出毛皮属性。11 月 18 日本仓的两次版本复现都记录到模型添加了 `is_a(eagle, mammal)`，于是引擎沿哺乳动物的规则推出了毛皮。读者能沿着证明定位这条错误前提。仅看求解是否成功，会把它误判为事实。[作者的五道小题](https://github.com/Euclid-BG/Euclid-MCP/blob/aed10179131fc990739f5d69b0584f4a065f0faa/benchmarks/reasoning_benchmark.py) · [本仓逐题原始输出](../../Euclid-MCP-复现/benchmarks-origin.jsonl)

| 对象 | 交给它什么 | 能核对哪一层 |
|---|---|---|
| PrologMCP | SWI-Prolog 程序文本和查询。论文表 1 用 `consult_text` 建会话，本次固定实现改名为 `create_session`，随后均以 `run_goal` 查询 | 可以检查子句、在同一会话测试或替换单个谓词、跟踪目标。适合检查“按这版转写能否推出结论”。[作者论文表 1](https://arxiv.org/html/2606.14935v2#S3.T1) · [本次固定实现的接口说明](https://github.com/dicelab-rhul/PrologMCP/blob/4ae536fd9b1cef8419d1798b5d4cb1569cba3cae/README.md#create_session) |
| Euclid-MCP（论文 v2） | 用 Euclid-IR 写下事实、规则和目标，由服务端编译为 SWI-Prolog | 通过 `check_kb` 检查知识库、`reason` 返回绑定和证明、`diagnose` 解释结果、`what_if` 比较假设变动前后。可让第二套规则表达对同一例题作交叉核对。两者共享 SWI 引擎，错误前提也可能共享。[作者论文 §3.4](https://arxiv.org/html/2607.21412v2#S3.SS4) · [作者仓库](https://github.com/Euclid-BG/Euclid-MCP) |
| Jev | TypeSafe 的 System One 判断模型，读入状态与限定问题。Choice 返回候选选择，Score 按量表评分，Noul 返回“是”的概率 | 可以另行读取原始证据，指出转写与原文的潜在分歧。概率属于模型判断，无法充当签名、授权或逻辑证明。项目的既有综述主张记录输出、本地校准、允许不确定，由人处理有后果的决定。[TypeSafe 官方接口](https://docs.typesafe.ai/introduction) · [项目综述](../../../../PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey/README.md) |

## 论文结果与本仓复现

Euclid 论文表 2 的五道短题涵盖家谱、动物属性和角色权限，表 3 的五道题则查询 1,000 名合成用户的角色、权限继承和直接授权。两张表都只有五道题。以下数字沿用论文与 2026 年 11 月 18 日已经归档的复现记录，本次核对来源时未重新调用模型。[论文 §5.2](https://arxiv.org/html/2607.21412v2#S5.SS2) · [复现方法与逐题对照](../../Euclid-MCP-复现/README.md)

| 测试 | 论文的 Llama 3.1 8B 单答 / 8B + Euclid | 本仓基准首发版本的单答 / 接工具 |
|---|---:|---:|
| 小规模 | 5/5、5/5 | 5/5、4/5 |
| 1,000 用户 RBAC | 2/5、5/5 | 2/5、5/5 |

RBAC 的对照还改变了可见信息。单答提示略去了 20 条直接授权的明细，而工具可查询完整知识库，因此分差同时受到信息完整性和求解方式影响。同期代码的 5 次工具请求还因参数上限不匹配而在求解前被拒绝。调整上限后重放得到首发版的五个答案，这是保存查询的重放结果。Q1 的 32 条证明只对应 31 名不同用户，PoL 若涉及计数，应先确定计数对象。论文的云模型对照组因模型退役未在本仓复跑。[作者权限基准](https://github.com/Euclid-BG/Euclid-MCP/blob/aed10179131fc990739f5d69b0584f4a065f0faa/benchmarks/rbac_1000.py) · [同期原始输出](../../Euclid-MCP-复现/benchmarks.jsonl) · [重放](../../Euclid-MCP-复现/replay.jsonl)

PoL 的交叉核对可以分两步。先给两个规则引擎同一份经核对的快照，保留各自的规则表达，与独立标注的预期结果比对。再让独立读者或获准使用的 Jev 读取原始材料，检查某个候选事实是否有出处。两个引擎得出相同结论只能说明给定规则在该例上结果一致。若两个系统都继承了“鹰属于哺乳动物”这样的录入错误，一致的证明仍然会错。本文没有执行 Jev 调用，因而没有三工具联合实测成绩。
