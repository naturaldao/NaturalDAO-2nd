# Euclid-MCP：一个基于 Prolog 实现确定性逻辑推理的模型上下文协议服务器

**原文标题：** Euclid-MCP: A Model Context Protocol Server for Deterministic Logical Reasoning via Prolog
**作者：** Bartolomeo Bogliolo
**出处：** arXiv:2607.21412v2 \[cs.AI\],2026 年 8 月 11 日 · 许可协议：CC BY 4.0
**原文链接：** https://arxiv.org/abs/2607.21412

> **译者说明：** 本文为完整译文。Euclid-IR 语法、Prolog 子句、JSON 请求、标识符与工具名等代码内容保持原文，以便直接使用；数学符号已规范化为通用写法；参考文献按学术惯例保留原始英文著录信息。章节编号沿用原文。

***

## 摘要

大语言模型（LLM）在自然语言理解与生成方面表现出色，但在多步逻辑推理上依然不可靠，在安全攸关或合规敏感领域尤其如此。近期的神经符号方法通过将神经模型与外部符号引擎耦合来弥补这一差距，然而多数集成方案都是为单一场景定制的，缺少面向工具增强型智能体的标准化接口。

本文提出 **Euclid-MCP**——一个开源的 MCP 服务器，通过 SWI-Prolog 提供确定性的逻辑推理能力。

Euclid-MCP 引入了 **Euclid-IR**，这是一种面向 Horn 子句逻辑的、与推理引擎无关的中间表示：它人类可读、易于由 LLM 生成，并且易于编译为 Prolog 或其他后端。服务器暴露了一套紧凑的工具接口，支持「翻译—执行—检查—修复」循环，使 LLM 客户端既能把推理工作委派出去，又能完整访问证明树（proof tree）与推导日志。

我们在一个贴近现实的 IT 安全与合规用例上评测了 Euclid-MCP。结果显示：当知识库较小时，单靠 LLM 已足够；而在规模更大的问题上，LLM 会系统性地产生幻觉，Euclid-MCP 则能给出精确答案，同时延迟更低、输出更紧凑。我们主张：语义 RAG 从根本上不适合用于规则强制执行，而 Euclid-MCP 可以同时作为基于 RAG 的助手与智能体系统的一套稳定、共享的推理基座。

***

## 1 引言

大语言模型（LLM）的快速进展改变了自然语言处理的诸多方面，从问答与摘要，到代码生成与类智能体交互。然而，当任务需要多步逻辑推导、严格遵循形式化规则，或需要可审计的决策轨迹时，纯神经方法会暴露出有充分文献记载的局限：输出不确定、易产生幻觉，且难以给出忠实的推理证明。这些问题在业务规则强制执行、监管合规、安全策略验证等领域尤为突出——在这些场景中，决策既必须正确，又必须可解释。

越来越多的研究通过神经符号 AI 来应对这些短板，将神经模型的模式识别能力与符号推理的严谨性结合起来。其中一个重要方向是把推断委派给外部求解器（如 SAT/SMT 求解器、约束规划系统或逻辑程序引擎），同时依靠 LLM 将非形式化的问题描述翻译为形式化表示。近期工作表明，只要从自然语言到逻辑的翻译足够准确，将 LLM 推理锚定在 Prolog 上能显著提升答案准确率与推理证明的可靠性\[3, 4\]。与此同时，新兴的模型上下文协议（MCP）为 LLM 应用发现并调用外部工具与数据源提供了标准化的方式\[5]，但目前很少有 MCP 服务器把形式化推理引擎作为一等公民、可复用的组件暴露出来。

我们项目的起点是一个观察：基于语义相似度的检索增强生成（RAG）与以规则为中心的任务在根本上不匹配——在这类任务中，决策必须逻辑地从明确的策略推导出来，而不是从近似的文本相似度中得来。本文提出 Euclid-MCP,一个开源的 MCP 服务器，为任何具备 MCP 能力的 LLM 客户端提供基于 Prolog 的确定性逻辑推理。Euclid-MCP 实现了一种混合认知架构：由轻量级 LLM 用事实与规则来描述世界，而由确定性的 Prolog 引擎执行真正的推导。系统的核心贡献包括：

- **一种高层逻辑描述语言（Euclid-IR）**，用于以人类可读的、声明式的形式表达业务规则、安全策略及其他领域约束。
- **一个自动翻译层**，把这些描述编译为可执行的 SWI-Prolog 子句，保留结构并便于直接审计。
- **一套紧凑的 MCP 工具接口**，暴露推理操作（推导、诊断、场景分析、校验），支持结构化的「翻译—执行—检查—修复」循环，并提供证明树访问能力以保证可解释性。
- **有代表性的用例**，展示 Euclid-MCP 如何以透明、可验证的方式执行业务规则并核验安全策略。

Euclid-MCP 起源于将检索增强生成（RAG）应用于业务规则强制执行时遇到的一个实际限制。在这一场景中，查询必须与一份形式化或半形式化的规则语料相匹配，决策必须逻辑地从这些规则中导出，而不是依靠近似的语义相似度。依赖向量搜索与最近邻检索的标准 RAG 流水线被证明是不充分的：它们能够捞出「相似」的规则，却无法保证检索到的子集在逻辑上充分或一致，也无法为推导出的结论提供形式化证明。实际上，语义搜索的行为就像「用电钻来钉钉子」:工具本身很强大，但与任务不匹配。

这一观察促使我们重新审视基于规则的专家系统与逻辑程序——在这些范式中，知识被编码为显式规则，推断由确定性引擎执行，能够推导并解释结论。在这一基础上，我们把 Euclid-MCP 设计为一个 MCP 服务器，向 LLM 客户端暴露基于 Prolog 的推理引擎。尽管 PrologMCP \[12] 与 LogicLease \[4] 等近期工作同样探索了 Prolog 与 LLM、MCP 的融合，Euclid-MCP 的主要动机仍是克服语义检索在以规则为中心的应用中的局限，并强调一个面向业务与安全策略定制的领域化逻辑描述层。

本文其余部分组织如下：第 2 节回顾神经符号 AI、逻辑程序与 MCP 的背景和相关工作；第 3 节描述 Euclid-MCP 架构，包括逻辑描述语言、向 Prolog 的翻译以及 MCP 集成；第 4 节给出业务规则强制执行与安全策略验证中的用例；第 5 节讨论其优势、局限以及与现有系统的关系；第 6 节为结论。

***

## 2 背景与相关工作

本节将 Euclid-MCP 置于三条研究脉络的交汇处：(i) 检索增强生成（RAG）在以规则为中心任务上的局限；(ii) 基于规则的专家系统与逻辑程序这一传统；(iii) 将 LLM 与形式化推理引擎结合的近期神经符号方法。我们还将简要回顾模型上下文协议（MCP）——一个正在兴起的工具集成标准。

### 2.1 检索增强生成及其在规则上的局限

