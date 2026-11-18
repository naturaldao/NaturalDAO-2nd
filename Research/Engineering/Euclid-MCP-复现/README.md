# Euclid-MCP 论文实验复现

2026 年 11 月 18 日复跑。[论文 v2](https://arxiv.org/abs/2607.21412v2) · [中文全文翻译](../Euclid-MCP_中文全文翻译.md) · [用户指定的代码仓库](https://github.com/shentonyan/Euclid-MCP)

在 1,000 用户 RBAC 基准上，首次发布基准的代码重现了表 3 的本地模型得分：Llama 3.1 8B 单独回答为 **2/5**，接入 Euclid 为 **5/5**。小规模基准上，8B 单独回答为 **5/5**，接入 Euclid 为 **4/5**。第 4 节的合规案例也有若干结果与论文不同。

## 两个代码版本

- [论文 v2 同期版本 aed1017](https://github.com/shentonyan/Euclid-MCP/tree/aed10179131fc990739f5d69b0584f4a065f0faa)，0.2.0，2026-08-11。按论文第 3.5 节逐次启动 SWI-Prolog 的描述选择；作者实际出表时的提交未知。先运行第 4 节及表 2、表 3，保存原始输出。
- [基准首次发布版本 dd51788](https://github.com/shentonyan/Euclid-MCP/tree/dd5178829100ed417fd90e69621292b49d7d869b)，0.1.0，2026-07-08。同期版本遇到下述参数错误后，再从该历史版本独立运行两张表的 A、C 条件。两个版本均使用各自原有的提示、模型调用、推理函数和评分器。每道题每个条件每版本运行一次。

## 表 2、表 3 的实测结果

A 为 `llama3.1:8b`，C 为同一模型加 Euclid。每格按 Q1 至 Q5 排列。表 3 的数值题沿用上游自动提取的答案。

| 基准 | 条件 | 论文正确数 | 基准首次发布版逐题答案 | 实测正确数 | 论文同期版 |
|---|---|---:|---|---:|---|
| 表 2，小规模 | A | 5/5 | 是、是、否、是、否 | 5/5 | 5/5 |
| 表 2，小规模 | C | 5/5 | 是、是、是、是、否 | 4/5 | 4/5 |
| 表 3，RBAC | A | 2/5 | 1、是、100、否、是 | 2/5 | 2/5 |
| 表 3，RBAC | C | 5/5 | 31、是、103、是、是 | 5/5 | 5 次参数错误 |

**条件 B 未复跑。** 论文使用 `qwen3-coder:480b-cloud`，表 2 报告 5/5，表 3 报告 2/5。实测原 Ollama 标签的聊天接口返回 HTTP 410，提示模型已退役。两张表中 B 的正确率、耗时和 token 数均只可引用论文值。

**小规模 Q3 的错误来自事实录入。** 两个版本的 C 都把鹰归入哺乳动物。在本次输出中，模型额外写入 `is_a(eagle, mammal)`，随后引擎据此推出鹰有毛皮。证明可以检查，输入事实仍需核验。

**表 3 有一处版本兼容问题。** 基准传入 `max_solutions=2000`，同期服务器上限为 1000。五次请求均在求解前被拒绝，模型实际生成的五条查询已保留。仅将求解上限改为 1000，逐条重放这些查询，得到 31、是、103、是、是；其中 Q1 有 32 条证明，按用户去重后为 31 人。该重放未再次调用模型，单独存档。[原始运行](benchmarks.jsonl) · [重放结果](replay.jsonl) · [历史版本端到端运行](benchmarks-origin.jsonl)

**输入条件影响表 3 的解释。** A 的提示给出角色区间、权限和“另有 20 条直接授权”，省略这 20 条授权的具体对象；C 的求解器读取完整授权。Q1、Q3、Q5 均涉及这些明细。代码实际生成 1,040 条事实，含 1,000 个用户角色、20 条直接授权、16 条基础权限和 4 条继承关系，另有 4 条规则。论文列为 1,053 条事实、17 项基础权限。Q1 还有评分差异：同期版 A 的回答以 `ANSWER: 30` 结尾，上游正则提取了推理步骤编号 1；两者对真值 31 均判错。由此，表 3 支持完整知识库下的精确查询，但无法单独量化在等量信息条件下两种推理方式的差距。[基准输入与评分代码](https://github.com/shentonyan/Euclid-MCP/blob/aed10179131fc990739f5d69b0584f4a065f0faa/benchmarks/rbac_1000.py)

### 延迟与 token

各单元格为五题平均墙钟毫秒及平均输入/输出 token。计时沿用上游代码，C 包含模型调用与引擎处理。同期版表 2 A 的第一题含冷启动（108,250 ms），同期版表 3 C 的时间是返回错误所需的时间。历史版在模型已加载后运行。不同机器、模型加载状态和服务开销限制了延迟比较。

| 表与条件 | 论文 ms；入/出 | 基准首次发布版 ms；入/出 | 同期版 ms；入/出 |
|---|---|---|---|
| 表 2 A | 4772；131/118 | 3331；130.8/114.8 | 24222；130.8/108.8 |
| 表 2 C | 2542；254/46 | 2697；254.2/47.8 | 2697；254.2/47.8 |
| 表 3 A | 6966；386/165 | 3519；386/133.6 | 3584；386/140.2 |
| 表 3 C | 963；421/12 | 2319；421.4/12.0 | 2256（参数错误）；421.4/12.0 |

## 第 4 节合规案例

同期版自带小型数据（30 用户、50 资源、577 行数据事实）和大型数据（200 用户、300 资源、3,869 行数据事实）。均加载示例指定的标准与策略文件。每套运行 10 个查询、3 个诊断和 3 个反事实，最大深度 30，每个查询最多 50 个解。下表查询行列出返回解数，同一对象可能对应多条证明。[32 条实测记录](cases.jsonl) · [上游用例及预期](https://github.com/shentonyan/Euclid-MCP/tree/aed10179131fc990739f5d69b0584f4a065f0faa/examples/07_it_security_compliance)

| 案例 | 小型 | 大型 | 对照说明 |
|---|---:|---:|---|
| Q1 管理服务器 | 0 | 0 | 论文称成立。示例数据没有用户 user_0005，上游 README 也预期为空 |
| Q2 可部署到生产 | 5 | 44 | 返回绑定的用户 |
| Q3 可访问 secret 资源 | 30 | 50 | 大型达到返回上限 |
| Q4 tech_lead 可部署到 golden | 2 | 4 | 返回角色与权限同时满足的绑定 |
| Q5 超过 90 天未登录 | 4 | 17 | 返回匹配记录 |
| Q6 职责分离违规 | 0 | 0 | 论文为 2 人和 11 人，上游 README 预期为空 |
| Q7 未加密生产资源 | 2 | 10 | 两套均能找到资源 |
| Q8 实习生可写代码 | 0 | 0 | 符合论文空集预期 |
| Q9 权限数超过 15 | 0 | 0 | 查询未返回解 |
| Q10 未加密生产 S3 | 0 | 1 | 大型返回一个绑定 |
| Q11 解释管理权限 | 成立 | 成立 | 证明含 eng_0008 的 sysadmin 角色及对应授权 |
| Q12 诊断部署权限 | 不成立 | 不成立 | 返回通用的规则条件检查提示 |
| Q13 给出部署所需条件 | 未确定 | 未确定 | 引擎未给出论文所述的具体角色建议 |
| W1 晋升至 senior_dev | 0→0 | 0→0 | 论文预期晋升后成功。公开策略给 tech_lead 部署权限，senior_dev 的权限表和上游继承链均无该权限 |
| W2 增加加密生产数据库 | 0→1 | 0→1 | 新资源 new_db 出现在结果中 |
| W3 增加 sysadmin 角色 | 0→1 | 0→1 | 新的管理权限成立 |

## 重跑方法

本次使用 Windows 11 Pro、i7-14700KF、RTX 5070、Python 3.12.10、SWI-Prolog 10.0.2 和 Ollama 0.34.2。模型为 Q4_K_M，Ollama 摘要 `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`。本地服务上下文 1024，KV 缓存 q8_0，开启 Flash Attention，服务并发槽位 4；本脚本顺序发送请求。上游温度为 0，未指定随机种子。论文第 5.4 节为定性 RAG 对照，无对应实测得分。

以下 PowerShell 命令从本报告所在目录执行。准备好 Git、uv、Ollama 和可从 PATH 调用的 swipl；确保 Ollama 在本机默认端口 11434 提供服务。输出用新文件名，避免覆盖归档数据。

```powershell
$report = (Get-Location).Path
$env:PYTHONUTF8 = '1'
$env:NO_PROXY = 'localhost,127.0.0.1'
ollama pull llama3.1:8b
git clone https://github.com/shentonyan/Euclid-MCP euclid-src
Set-Location euclid-src
git checkout --detach aed10179131fc990739f5d69b0584f4a065f0faa
uv sync --frozen --python 3.12
uv pip install requests==2.34.2
.\.venv\Scripts\python "$report/reproduce.py" cases cases-new.jsonl
.\.venv\Scripts\python "$report/reproduce.py" benchmarks benchmarks-new.jsonl
.\.venv\Scripts\python "$report/reproduce.py" replay replay-new.jsonl --source benchmarks-new.jsonl

git worktree add --detach ../euclid-origin dd5178829100ed417fd90e69621292b49d7d869b
Set-Location ../euclid-origin
uv venv --python 3.12
uv pip install -r "$report/requirements-origin.txt" -e .
.\.venv\Scripts\python "$report/reproduce.py" benchmarks benchmarks-origin-new.jsonl
```

[运行脚本](reproduce.py)直接调用两个版本各自的基准函数。逐题 JSONL 保存模型原文、解析答案、评分、耗时、token 数及错误；案例文件保存查询绑定、首个证明样例、诊断和反事实结果。
