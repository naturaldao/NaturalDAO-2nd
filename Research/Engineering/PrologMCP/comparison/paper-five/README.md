# 作者表 2 五道原题的参考程序回放

2026 年 11 月 19 日。将作者随题发布的 `gold_euclid` 和目标交给两个真实 MCP 服务，通过标准输入输出读取答复。两个服务均答对 **5/5**，未发生接口或求解错误。这个分数衡量解析、转写和求解已知参考程序的表现。11 月 18 日由 8B 模型读原题并填写事实时，Euclid 路径在 Q3 加入错误事实，五题为 4/5。[原论文表 2](https://arxiv.org/html/2607.21412v2#S5.SS2.SSS1) · [上游题面、参考程序及标签](https://github.com/Euclid-BG/Euclid-MCP/blob/aed10179131fc990739f5d69b0584f4a065f0faa/benchmarks/reasoning_benchmark.py) · [11 月 18 日复现](../../../Euclid-MCP-复现/README.md)

| 编号 | 要判定的关系 | 作者预期 | PrologMCP | Euclid-MCP |
|---|---|---|---|---|
| Q1 | Tom 是 Ann 的祖先 | 是 | 是 | 是 |
| Q2 | 暹罗猫继承可伸缩爪属性 | 是 | 是 | 是 |
| Q3 | 鹰继承毛皮属性 | 否 | 否 | 否 |
| Q4 | Alice 继承文档写权限 | 是 | 是 | 是 |
| Q5 | Bob 有文档删除权限 | 否 | 否 | 否 |

脚本从固定提交读取五个题目的字面量与作者的独立 `expected` 字段，无模型调用。将事实、正 Horn 规则及其合取转为 SWI 语法，再逐字符核对反向转换还原的 Euclid 程序。两个引擎收到相同事实与目标，预期标签只在执行结束后用于评分。此处“否”指在给定有限知识库里找不到查询的证明。两条路径共用 SWI-Prolog，五道参考题均未涉及开放证据的完整性。[转换和评分脚本](replay.py) · [实际请求与答复（PrologMCP）](raw/prolog.json) · [实际请求与答复（Euclid-MCP）](raw/euclid.json) · [逐题评分与输入来源摘要](raw/scores.json)

## 重跑

准备两个干净的固定版本工作副本、它们各自安装了服务依赖的解释器、可用的 SWI-Prolog，以及安装了 Python MCP SDK 的客户端解释器。实测版本与提交号保存在上述两份响应文件开头。下列命令从本目录运行，命令中的大写参数取本机实际路径。输出保存在新目录。

```text
CLIENT_PYTHON replay.py --prolog-repo PROLOG_REPO --prolog-python PROLOG_PYTHON --euclid-repo EUCLID_REPO --euclid-python EUCLID_PYTHON --swipl SWIPL_EXECUTABLE --output new-results
```

原题参考程序及转写所用上游材料保留 [Euclid-MCP 许可证](LICENSE-upstream)。