检索增强生成（RAG）已成为让 LLM 锚定于外部知识的主流范式。在典型的 RAG 流水线中，用户查询被嵌入向量空间，通过近似最近邻搜索检索相似的文档或段落，LLM 再以检索到的上下文为条件进行生成。这一做法在开放式问答、摘要以及众多知识密集型任务上表现良好——在这些任务中，「语义相似度」是相关性的良好代理指标。

然而，基于语义相似度的 RAG 与以规则为中心的应用（如业务规则强制执行、策略合规性检查、安全约束核验）在根本上不匹配。在这些场景中：

- **正确性取决于逻辑后承**：决策必须从一组明确的规则与事实中推导出来，而非从文本相似度中得出。
- **检索到的规则子集必须对查询在逻辑上充分且自洽**；最近邻检索无法提供此类保证。
- **审计与可解释性**需要形式化证明，至少也需要可追溯的推导链，而不是「模型在上下文中看到了相似规则」这种交代。

近期对实践中 RAG 的分析凸显了这些失效模式：语义检索可能捞出表面相关、却遗漏关键例外、交互关系或否定条件的规则，导致结论不一致或不安全。实际上，用语义搜索来执行形式化规则，无异于「用电钻来钉钉子」:工具很强大，但底层操作（近似匹配 vs. 逻辑推断）对这项任务是错的。

这些局限促使人们转向这样一类架构：以符号推理层补充或取代检索，该层能够保证逻辑正确性并给出显式的推导轨迹。

### 2.2 基于规则的专家系统与逻辑程序

在当前 LLM 时代之前，专家系统是编码与自动化领域专长的主流范式，尤其适用于需要严格规则应用与可解释性的场景。知识被表示为 if-then 规则与事实，推断引擎采用前向或后向链推导出结论并回答查询。这一路线的一个关键优势是透明性：系统能够通过暴露规则应用的链条来解释某个结论为何成立。

逻辑程序，尤其是 Prolog,成为众多专家系统的自然基础。Prolog 的声明式语义允许知识被表达为 Horn 子句，而其内置的推断机制（带合一的回溯搜索）能够自动从事实与规则中导出结论。经典工作论证了 Prolog 对专家系统的适用性，强调以下几点：

- 知识库（事实与规则）与推断引擎之间的清晰分离。
- 通过检视搜索过程来生成解释与证明轨迹的能力。
- 对复杂领域逻辑的紧凑、人类可读的编码。

尽管在统计机器学习与深度学习兴起期间，专家系统与 Prolog 淡出了主流视野，但在那些确定性推理、可审计性与形式化保证至关重要的任务上，它们在概念上依然相关。近期关于 Prolog 在现代 AI 中角色的讨论，凸显了它作为混合系统符号骨干的持久价值，尤其是在与神经组件结合时\[8]。

### 2.3 神经符号 AI：结合 LLM 与符号推理

神经符号 AI 力求整合神经模型的优势（模式识别、语言理解）与符号方法的优势（逻辑推断、结构化知识）。一种常见模式是：用 LLM 解析自然语言并生成结构化表示，再交由符号引擎处理，以确保正确性与可解释性。

这一方向的近期工作包括：

- **神经符号合规框架**，将基于 LLM 的理解与基于 SMT 的推理相结合，以可解释、可验证的方式分析金融法规\[9]。
- **从自然语言中抽取策略并用符号引擎强制执行的系统**，在抽取出的规则不足以完整判定时，显式地设计为「安全失效」行为。
- **将规则编译为逻辑形式、并用可满足性或约束求解器验证性质的方法**，常见于多智能体或特定领域的配置中。

在这一格局中，基于 Prolog 的神经符号系统重新受到关注。多条研究线索探索了：

- **训练或提示 LLM 生成 Prolog 代码**，再交由外部求解器执行，以同时提升答案准确率与推理证明的可靠性\[3]。
- **利用 Prolog 的推导日志生成因果性、可读的说明**，以应对纯神经推理的「黑箱」本质。
- **将自适应神经符号系统与传统的硬编码业务规则引擎作对比**，尤其是在金融与医疗等合规攸关领域。
- **将神经符号方法应用于企业系统**（如 CRM、ERP），这些系统中的业务逻辑既需灵活，又需可作形式化分析。

以往工作大多把 LLM 幻觉视为事后缓解问题，采用多智能体评审流水线和专门的评分指标，在生成之后检测并纠正无依据的断言\[11]。更近期的架构把智能体式评审与嵌套学习（Nested Learning）、语义缓存结合起来，在降低算力成本的同时减少幻觉\[10]。Euclid-MCP 走的是一条互补的、架构层面的路线：它不是在幻觉发生之后再加以纠正，而是把推理步骤彻底从模型中移除，将推导委派给确定性引擎。

### 2.4 模型上下文协议（MCP）

模型上下文协议（MCP）是一个正在兴起的开放标准，用于把 LLM 应用与外部工具、数据源及服务连接起来\[5]。MCP 定义了一套统一接口，LLM 客户端可以借此：

- 发现可用的工具与资源（如数据库、API、推理引擎）。
- 以结构化输入调用工具，并接收结构化输出。
- 把多个工具编排进复杂工作流，同时保持一致的交互模型。

MCP 很快吸引了众多大型组织的实现，以及由社区维护、不断壮大的服务器生态，涵盖文件系统与代码访问，以及各类专用数据处理器。然而直到近期，很少有 MCP 服务器把形式化推理引擎作为一等组件暴露出来。PrologMCP \[12] 等早期工作证明了把 Prolog 作为 MCP 工具暴露出来的可行性，其主要目标是通用的逻辑推理任务。

Euclid-MCP 建立在 MCP 抽象之上，但将其专门化到策略与规则建模，提供：

- 一种面向业务规则与安全约束定制的领域化逻辑描述语言。
- 内置的 Prolog 翻译、安全检查与错误报告。
- 专为策略评估、诊断分析、场景测试与知识库校验设计的工具，而非通用的 Prolog 执行器。

如此，Euclid-MCP 为新兴的「基于 MCP 的神经符号系统」这一类工作添砖加瓦，其聚焦点十分明确：克服语义检索在以规则为中心的应用中的局限。

***

## 3 Euclid-MCP 架构

本节描述 Euclid-MCP 的设计，从高层架构讲到 Euclid-IR 语言、向 Prolog 的翻译，以及 MCP 集成。系统以 Python 实现为一个 MCP 服务器，调用 SWI-Prolog 作为本地推理后端，并暴露一套小巧而专用的工具面，用于策略与规则推理。

在当前原型中使用 SWI-Prolog,是一个战术层面的选择，而不是架构依赖。Euclid-MCP 围绕一种与引擎无关的中间表示（Euclid-IR）设计，该表示可以被下沉（lowering）到 Prolog,也可以下沉到其他推断引擎（如 Datalog 引擎、SMT 求解器、自定义规则引擎），而不必改动面向用户的 API 或 MCP 工具面。

### 3.1 高层架构

Euclid-MCP 遵循一种混合认知架构：由 LLM 用事实与规则来描述世界，而由确定性推断引擎执行真正的推导。主要组件如下：

**LLM 客户端**

