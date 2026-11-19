# 复验方法

所有命令从本实验目录运行。只想查结果时，运行 `python score.py` 即可从已归档的逐题输出重算 [指标](metrics.json) 和 [预测表](predictions.csv)，这一操作只用 Python 标准库。建议在独立工作副本重新推理，便于和归档结果逐行比较。

## 一、输入和标签

[案例生成器](make_cases.py) 生成 [20 条英文公开合成题](cases.json)。每条 `text` 是政策、记录和待判问题；`labels` 是允许的答案。同一家族按题序循环改变选项顺序。这里的“独立预期”指建题时手工指定的标签，不代表已有外部专家复标。前两组允许两种证据均缺或相互冲突；第三组明确假设登记册完整，未能推出权限即可答 NO。

| 字段 | 用途 |
|---|---|
| `gold` | 评估时比对，从未作为模型提示或 Prolog 子句 |
| `vocabulary`、`facts` | 前者为该家族允许的原子词表，对抽取器可见；后者为人工参考，供抽取评分和人工事实对照组使用 |
| `rules`、`goals`、`decode` | 预先写好的规则、按顺序查询的目标、支持位到标签的映射 |
| `knowledge` | 规则与该路输入事实的拼接。虚拟常量 dummy 仅声明谓词并使其可查询；所有实际目标指向其他常量 |

抽取器只可返回预设原子，不生成可执行程序。客户端将已选原子去重，添加到同一套规则上。适配器只接受本实验所需的平坦谓词、变量与合取，将其转成 Euclid-IR。两个系统共享事实、规则、目标和解码表。返回上限为 1，因为每个目标只问存在性；这个设置不适用于枚举全部证明或统计授权人数。

## 二、直接判断与抽取

本机为 Windows，Ollama 0.34.2，Llama 3.1 8B，Q4_K_M，模型摘要以 [运行元数据](llm_meta.json) 为准。模型加载在本机，接口默认为 `127.0.0.1:11434`。提示、输出 JSON Schema、采样参数、原始文本、计时和 token 计数均随 [逐题响应](llm_raw.jsonl) 保存。只向直接判断臂发送 `text`、选项和任务指令。抽取臂看同一 `text` 和有限候选事实，不看人工事实、预期答案或前一路回答。

~~~powershell
ollama pull llama3.1:8b
python make_cases.py
python llm_runner.py
python llm_runner.py --record-only
~~~

第一次运行依次做 20 次判断和 20 次抽取。第二次只做 20 次抽取，用记录正文替换原提示里的“政策 + 记录”，得到 [另存的原始响应](record_only_llm_raw.jsonl)。温度为 0、seed 为 42，上下文窗口 2,048，最多新生成 160 token；使用 Ollama 的 JSON Schema 约束输出。模型服务或硬件版本改变时，逐字响应与延迟可能变化。

## 三、启动真实的两个 MCP 服务

运行器是 stdio 客户端。先准备两个独立的作者仓库和环境。下列 PowerShell 命令假定已安装 Git、uv、SWI-Prolog 10.0.2，且可执行文件 swipl 在 PATH。仓库放在临时目录中；已有对应版本工作副本时可直接指定其绝对路径。

~~~powershell
$pr = Join-Path $env:TEMP 'comparison-prologmcp'
$eu = Join-Path $env:TEMP 'comparison-euclid-mcp'
git clone https://github.com/dicelab-rhul/PrologMCP.git $pr
git -C $pr checkout 4ae536fd9b1cef8419d1798b5d4cb1569cba3cae
git clone https://github.com/Euclid-BG/Euclid-MCP.git $eu
git -C $eu checkout aed10179131fc990739f5d69b0584f4a065f0faa
uv venv --python 3.13.15 "$pr/.venv"
$pc = Join-Path $pr '.venv/Scripts/python.exe'
uv pip install --python $pc 'mcp==1.30.0'
uv sync --project $eu --python 3.12.10 --frozen --no-dev
$ec = Join-Path $eu '.venv/Scripts/python.exe'
$sw = (Get-Command swipl).Source
$common = @('--prolog-repo',$pr,'--prolog-python',$pc,'--euclid-repo',$eu,'--euclid-python',$ec,'--swipl',$sw)
& $pc mcp_runner.py @common --cases cases.json --output raw/oracle
& $pc mcp_runner.py @common --cases extracted_cases.json --output raw/hybrid
& $pc mcp_runner.py @common --cases record_only_extracted_cases.json --output raw/record-only
& $pc paper-five/replay.py @common --output paper-five/raw
~~~

[运行器](mcp_runner.py) 会核对两个仓库的提交号与已跟踪文件，分别启动 `prolog_mcp.server` 和 `euclid_mcp`。两端均实际调用 SWI-Prolog。PrologMCP 对每个案件调用 `create_session`，读出装载诊断，再逐条 `run_goal` 并 `close_session`。Euclid 对每个查询调用一次 `reason`，重发完整 IR；本实验固定的论文同期版本按查询启动引擎。每个 MCP 工具调用等待上限 45 秒。工具报错和普通无解分开记录，只有正常响应才能映射为标签。原始结果同时保存输入文件的 SHA-256、服务版本和逐调用响应。两种适配器所需的会话管理步骤不同。

## 四、PoL2 本地判别器与评分

使用 NaturalDAO 发布的 Kev PoL2 Score-v2 M10 的 seed-43 adapter 和 pointer head，底座为 Qwen3.5-4B-Base，固定 revision 见脚本。项目在此前看到三个训练种子的结果后选定 seed-43 为默认候选。这里沿用已发布默认版本。请按项目模型卡取得权重并用清单校验；安装 [Kev 源码 2074cc4](https://github.com/jaredpalmer/kev/tree/2074cc44256200bb37540103fa4572901faa10f3)并准备底座缓存后运行。脚本在本机以 CPU BF16、6 线程逐题推理，PyTorch 包版本为 2.8.0+cu128，输出各选项的 logits、概率、预测、用时及实际加载文件摘要。[模型卡与安装](../../../../PoL-Governance/models/kev-pol2-score-v2-m10/README.md) · [固定权重摘要](../../../../PoL-Governance/models/kev-pol2-score-v2-m10/weights.json) · [模型运行器](run_kev.py)

~~~bash
python run_kev.py --checkpoint /path/to/seed-43 --output kev-m10.json
python score.py
~~~

单次计时随运行阶段而异。LLM 记录本地 HTTP 墙钟时间（可含首题载入），PoL2 记录编码和前向推理时间（排除一次性模型加载），MCP 记录已连接后处理整案的耗时。组合路径以同一题的抽取时间和工具时间相加，属于串行估计。p95 取最近秩，20 题仅为第 19 个排序观测。部分任务并发执行，延迟不能用作线上吞吐承诺。

官方 TypeSafe Jev 没有参加本机实验。[官方接口脚本](run_jev.py) 为日后有凭据时的复验入口，不参与本次评分。三路一致性分析实际用的是 Llama 直接标签、Llama 抽取后 Prolog 的标签，以及本地 PoL2 判别器的标签。