: 任何具备 MCP 能力的 LLM 应用（如 AI 助手、智能体框架或自研工具）。LLM 负责解读用户的自然语言输入、生成以 Euclid-IR 表示的结构化事实与规则描述、调用 Euclid-MCP 工具来求值查询并检视推导过程，再把结果与解释渲染回给用户。

**Euclid-MCP 服务器**

: 一个通过 FastMCP 实现 MCP 服务器接口的 Python 进程。它提供：一个 Euclid-IR 解析器，用于校验并规范化事实、规则与查询；一种独立于任何特定推断引擎的中间表示（Euclid-IR）；一个把 Euclid-IR 编译为可执行 SWI-Prolog 代码的下沉层；用于限制可用 Prolog 构造的安全与净化机制；以及一套面向查询求值、诊断分析、场景测试与知识库校验的工具接口。

**推断后端**

: 在当前原型中，SWI-Prolog 充当确定性推断引擎，以外部进程方式调用。服务器把 Euclid-IR 翻译成一个自包含的 Prolog 程序，写入临时文件并通过 swipl 子进程执行，解析包含解集与证明树的结构化 JSON 输出，再以类型化数据结构把结果返回给 MCP 客户端。

这种关注点分离确保了 LLM 永远不需要在内部执行多步逻辑推理；它只需描述问题并解读结果。所有推导都被委派给推断后端，从而相对于已编码的规则与事实保证逻辑正确性。

### 3.2 Euclid-IR：一种与引擎无关的中间表示

Euclid-MCP 的核心抽象是 Euclid-IR——一门为逻辑推断设计的声明式语言，其设计目标是：

- **可读**——语法同时针对人类与 LLM 做了优化。
- **精简**——只保留 Horn 子句逻辑的必需构造。
- **确定**——每个查询都有有限的、可追溯的证明。
- **后端无关**——Euclid-IR 是一层中间表示；今天它面向 Prolog,明天也可以面向其他引擎。

一个 Euclid-IR 知识库由以下部分构成：

- **事实（Facts）**——关于世界当前状态的基原子断言。
- **规则（Rules）**——形如「头 IF 体」的蕴含式。
- **查询（Queries）**——待证明的目标，以 `?` 前缀标记。
- 可选的版本声明(`@version 1.0`)与注释(`#` 或 `//`)。

#### 3.2.1 核心构造

**事实。** 描述世界当前状态的基原子：

```
parent(tom, bob)
color(apple, red)
active(user_42)
rainy
```

谓词名为小写标识符；实参为原子、整数或变量。允许零元事实(例如 `rainy`)。

**变量。** 表示未知或一般取值的量，以 `$` 为前缀：

```
$x
$who
$user_name
```

变量必须以 `$` 开头后接小写字母；它们区分大小写，并在下沉阶段被翻译为 Prolog 变量（首字母大写）。

**规则。** 带头与体的逻辑蕴含式：

```
mortal($x) IF human($x)
ancestor($x, $y) IF parent($x, $y)
ancestor($x, $y) IF parent($x, $z) AND ancestor($z, $y)
```

规则体是由 AND 连接的条件的合取。规则可以跨多行书写以提升可读性，当某行以 IF 或 AND 结尾时，续行是隐含的。

**否定。** 使用 NOT 的闭世界否定：

```
blocked($user) IF NOT active($user)
eligible($user) IF registered($user) AND NOT blocked($user)
```

当 p 无法被证明时，`NOT p` 成立，这对应于 Prolog 的 `\+`。

**查询。** 待证明的目标，以 `?` 前缀标记：

```
? mortal(socrates)
? ancestor(tom, $who)
? can_access($user, $res) AND resource($res, _, _, _, _, secret)
```

查询可以包含变量（用于寻找绑定），也可以是基项（布尔检查）。允许使用 AND 构成合取。

**算术。** 规则体中的数值比较与求值：

```
stale($user) IF user($user) AND last_login($user, $days) AND $days > 90
adult($person) IF age($person, $age) AND $age >= 18
```

支持的运算符包括 `>`, `>=`, `<`, `=<`, `=:=`, `=\=`, 以及 `is`，它们会被原样传递给后端（当前为 Prolog），并在推导时求值。

**通配符。** 下划线符号 `_` 表示匿名变量：

```
resource(apple, $color, _, _, _, _)
```

**注释。** 支持两种风格：

```
# This is a comment
// This is also a comment

parent(tom, bob)  # inline comment
```

**版本声明。** 可选的首行可声明 Euclid-IR 版本：

```
@version 1.0

parent(tom, bob)

? parent($x, $y)
```

若省略，则默认版本为 1.0。未来版本计划保持向后兼容。

#### 3.2.2 设计取舍与局限

Euclid-IR 面向 Horn 子句逻辑——即去掉高级特性后的 Prolog 核心：

- **支持**：事实、规则、否定（闭世界）、算术、多行规则、合取查询、通配符。
- **不支持**：析取（OR）、cut(`!`)、列表语法、`findall`/`bagof`、动态 `assert`/`retract`、模块、字符串（仅支持原子）。

这些局限是有意为之：它们让这门语言保持精简、确定，且易于下沉到多个后端。对于常见模式存在变通办法（例如把析取编码为多条规则，用带索引的事实来表示列表）。

Euclid-IR 也支持 YAML 格式作为结构化输入，但出于简洁性与可读性的考虑，仍推荐使用文本格式。

### 3.3 向 Prolog 的翻译

该过程完全自动化且确定：

1. **映射到子句。** 每条 Euclid-IR 事实被直接翻译为一条 Prolog 事实；每条 Euclid-IR 规则被翻译为一条 Prolog 子句。例如：

   ```
   mortal(X) :- human(X).
   ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
   ```

   查询被编码为顶层目标，可从 MCP 工具中调用。

2. **变量翻译。** Euclid-IR 变量(如 `$x`、`$who`)通过首字母大写映射为 Prolog 变量(如 `X`、`Who`)。这使用户与 LLM 免于接触 Prolog 的语法怪癖（大写变量）。

3. **关键字与运算符映射。** Euclid-IR 关键字与运算符被翻译为对应的 Prolog 形式：`IF` → `:-`,`AND` → `,`,`NOT` → `\+`,`?` → `?-`。算术运算符(`>`、`>=` 等)原样透传。

4. **安全与净化。** 翻译层强制实施若干安全属性：一个净化器校验输入中只出现被允许的谓词构造；潜在危险的内建谓词（例如文件 I/O、网络访问）被排除在生成的代码之外；输入大小上限为 500 KB,执行受超时约束（默认 30 秒）。

这一设计确保了生成的 Prolog 代码既是**可审计的**（人可以读懂并核验映射关系），又是**安全的**（LLM 无法通过 Prolog 任意执行系统命令）。未来的后端将遵循同样的模式：Euclid-IR → 目标语言，并配备相应的安全控制。

### 3.4 MCP 集成：工具与交互模式

Euclid-MCP 通过一组小而定义明确的四个 MCP 工具暴露其功能，遵循既有的 MCP 设计模式。每个工具都是一个无状态函数，接受知识库作为输入，返回带类型的结果。工具如下：

**reason**

: **用途**：主要推导——求值知识库并返回解集与证明树。

  **输入**：`knowledge`（Euclid-IR 文本或 YAML）、可选的 `query` 覆盖、`max_solutions`（默认 5）、`max_depth`（默认 30）。

  **输出**：一组解，每条解包含变量绑定（替换）以及一棵证明树，其节点类型为 fact、rule 或 and。

  **示例**：给定关于父子关系的事实与关于祖先关系的规则，`reason` 返回 `ancestor(tom, $who)` 的所有解，并附完整推导链。

**diagnose**

: **用途**：查询分析——理解某个查询为何成立或为何失败。

  **输入**：`knowledge`、`query`、`mode`(取 `why`、`why_not`、`what_needs` 之一)、`max_solutions`、`max_depth`。

  **输出**：一个 `DiagnosisResult`，含 `holds`（布尔）、`findings[]`（检测到的问题列表）、`conclusion`（人类可读摘要），以及可选的证明。

  **模式**：
  - `why`——解释某个查询为何成立（或为何不成立）;
  - `why_not`——解释某个查询为何失败（缺少哪些事实/规则）;
  - `what_needs`——指出需要补充什么才能让一个为假的查询变为真。

  **示例**：`diagnose(knowledge, "mortal(plato)", mode="why_not")` 返回形如「No facts or rules defined for 'mortal」这样的发现项，并建议应补充什么。

**what_if**

: **用途**：场景分析——对知识库施加修改，并比较修改前后的结果。

  **输入**：`base_knowledge`、`modifications`(以 `+` 开头表示新增、`-` 开头表示移除事实的若干行)、`query`、`max_solutions`、`max_depth`。

  **输出**：一个 `WhatIfResult`，含 `before_count`、`after_count`、`delta`、`solutions_before`、`solutions_after`，以及一段描述影响的结论。

  **示例**：`what_if(base_kb, "+ human(plato)", "mortal($who)")` 展示新增一条事实如何改变解的数量。

**check_kb**

: **用途**：知识库校验器——在执行推导之前检查语法错误、未定义谓词、循环规则与重复定义。

  **输入**：`knowledge`（Euclid-IR 文本或 YAML）。

  **输出**：一个 `KBCheckResult`，含 `valid`（布尔）、`errors[]`、`warnings[]`、`facts_count`、`rules_count`、`predicates_count`。

  **示例**：`check_kb(knowledge)` 返回 `{valid: true, errors: [], warnings: [], facts_count: 2, rules_count: 1}`。

这些工具被设计为支撑一个「翻译—执行—检查—修复」循环：

1. **校验（Validate）**：LLM 调用 `check_kb`，确认知识库格式良好，再进行推理。
2. **翻译（Translate）**：LLM 生成一个 Euclid-IR 知识库（事实 + 规则 + 查询）。
3. **执行（Run）**：LLM 调用 `reason`，获取带证明树的答案。
4. **检查（Inspect）**：若结果出乎意料，LLM 调用 `diagnose`，理解某个查询为何成立或失败。
5. **修复（Repair）**：依据诊断结果，LLM 可以精炼知识库（例如补上缺失规则、修正错误编码的条件），并重新运行查询。
6. **探索（Explore）**：LLM 使用 `what_if` 在真正应用修改之前先测试假设性改动。

来自推断后端的错误（例如语法错误、不可满足的查询）会按照 MCP 最佳实践，以可读文本消息的形式返回，使 LLM 能够将其作为自我纠正的反馈。

### 3.5 实现细节

Euclid-MCP 当前的原型以 Python 实现，并以 SWI-Prolog 作为推理后端。关键实现选择包括：

**Prolog 集成**

: 服务器以外部子进程方式调用 SWI-Prolog。每一次推理调用：生成的 Prolog 代码被写入一个临时 `.pl` 文件；通过 `subprocess.run()` 调用 `swipl` 二进制并设置可配置超时（默认 30 秒）；从 stdout 捕获结构化 JSON 输出（解集 + 证明树）并解析；执行完毕后清理临时文件。这一做法优先考虑简单性与可移植性：它不需要编译扩展、不需要外部语言接口，也不需要常驻的 Prolog 进程。

**MCP 传输方式**

: Euclid-MCP 支持两种传输模式：
  - `stdio`——默认的 MCP 传输方式，当服务器由本地客户端（如 Claude Desktop、OpenCode、Cursor）启动时使用；
  - `HTTP API`——一个独立的 REST 服务器(经由 `integrations/euclid_api.py`)，暴露 `POST` 端点 `/reason`、`/diagnose`、`/what-if`、`/check-kb`，以及一个 `GET /health` 端点。

  后一种模式面向与自动化平台（n8n、Zapier、Make）的集成以及远程访问场景。

**打包与分发**

: 服务器以 Python 包的形式通过 PyPI 分发(`pip install euclid-mcp`)，也可构建为捆绑了 SWI-Prolog 的 Docker 镜像，从而免去本地安装 Prolog 的需要。

这一实现为把确定性逻辑推理集成进基于 LLM 的应用提供了实用、可复用的基础，尤其聚焦于业务规则与安全策略。Euclid-IR 的存在确保了：当出现新的、更为可取或必要的推断后端时，系统能够演进到 Prolog 之外。

***
## 4 用例：IT 安全与合规

为展示 Euclid-MCP 的实际适用性，我们为一个云原生组织构建了一个贴近真实的安全合规模型。该用例说明了 Euclid-IR 如何编码多层次策略、支持多样的推理模式，并实现单靠语义检索无法企及的解释与反事实分析。

本节描述的完整知识库，连同全部查询与场景，均可在公开仓库获取：https://github.com/meob/Euclid-MCP/tree/main/examples/07_it_security_compliance

### 4.1 场景描述

被建模的组织在云环境（AWS 风格）中运行多团队的工程与运维体系。其合规要求源自：

- **外部基准**：CIS Amazon Web Services Foundations Benchmark,其控制项覆盖账户管理、S3、CloudTrail、网络、GuardDuty、RDS、EC2、Lambda 等方面。
- **内部策略**：IAM 最佳实践、角色层级、环境分层、数据分级、审批工作流以及事件响应流程。

知识库按三个概念层次组织：

1. **标准（Layer 1）**：
   CIS 控制项，带严重级别（critical、high、medium、low）。IAM 最佳实践规则，编码了职责分离违规、权限过度、僵尸访问、特权提升、根账户违规、服务账户风险等风险。

2. **策略（Layer 2）**：
   角色层级（intern → junior_dev → mid_senior_dev → senior_dev → tech_lead → eng_manager → director → vp_engineering → cto,以及运维、安全与产品角色）。环境分层（production、golden、staging、development、sandbox），附带相应的部署等级要求、加密/备份要求与审计日志要求。数据分级（public、internal、confidential、secret）与角色密级等级。访问控制规则、关键操作、审批工作流、MFA 要求，以及事故模式下的限制。

3. **数据（Layer 3）**：
   30 个用户（小版本），属性包括部门、角色、权限、MFA 状态、最后登录时间、账户类型（人类/服务）、控制台访问权限与访问密钥。50 项资源（EC2、S3、RDS、KMS、Lambda、ECS、EKS、SNS、SQS、DynamoDB），属性包括环境、加密状态、备份状态、访问级别（public/private）与数据分级。CIS 控制项适用性事实，把具体资源关联到相关 CIS 控制项。

同一模型的更大变体（200 个用户、300 项资源、约 3,872 条事实）用于性能评测与压力测试。

### 4.2 代表性查询

我们定义了一组 10 条规范查询，覆盖广泛的推理模式：单跳权限检查、多跳策略推理、时序与阈值模式、跨策略违规与资源审计。下面给出四条代表性查询，以体现 Euclid-MCP 能够回答的问题之多样性。

#### 4.2.1 通过角色层级进行权限检查（Q1）

**问题**：“user_0005 能管理服务器吗？”

```
? user_has_permission(user_0005, manage_servers)
```

该查询检查某个特定用户是否通过角色层级拥有某项特定权限。`user_has_permission/2` 谓词由用户被分配的角色导出，而 `role_has_permission/2` 谓词则同时考虑直接角色权限与经由 `inherits/2` 关系继承而来的权限。

**结果**：查询成功。证明树显示，user_0005 拥有 sysadmin 角色，该角色直接授予 manage_servers 权限。

#### 4.2.2 多跳策略推理：向生产环境部署（Q2）

**问题**：“哪些角色可以把代码部署到生产环境？”

```
? can_deploy($who, production)
```

`can_deploy/2` 谓词编码了一条复合策略：用户必须拥有 deploy_code 权限；用户的角色等级必须达到或超过目标环境的要求（production 要求等级 ≥ 6）；角色层级与 `deploy_role_level/2` 事实共同决定各角色的等级。

**结果**：查询返回 `$who` 的绑定结果，对应那些角色等级在 6 级及以上（如 director、vp_engineering、cto）且同时拥有 deploy_code 权限的用户。

#### 4.2.3 跨策略违规：职责分离（Q6）

**问题**：“哪些用户违反了职责分离原则？”

```
? violates_separation_of_duties($who)
```

`violates_separation_of_duties/1` 谓词编码了两种冲突模式：同时拥有 deploy_code 与 approve_deploy 权限；同时拥有 create_role 与 assign_role 权限。

**结果**：在小型知识库中，查询产生 2 名用户；在更大的知识库中则产生 11 名。对每名违规用户，`diagnose` 都能生成人类可读的解释，列出冲突的权限以及将其判定为违规所依据的规则。

#### 4.2.4 资源审计：未加密的生产资源（Q7）

**问题**：“哪些生产资源未加密？”

```
? resource($name, production, not_encrypted, _, _, _)
```

该查询在资源事实上执行简单的模式匹配，按环境（production）与加密状态（not_encrypted）过滤。

**结果**：查询返回一份资源名称列表（即那些位于生产环境但未加密的具体 EC2 实例、S3 存储桶、RDS 数据库等）。这直接支撑 CIS 合规审计（例如 RDS 加密对应 CIS 2.7,EC2 对应 CIS 7.1）。

### 4.3 其他查询模式

完整查询集还包含若干其他模式，进一步展示了 Euclid-IR 的表达能力：

- **基于密级的访问（Q3）**：“哪些用户可以访问 secret 数据？”

  ```
  ? can_access_resource($who, $res) AND resource($res, _, _, _, _, secret)
  ```

  该查询把用户的密级等级与资源分级关联起来，强制要求 `user_max_clearance ≥ resource_classification_level`。

- **否定查询（Q8）**：“实习生能编写代码吗？”

  ```
  ? user_has_permission($who, write_code) AND has_role($who, intern)
  ```

  **预期结果**：空集，因为实习生只有 read_code。这验证了策略确实正确地限制了实习生。

- **时序 / IAM 治理（Q5、Q9）**：“哪些用户存在僵尸访问（超过 90 天）？”

  ```
  ? stale_access($who)
  ```

  “哪些用户权限过多（超过 15 项）？”

  ```
  ? excessive_permissions($who, $count)
  ```

  这些编码了 AWS IAM 最佳实践中的模式，用于检测陈旧凭据与最小权限违规。

综合来看，这些查询覆盖了单跳、多跳、时序、跨策略、阈值与资源审计等推理模式。

### 4.4 解释与诊断推理

除了回答查询，Euclid-MCP 还能解释某个结论为何成立或为何失败。我们定义了三个诊断问题来说明这一能力。

#### 4.4.1 为什么某用户拥有某项权限？(Q11)

**问题**：“为什么 eng_0008 拥有 manage_servers 权限？”

使用 `diagnose` 工具并设 `mode="why"`：

```
{"knowledge": "...",
 "query": "user_has_permission(eng_0008, manage_servers)",
 "mode": "why"}
```

**解释**：系统生成一棵证明树，显示 eng_0008 拥有 sysadmin 角色，该角色通过 `role_permission(sysadmin, manage_servers)` 拥有 manage_servers 权限。

#### 4.4.2 为什么某用户缺少某项权限？(Q12)

**问题**：“为什么 eng_0002（实习生）没有 deploy_code 权限？”

使用 `diagnose` 工具并设 `mode="why_not"`：

```
{"knowledge": "...",
 "query": "user_has_permission(eng_0002, deploy_code)",
 "mode": "why_not"}
```

**解释**：系统报告 eng_0002 的角色为 intern,该角色只有 read_code 与 run_tests 权限。从 intern 到任何拥有 deploy_code 的角色之间都不存在继承路径。

#### 4.4.3 要获得某项权限需要什么？(Q13)

**问题**：“eng_0002 需要什么才能部署代码？”

使用 `diagnose` 工具并设 `mode="what_needs"`：

```
{"knowledge": "...",
 "query": "user_has_permission(eng_0002, deploy_code)",
 "mode": "what_needs"}
```

**解释**：系统识别出缺失的条件：eng_0002 需要拥有一个带 deploy_code 权限的角色（如 senior_dev、tech_lead 或更高）。

### 4.5 假设性分析与反事实

Euclid-MCP 还能对知识库的假设性改动进行求值，从而支持影响分析与策略设计。我们使用 `what_if` 工具定义了三个假设性场景：

#### 4.5.1 角色晋升（W1）

**问题**：“如果 eng_0002（实习生）被晋升为 senior_dev 会怎样？”

```
{"base_knowledge": "...",
 "modifications": "- has_role(eng_0002, intern)\n+ has_role(eng_0002, senior_dev)",
 "query": "user_has_permission(eng_0002, deploy_code)"}
```

**结果**：在基线配置下，查询失败（实习生不能部署）。在修改后的配置下，查询成功，解释显示 senior_dev 拥有 deploy_code 权限，并被 eng_0002 继承。

#### 4.5.2 新增一项合规资源（W2）

**问题**：“如果新增一个已加密的生产数据库会怎样？”

```
{"base_knowledge": "...",
 "modifications": "+ resource(new_db, production, encrypted, db_team, 2026-07-01, database)\n+ resource_type(new_db, database)",
 "query": "resource($name, production, encrypted, _, _, _) AND resource_type($name, database)"}
```

**结果**：在修改后的配置下查询成功，确认新资源满足加密与环境要求。

#### 4.5.3 新增角色（W3）

**问题**：“如果 ops_0001（helpdesk）获得 sysadmin 角色会怎样？”

```
{"base_knowledge": "...",
 "modifications": "+ has_role(ops_0001, sysadmin)",
 "query": "user_has_permission(ops_0001, manage_servers)"}
```

**结果**：在基线配置下，ops_0001（helpdesk）没有 manage_servers。在修改后的配置下，查询成功，解释展示了新的权限路径。

### 4.6 讨论

该用例展示了若干关键要点：

1. **表达能力**：Euclid-IR 能够编码贴近真实的多层次安全与合规策略，包括角色层级、环境分层、数据分级、审批工作流与 CIS 控制项适用性。

2. **多样的推理模式**：查询集覆盖单跳、多跳、时序、跨策略、阈值与资源审计模式，以及诊断推理与反事实推理。

3. **可解释性**：对每一个结论，Euclid-MCP 都能生成证明树并渲染为人类可读的形式，支撑审计、人员入职与策略设计。

4. **确定性与可审计性**：与只能检索「相似」策略的语义 RAG 不同，Euclid-MCP 能对「该用户是否合规？」或「哪些资源违反 CIS 控制项？」这类问题给出确定且可审计的答案。

5. **可扩展性**：同一模型可从小型知识库（约 30 用户、约 50 资源）扩展到较大知识库（约 200 用户、约 300 资源），而无需修改任何策略规则，表明 Euclid-IR 能够支撑现实中的组织规模。

### 4.7 查询汇总

供参考，表 1 汇总了全部规范查询、诊断问题与假设性场景。

**表 1:IT 安全与合规用例中的查询与场景汇总。**

| ID | 类型 | 问题 | 模式 |
|---|---|---|---|
| Q1 | 查询 | user_0005 能管理服务器吗？ | 单跳权限检查 |
| Q2 | 查询 | 哪些角色可以把代码部署到生产环境？ | 多跳策略推理 |
| Q3 | 查询 | 哪些用户可以访问 secret 数据？ | 密级 vs. 数据分级 |
| Q4 | 查询 | tech_lead 能部署到 golden 环境吗？ | 多角色部署 |
| Q5 | 查询 | 哪些用户存在僵尸访问（超过 90 天）? | 时序 / IAM 治理 |
| Q6 | 查询 | 哪些用户违反职责分离原则？ | 跨策略违规 |
| Q7 | 查询 | 哪些生产资源未加密？ | 资源审计 |
| Q8 | 查询 | 实习生能编写代码吗？ | 否定查询（预期为空） |
| Q9 | 查询 | 哪些用户权限过多（>15）? | 阈值 / 最小权限 |
| Q10 | 查询 | 生产环境中哪些 S3 存储桶未加密？ | 组合过滤 |
| Q11 | 诊断 | 为什么 eng_0008 拥有 manage_servers 权限？ | 「为什么成立」解释 |
| Q12 | 诊断 | 为什么 eng_0002（实习生）没有 deploy_code 权限？ | 「为什么不成立」解释 |
| Q13 | 诊断 | eng_0002 需要什么才能部署代码？ | 「需要什么」分析 |
| W1 | 假设 | 如果 eng_0002（实习生）被晋升为 senior_dev? | 角色晋升 |
| W2 | 假设 | 如果新增一个已加密的生产数据库？ | 资源新增 |
| W3 | 假设 | 如果 ops_0001（helpdesk）获得 sysadmin 角色？ | 角色新增 |

***

## 5 评测

我们从两个维度评测 Euclid-MCP：

1. **定性表达能力**：Euclid-IR 能否编码贴近真实的多层次策略，并支持多样的推理模式（如第 4 节所展示）?
2. **定量性能与准确性**：系统如何随知识库规模扩展？在逻辑任务上与纯 LLM 推理相比表现如何？

评测聚焦于第 4 节的 IT 安全与合规用例，同时使用小型（约 30 用户、约 50 资源、约 578 条事实）与大型（约 200 用户、约 300 资源、约 3,872 条事实）两个知识库，另加一个 1,000 用户的合成 RBAC 基准。

### 5.1 表达能力

安全合规模型表明 Euclid-IR 能够编码：

- **多层次策略**：外部标准（CIS 控制项）、内部策略（角色层级、环境分层、数据分级）与具体数据（用户、资源、配置）。

- **多样的推理模式**：单跳权限检查、多跳策略推理、时序模式（僵尸访问）、阈值模式（权限过多）、跨策略违规（职责分离）与资源审计（未加密的生产资源）。

- **诊断与反事实推理**：「为什么成立 / 为什么不成立」的解释、「需要什么」的分析，以及面向角色工程与基础设施规划的假设性场景。

这些能力远远超出了语义 RAG 所能提供的范围。RAG 可以检索出「相似」的策略或历史事件，但它无法确定性地推导出某用户是否违反职责分离、哪些资源未通过 CIS 控制项检查，以及某个角色被修改后会发生什么变化。

### 5.2 推理基准

为量化 Euclid-MCP 相对纯 LLM 推理的收益，我们进行了两组基准测试，比较以下三种条件：

- **A**：llama3.1:8b（小型本地 LLM）。
- **B**：qwen3-coder:480b-cloud（大型云端 LLM）。
- **C**：llama3.1:8b + Euclid-MCP（以确定性推断增强的小型 LLM）。

#### 5.2.1 小规模推理基准

**任务**：5 项逻辑推理任务（家谱、分类法、RBAC），每项含 5–15 条事实。
**目标**：评估 LLM 单独能否处理小型、自包含的逻辑问题。

**表 2:小规模推理基准结果。**

| 题号 | 任务 | 真值 | A(8B) | B(480B) | C(8B+Euclid) |
|---|---|---|---|---|---|
| Q1 | 家谱（深层链） | 是 | ✓ | ✓ | ✓ |
| Q2 | 分类法（属性继承） | 是 | ✓ | ✓ | ✓ |
| Q3 | 分类法（否定推断） | 否 | ✓ | ✓ | ✓ |
| Q4 | RBAC（权限继承） | 是 | ✓ | ✓ | ✓ |
| Q5 | RBAC（否定） | 否 | ✓ | ✓ | ✓ |
|  | 准确率 |  | 5/5 | 5/5 | 5/5 |
|  | 平均耗时 |  | 4 772 ms | 2 180 ms | 2 542 ms |
|  | 平均 token（入/出） |  | 131 / 118 | 130 / 133 | 254 / 46 |

**结论**：在小型知识库（5–50 条事实）下，三种条件的准确率相当。Euclid-MCP 的准确率与 LLM 持平，但输入 token 略高（254 vs. 131），原因在于 Euclid-IR 的编码开销。执行时间也处于同一量级（2.5 s vs. 4.8 s / 2.2 s）。

#### 5.2.2 大规模 RBAC 基准

**任务**：1,000 个合成用户、7 个带层级的角色、17 项基础权限、20 条直接授权——共 1,053 条事实。
**目标**：评估在 LLM 工作记忆失效的规模下的性能表现。

**表 3:大规模 RBAC 基准结果。**

| 题号 | 任务 | 真值 | A(8B) | B(480B) | C(8B+Euclid) |
|---|---|---|---|---|---|
| Q1 | 统计拥有 delete_repo 的用户数 | 31 | × 1 | × 1 | ✓ 31 |
| Q2 | user_0142 能 push_code 吗？ | 是 | ✓ | ✓ | ✓ |
| Q3 | 统计拥有 deploy 的用户数 | 103 | × 100 | × 901 | ✓ 103 |
| Q4 | user_0834 能 read_logs 吗？ | 是 | × 否 | ✓ | ✓ |
| Q5 | user_0222 能 manage_billing 吗？（直接授权） | 是 | ✓ | × 否 | ✓ |
|  | 准确率 |  | 2/5 | 2/5 | 5/5 |
|  | 平均耗时 |  | 6 966 ms | 3 695 ms | 963 ms |
|  | 平均 token（入/出） |  | 386 / 165 | 435 / 212 | 421 / 12 |

**结论**：在规模化场景下（1,000 条以上事实）,LLM 单独使用会系统性地产生幻觉——8B 与 480B 云端模型都给出了错误的计数，并遗漏了明确存在的事实。Euclid-MCP 则每次都给出精确答案，同时更快（963 ms vs. 6 966 ms）、token 效率更高（输出 12 vs. 165 个 token），因为 LLM 只需生成一条简单查询，而不是一整段谬误推理。

### 5.3 基准测试结果小结

**表 4:基准测试汇总。**

| 知识库规模 | 纯 LLM | LLM + Euclid-MCP |
|---|---|---|
| 小型（5–50 条事实） | ✓ 准确率足够 | △ 准确率相当，输入 token 更高 |
| 大型（1,000 条以上事实） | × 系统性幻觉 | ✓ 精确推导，更快，token 更省 |

**核心结论**：Euclid-MCP 在规模化场景中证明了自身价值。当事实能装进 LLM 的上下文窗口、且推理链较浅时，引入确定性引擎的开销通常并不划算；但当知识库超过数百条事实——或当需要精确计数、求交集、多跳继承时——Euclid-MCP 能给出精确答案，而任何规模的 LLM 都会系统性地产生幻觉。

### 5.4 与语义 RAG 的对比

为使上述结果具备参照系，不妨考察用语义 RAG 回答一个合规问题的典型流程：

1. 依据查询检索相关策略文档或历史事件。
2. 阅读检索到的文档，尝试推断答案。
3. 猜测或近似给出结论，且往往带着相当的不确定性。

相比之下，Euclid-MCP：

1. 把策略编码为 Euclid-IR 中的形式化规则。
2. 用逻辑推断确定性地导出答案。
3. 用证明树解释推导过程。

**表 5:对比：语义 RAG vs. Euclid-MCP。**

| 方面 | 语义 RAG | Euclid-MCP |
|---|---|---|
| 推理 | 近似，基于相似度 | 确定性，基于形式化规则 |
| 可审计性 | 低（只有检索到的片段，无证明） | 高（证明树、规则引用） |
| 策略强制执行 | 做不到（仅检索） | 直接支持（规则编码了执行逻辑） |
| 反事实 | 不支持 | 支持（假设性场景） |
| 规模化准确性 | 随知识库规模退化 | 精确，与知识库规模无关 |
| 延迟 | 取决于检索 + LLM 推理 | 所测查询通常约 1 秒 |

这一对比凸显：Euclid-MCP 并非 RAG 的替代品，而是针对需要确定性推理与可审计性的场景的一种补充性工具。

### 5.5 局限

尽管评测展现出较强的表达能力与准确性，仍有若干局限需要说明：

1. **Horn 子句限制**：Euclid-IR 不支持析取、cut、列表模式匹配或 Prolog 的高级特性。这限制了它在某些问题域的表达能力（例如复杂数据结构、超出「失败即否定」的非单调推理）。

2. **超过 1 万条事实后的可扩展性**：系统在知识库规模达到约 4,000 条事实时表现良好，但更大的知识库（例如 10 万条以上事实）可能需要优化（例如建立索引、使用 tabling,或迁移到 Datalog 引擎）。

3. **后端依赖**：当前原型依赖 SWI-Prolog。虽然 Euclid-IR 被设计为与后端无关，但替代后端（如 Datalog、SMT）尚未实现或评测。

4. **集成开销**：把 Euclid-MCP 集成进基于 LLM 的应用需要额外工具链（例如 Euclid-IR 生成、错误处理、解释渲染），与纯 RAG 相比可能提高开发复杂度。

### 5.6 小结

评测表明 Euclid-MCP：

- 能用 Euclid-IR 表达贴近真实的多层次策略。
- 支持多样的推理模式，包括诊断分析与反事实分析。
- 在 LLM 单独使用会系统性幻觉的规模化场景中给出精确答案。
- 在交互式使用中表现良好，知识库规模达约 1,000 条事实时，查询延迟中位数低于 1 秒。
- 通过为策略强制执行与合规场景提供确定性、可审计的推理，补充了语义 RAG。

未来工作将探索替代后端（如 Datalog、SMT）以提升可扩展性与表达能力，并研究面向生产环境 LLM 应用的集成模式。

## 6 结论

本文提出了 Euclid-MCP——一个通过模型上下文协议为大语言模型增强确定性逻辑推理能力的系统。通过引入 Euclid-IR（一种面向 Horn 子句逻辑、与引擎无关的中间表示）,Euclid-MCP 让 LLM 能够编码、求值并解释复杂策略与规则，而无需具备逻辑程序或 Prolog 语法方面的专业能力。

评测给出三项关键发现：

1. **表达能力**：Euclid-IR 能够编码贴近真实的多层次安全与合规策略，包括角色层级、环境分层、数据分级、审批工作流与 CIS 控制项适用性。系统支持多样的推理模式（单跳、多跳、时序、跨策略、阈值与资源审计查询），以及诊断分析与反事实分析。

2. **规模化准确性**：在小规模知识库（5–50 条事实）上，纯 LLM 的准确率与 Euclid-MCP 相当。然而在规模化场景下（1,000 条以上事实），任何规模的 LLM——从 8B 本地模型到 480B 云端模型——都会在计数、求交集与继承类查询上系统性地产生幻觉。Euclid-MCP 在所有情形下都给出精确答案，同时更快、token 更省。

3. **可解释性与可审计性**：对每一个结论，Euclid-MCP 都能生成证明树并渲染为人类可读的形式。这支撑了审计、人员入职、角色工程与策略设计——这些正是语义 RAG 与纯 LLM 推理所不具备的能力。

本工作的核心论点是：语义 RAG 是用于规则强制执行的错误工具。RAG 擅长检索相关文档，但它无法确定性地推导出某用户是否违反职责分离、哪些资源未通过合规控制项检查，以及某项策略被修改后会发生什么变化。Euclid-MCP 通过提供一个确定性推断层填补了这一空白，与 RAG 和 LLM 推理形成互补。

## 实践启示

对于构建基于 LLM 应用的从业者，启示很明确：

- **用 RAG 处理开放式查询、文档检索与知识探索。**
- **用 Euclid-MCP（或类似的确定性推理工具）处理策略强制执行、合规检查、访问权限审查，以及任何需要精确、可审计答案的场景。**
- **两者结合**：用 RAG 检索出相关策略，再用 Euclid-MCP 判定某个具体配置或操作是否符合这些策略。

这种混合方式同时利用了两种范式的长处：语义检索的灵活性与广度，以及逻辑推断的精确性与可审计性。

## Euclid-MCP：面向智能体的稳定推理基座

处理复杂任务的一个新兴趋势，是使用能够生成并执行程序的 LLM 智能体：它们收集信息、编写代码、编排工具，最终返回结果。这缓解了流程性任务上的幻觉，却为合规与策略推理带来了另一个问题：

- 每一个新的合规问题都可能催生新的智能体与新生成的程序。
- 不同智能体可能对同一策略编码出略有差异的解释。
- 久而久之，组织会积累起彼此不一致、临时拼凑的策略实现，难以审计、比较或演进。

Euclid-MCP 对此的解法，是把规则知识外化为单一的、权威的表示（Euclid-IR），它具有以下性质：

- **共享**：所有智能体与工具查询同一套策略定义。
- **稳定**：策略只在 Euclid-IR 知识库被更新时才发生变化，而非在部署新智能体时。
- **可审计**：无论由哪个智能体发起查询，每一个决策都可回溯到具体的规则与事实。
- **可复用**：同一知识库即可支撑访问权限审查、部署审批、事件响应与合规报告，无需重复编码逻辑。

在这一视角下，Euclid-MCP 并非智能体的替代方案；它是一个共享的策略引擎，智能体（以及 RAG 系统）在遇到基于规则的、需要确定性答案的问题时，通过 MCP 调用它。

## 更广泛的影响

Euclid-MCP 代表了迈向混合认知架构的一步——这类架构把 LLM 的通用性与符号推理的精确性结合起来。通过把逻辑推理暴露为一个 MCP 工具，我们降低了开发者将确定性推断集成进应用的门槛：他们无需成为逻辑程序专家。

Euclid-IR 的设计——人类可读、与后端无关、易于翻译到多种目标语言——确保了随着新推断引擎的出现，系统能够演进到 Prolog 之外。这使 Euclid-MCP 成为未来混合推理系统研究的灵活基础。

## 最后的话

本次评测的结果支持一个简单的结论：当事实能装进 LLM 的上下文窗口、且推理链较浅时，单靠 LLM 就足够了。当情况并非如此——超过数百条事实时——确定性推理就变得必不可少。

Euclid-MCP 在规模化场景中证明了自身价值：在任何规模的 LLM 都系统性幻觉的地方，它给出精确答案。通过在自然语言与形式化逻辑之间架起桥梁，Euclid-MCP 催生了一类全新的 LLM 应用——它们不仅表达流畅、灵活，而且精确、可审计、可信。

**可用性**：Euclid-MCP 的实现、Euclid-IR 规范，以及本文描述的全部基准测试，均可在 https://github.com/meob/Euclid-MCP 获取。

***

## 参考文献

- **[1]** meob. *Euclid-MCP: MCP Server for Logical Reasoning — Turns Facts into Formal Proofs.* https://github.com/meob/Euclid-MCP, 2025. 访问日期：2025-07-22。

- **[2]** Lauren Nicole DeLong, Ramon Fernández Mir, and Jacques D. Fleuriot. *Neurosymbolic AI for Reasoning over Knowledge Graphs: A Survey.* IEEE Transactions on Neural Networks and Learning Systems, 2024. https://doi.org/10.1109/TNNLS.2024.3420218。

- **[3]** Sen Yang, Xin Li, Leyang Cui, Lidong Bing, and Wai Lam. *Neuro-Symbolic Integration Brings Causal and Reliable Reasoning Proofs.* In Findings of the Association for Computational Linguistics: NAACL 2025, 2025.

- **[4]** Sanskar Sehgal and Yanhong A. Liu. *Logical Lease Litigation: Prolog and LLMs for Rental Law Compliance in New York.* In Proceedings of the International Conference on Logic Programming (ICLP 2024), volume 416 of EPTCS, pages 59–68, 2025. https://doi.org/10.4204/EPTCS.416.4。

- **[5]** Model Context Protocol Contributors. *Model Context Protocol Servers.* https://github.com/modelcontextprotocol/servers, 2025. 访问日期：2025-07-22。

- **[6]** Jan Wielemaker and others. *SWI-Prolog: A Modern Prolog System.* https://www.swi-prolog.org/, 2025. 访问日期：2025-07-22。

- **[7]** Zenodo Community. *Knowledge Graphs as Grounded World Models for Neuro-Symbolic Artificial Intelligence.* https://zenodo.org/records/18880228, 2025. 访问日期：2025-07-22。

- **[8]** Adam Rybiński. *Prolog MCP Server: Neurosymbolic AI for Modern Workflows.* https://dev.to/adamrybinski/prolog-mcp-server-neurosymbolic-ai-for-modern-workflows-3e35, 2025. 访问日期：2025-07-22。

- **[9]** Yung-Shen Hsia, Fang Yu, and Jie-Hong Roland Jiang. *Neuro-Symbolic Compliance: Integrating LLMs and SMT Solvers for Automated Financial Legal Analysis.* Proceedings of the 2nd ACM AIware Conference, 2026.

- **[10]** Diego Gosmar and Deborah A. Dahl. *Hallucination Mitigation with Agentic AI, Nested Learning, and AI Sustainability via Semantic Caching.* arXiv preprint, 2026.

- **[11]** Diego Gosmar and Deborah A. Dahl. *Hallucination Mitigation using Agentic AI Natural Language-Based Frameworks.* arXiv preprint, 2025. 提出 Total Hallucination Score(THS)KPI。

- **[12]** Agnieszka Mensfelt, Adarsh Prabhakaran, Adrian Haret, Vince Trencsenyi, and Kostas Stathis. *PrologMCP: A Standardized Prolog Tool Interface for LLM Agents.* arXiv preprint, 2026. 录用于 Joint Workshop on Statistics and Knowledge Integration for Logic, Learning, Ethical Decisions, and LLMs,2026 年 7 月 18 日，里斯本。

***

**版权与许可**：原文以 CC BY 4.0 许可发布。本译文为该论文的中文翻译，仅供学习与参考；如需引用、转载或再分发，请遵循原始许可条款。
