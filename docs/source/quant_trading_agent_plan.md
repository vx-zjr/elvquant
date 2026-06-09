# 文档驱动的量化交易系统开发计划

> 目标：做一个模块化、可迭代、低技术债的量化交易系统。第一阶段不追求赚钱，也不追求 AI 炫技，先追求“不会骗自己、能查清楚、能小步生长”。

> 总原则：上下文放进文档，不放进大模型记忆。任何 code agent 开始工作前都必须读文档；任何任务结束后都必须更新文档。

---

## 0. 大白话总览

你要做的不是“让 AI 自动炒股”，而是先做一条可信流水线：

1. 数据进来。
2. 策略根据当时能看到的数据产生想法。
3. 组合模块把想法变成目标仓位。
4. 风控模块判断能不能做。
5. 回测模块在历史里演练。
6. 记账模块算现金、持仓、成本、盈亏。
7. 报告模块告诉你结果靠不靠谱。
8. 模拟盘每天像实盘一样跑，但不真钱下单。
9. 很后面才允许小资金实盘。

AI 的位置：AI 可以当研究助理、代码助理、文本总结助理；ML 模型可以当一种信号来源。但 AI 不能绕过风控，不能直接控制账户。

---

## 1. 文档是系统大脑

仓库根目录必须维护这些文档：

- `PROJECT.md`：项目目标、当前阶段、明确不做什么。
- `ARCHITECTURE.md`：模块边界，谁负责什么，谁不能碰什么。
- `CONTRACTS.md`：接口契约，比如 `DataSource`、`SignalModel`、`Backtester` 的输入输出和语义保证。
- `DATA_POLICY.md`：数据规则，尤其是时间语义、时区、复权、缺失值、数据什么时候可见。
- `RISK_POLICY.md`：风控规则，比如最大仓位、最大亏损、最大订单金额、禁止杠杆。
- `TASKS.md`：当前任务队列。每次只允许执行一个任务。
- `DECISIONS.md`：架构决策记录，说明为什么这样做。
- `REVIEW.md`：合并前检查清单。
- `RUNBOOK.md`：怎么运行、怎么排错、怎么停机。
- `EXPERIMENTS.md`：每次回测/模拟盘的实验记录。
- `CHANGELOG.md`：用户可读的变更记录。

### 每个 code agent 的固定开工协议

你每次开新会话都这样要求 agent：

```text
你不能依赖聊天历史。请先阅读仓库根目录的 PROJECT.md、ARCHITECTURE.md、CONTRACTS.md、DATA_POLICY.md、RISK_POLICY.md、TASKS.md、REVIEW.md。

然后用 5-10 行总结：
1. 当前项目阶段是什么；
2. 本次只做 TASKS.md 里的哪一个任务；
3. 你不会修改哪些模块；
4. 本次完成标准是什么；
5. 你会跑哪些测试。

在我确认前，不要写代码。
```

### 每个 code agent 的固定收工协议

每次任务结束都要求 agent：

```text
请更新相关文档：
1. TASKS.md：标记本任务完成，写下一步建议；
2. CHANGELOG.md：写本次用户可读变更；
3. DECISIONS.md：如果你改变了接口、边界或重要规则，记录原因；
4. EXPERIMENTS.md：如果跑了回测或模拟，记录 run_id、参数、数据范围、结果；
5. RUNBOOK.md：如果运行方式变了，更新命令。

最后给我汇报：
- 改了哪些文件；
- 跑了哪些命令；
- 测试结果；
- 还有哪些风险。
```

---

## 2. 强制纪律

1. 一次只做一个任务。
2. 每个任务先写测试，再写实现。
3. 每一步结束系统必须能运行。
4. 不允许为了策略想法修改回测引擎。
5. 不允许绕过 `Risk` 模块产生订单。
6. 不允许在回测中使用未来数据。
7. 不允许一开始接真钱账户。
8. 不允许把 API key、账户信息、密码写进代码或文档。
9. 不允许用“模型觉得应该买”作为最终下单理由。
10. 所有结果都必须能追溯：代码版本、配置、数据版本、随机种子、运行时间。

---

## 3. 推荐技术栈

第一版推荐简单 Python：

- Python 3.11 或 3.12
- `pandas`：表格数据
- `numpy`：计算
- `pydantic`：配置校验
- `pytest`：测试
- `ruff`：格式和 lint
- `mypy`：类型检查
- `matplotlib` 或 `plotly`：报告图

第一版不建议上来就用：

- 复杂分布式系统
- 高频交易框架
- Kubernetes
- 大型数据库
- 自动实盘
- 深度学习

---

## 4. 开发阶段和对 code agent 的要求

### 阶段 0：项目脚手架和文档地基

目标：先建立一个空项目，但能测试、能格式检查、能被下一个 agent 读懂。

你对 code agent 说：

```text
任务：创建项目脚手架和文档地基。不要写任何量化业务逻辑。

要求：
1. 创建 Python 包结构；
2. 配置 pytest、ruff、mypy；
3. 创建 PROJECT.md、ARCHITECTURE.md、CONTRACTS.md、DATA_POLICY.md、RISK_POLICY.md、TASKS.md、DECISIONS.md、REVIEW.md、RUNBOOK.md、EXPERIMENTS.md、CHANGELOG.md；
4. 写一个空测试，证明测试系统能跑；
5. 更新 README，写清楚如何安装和运行测试。

完成标准：
- `pytest` 通过；
- `ruff check` 通过；
- `mypy` 通过；
- 不存在真实交易逻辑；
- 文档能让下一个 agent 明白当前阶段。
```

阶段 0 的 `TASKS.md` 下一步只写：定义核心接口。

---

### 阶段 1：只定义接口，不写实现

目标：先把模块边界切出来。

你对 code agent 说：

```text
任务：只定义核心接口，不写任何实现。

请先读 PROJECT.md、ARCHITECTURE.md、CONTRACTS.md、DATA_POLICY.md。

需要定义这些接口：
1. DataSource：给定时间点，返回当时可见的数据快照；
2. SignalModel：给定数据快照，输出信号；
3. PortfolioConstructor：把信号变成目标仓位；
4. RiskManager：检查目标仓位和订单是否允许；
5. Backtester：驱动回测流程；
6. ExecutionSimulator：模拟成交；
7. AccountingLedger：记录现金、持仓、成本、盈亏；
8. Reporter：输出结果和诊断。

要求：
- 每个接口都要有 docstring；
- docstring 必须说明时间语义，尤其是不能用未来数据；
- 只允许创建类型、Protocol、dataclass；
- 不允许写真实策略；
- 不允许写真实数据源；
- 不允许写回测循环。

完成标准：
- 类型检查通过；
- 测试证明接口可以 import；
- CONTRACTS.md 与代码接口一致。
```

---

### 阶段 2：最薄端到端闭环

目标：用假数据、笨策略、简单回测跑出一条净值曲线。

你对 code agent 说：

```text
任务：实现最薄端到端闭环。只用合成数据，不接真实市场数据。

实现：
1. SyntheticDataSource：生成两三个资产的假价格；
2. EqualWeightSignal：永远等权；
3. SimplePortfolioConstructor：把信号转成目标权重；
4. BasicRiskManager：只检查权重不超过 100%，不允许做空；
5. SimpleExecutionSimulator：假设下一根 bar 成交；
6. AccountingLedger：计算现金、持仓、市值、手续费；
7. Backtester：串起流程；
8. Reporter：打印收益、最大回撤、换手率。

要求：
- 先写端到端测试；
- 每个实现只能依赖接口，不要跨层偷用内部细节；
- `run.py` 或 CLI 必须能跑出结果；
- 不允许接真实数据；
- 不允许加 ML。

完成标准：
- `python run.py` 能输出结果；
- `pytest` 通过；
- 结果中包含净值、总收益、最大回撤、换手率；
- CHANGELOG.md 和 RUNBOOK.md 已更新。
```

---

### 阶段 3：诚实探针

目标：先证明系统能抓住作弊和低级错。

你对 code agent 说：

```text
任务：增加诚实探针测试。重点不是赚钱，是防止自欺。

必须增加这些测试：
1. 零信号或等权策略在扣除成本后不会凭空暴富；
2. 故意使用未来价格的作弊策略必须被测试抓住；
3. 现金 + 持仓市值 = 总权益；
4. 成本不能为负数；
5. 无交易时仓位不能乱变；
6. 风控拒绝超过最大仓位的目标；
7. 回测结果必须包含 run_id 和配置摘要。

要求：
- 先写失败测试，再改实现；
- 如果发现接口不够表达这些规则，只能先更新 CONTRACTS.md 和 DECISIONS.md，再改代码；
- 不允许加新策略；
- 不允许接真实数据。

完成标准：
- 所有诚实探针通过；
- REVIEW.md 增加“诚实探针必须通过”的检查项；
- TASKS.md 下一步才允许接真实数据。
```

---

### 阶段 4：接真实历史数据，但不做新策略

目标：把假数据源换成真实数据源，其他模块不变。

你对 code agent 说：

```text
任务：实现真实历史数据 DataSource。只替换数据源，不修改策略、回测、风控、记账。

要求：
1. 先在 DATA_POLICY.md 写清数据来源、字段、时区、复权规则、缺失值处理；
2. 实现一个只读数据源；
3. 保存原始数据和处理后数据的版本信息；
4. 每次回测结果记录数据版本；
5. 如果数据缺失，系统要明确报错或跳过，不能静默乱填。

限制：
- 不允许修改 Backtester；
- 不允许加真实策略；
- 不允许加 ML；
- 不允许接实盘 API。

完成标准：
- 同一个等权策略能在真实数据上跑；
- 诚实探针继续通过；
- EXPERIMENTS.md 记录一次真实数据 smoke run。
```

---

### 阶段 5：第一个规则策略

目标：先做一个人能理解的简单策略，比如动量或均值回归。

你对 code agent 说：

```text
任务：增加第一个规则策略。不要改回测引擎。

策略选择：
- 优先实现日线动量策略；
- 输入：过去 N 日收益；
- 输出：排名靠前资产的目标权重；
- 不允许使用未来数据。

要求：
1. 在 CONTRACTS.md 说明 SignalModel 的输入输出；
2. 在 PROJECT.md 写明这是研究策略，不是实盘建议；
3. 先写测试：给一段已知价格，验证策略选择过去表现最强的资产；
4. 策略只能通过 DataSnapshot 读取数据；
5. 不允许访问完整未来价格表；
6. 不允许修改 AccountingLedger、Backtester、ExecutionSimulator。

完成标准：
- 策略测试通过；
- 端到端回测通过；
- 报告能比较策略和等权基准；
- EXPERIMENTS.md 记录参数、结果和观察。
```

---

### 阶段 6：真实成本和成交规则

目标：让回测更接近现实。

你对 code agent 说：

```text
任务：加入交易成本和成交模拟。只改执行/成本相关模块。

要求：
1. 在 CONTRACTS.md 定义 CostModel；
2. 在 DATA_POLICY.md 写明成交价假设；
3. 实现固定佣金、按比例佣金、滑点；
4. 所有成本必须进入 AccountingLedger；
5. 报告中显示总成本、成本占收益比例、换手率。

限制：
- 不允许改策略；
- 不允许优化参数；
- 不允许加 ML。

完成标准：
- 成本非负测试通过；
- 无成本与有成本结果不同，且有成本收益不应更高；
- 端到端回测通过；
- EXPERIMENTS.md 记录成本假设。
```

---

### 阶段 7：风控层

目标：把“不能做什么”写进代码。

你对 code agent 说：

```text
任务：实现基础风控。任何订单或目标仓位都必须经过 RiskManager。

第一版风控：
1. 不允许做空；
2. 单资产最大权重 20%；
3. 总仓位最大 95%；
4. 单日换手最大 50%；
5. 单日亏损超过阈值后停止新开仓；
6. 缺失价格或异常价格时禁止交易。

要求：
- RISK_POLICY.md 必须先更新；
- 测试每条风控规则；
- 风控拒绝要返回明确原因；
- 报告中显示风控拦截次数和原因。

完成标准：
- 所有风控测试通过；
- 回测必须通过 RiskManager；
- REVIEW.md 增加风控检查项。
```

---

### 阶段 8：研究报告和实验记录

目标：让每次回测都能复盘。

你对 code agent 说：

```text
任务：增加结构化实验记录和报告。

要求：
1. 每次运行生成 run_id；
2. 记录 git commit、配置 hash、数据版本、随机种子、开始结束日期；
3. 输出净值、回撤、月度收益、换手、成本、持仓、风控拦截；
4. 报告同时保存机器可读 JSON 和人可读 Markdown；
5. EXPERIMENTS.md 只写摘要，并链接到具体报告文件。

限制：
- 不允许改策略逻辑；
- 不允许为了结果好看改指标；
- 不允许删除失败实验记录。

完成标准：
- 同一配置可复现同一 run_id 或同一配置 hash；
- 报告文件落盘；
- RUNBOOK.md 写清如何生成报告。
```

---

### 阶段 9：模拟盘

目标：每天像实盘一样跑，但不真钱下单。

你对 code agent 说：

```text
任务：实现模拟盘模式。禁止连接真钱交易。

要求：
1. 增加 paper trading 配置；
2. 每天读取最新数据；
3. 生成目标仓位、模拟订单、风控结果；
4. 订单只写入本地日志或数据库，不发给券商；
5. 每天生成一份模拟盘日报；
6. 异常时明确失败，不要静默继续。

限制：
- 不允许使用真实 broker API key；
- 不允许自动下真钱订单；
- 不允许跳过风控。

完成标准：
- 连续运行多个交易日不需要手工改代码；
- 失败有日志；
- RUNBOOK.md 写清启动、停止、排错方式。
```

---

### 阶段 10：AI/ML 研究层

目标：在系统可信之后，再把 AI 放进 `SignalModel` 这条缝后面。

你对 code agent 说：

```text
任务：增加 ML 信号研究模块。它只能输出信号，不能下单，不能改风控，不能改回测引擎。

要求：
1. 在 PROJECT.md 写明 ML 仅用于研究；
2. 在 CONTRACTS.md 定义 MLSignalModel 仍然遵守 SignalModel 接口；
3. 训练集、验证集、测试集按时间切分；
4. 特征必须记录可见时间，不能用未来数据；
5. 每次训练记录数据版本、特征版本、模型参数、随机种子；
6. ML 策略必须和简单规则策略比较。

限制：
- 不允许直接接实盘；
- 不允许用测试集调参；
- 不允许只报告最漂亮的一次结果；
- 不允许改 Backtester 来适配模型。

完成标准：
- 时间切分测试通过；
- 特征无未来数据测试通过；
- 模型结果可复现；
- 报告展示相对规则策略是否真的有增益。
```

---

### 阶段 11：小资金实盘前检查

目标：不是马上自动交易，而是确认系统达到了可以小心试水的工程标准。

你对 code agent 说：

```text
任务：做实盘前 readiness review。不要实现自动实盘交易。

请根据 REVIEW.md、RISK_POLICY.md、RUNBOOK.md 生成检查报告：
1. 所有测试是否通过；
2. 是否有 kill switch 设计；
3. 是否有订单金额限制；
4. 是否有最大亏损限制；
5. 是否有异常报警；
6. 是否能追溯每一笔订单的来源信号；
7. 是否能停机后恢复；
8. 是否有 API key 管理方案；
9. 是否有人工确认流程；
10. 是否经过足够长的模拟盘观察。

完成标准：
- 生成 readiness report；
- 明确列出不能实盘的阻塞项；
- 如果有阻塞项，不允许继续开发实盘下单。
```

---

### 阶段 12：人工确认式小资金实盘

目标：即使进入实盘，也先让人确认每一笔订单。

你对 code agent 说：

```text
任务：实现人工确认式实盘订单流程。默认不能自动下单。

要求：
1. 系统生成订单建议；
2. 风控先检查；
3. 人工确认后才允许提交；
4. 每笔订单记录：来源策略、信号、目标仓位、风控结果、确认人、确认时间；
5. 必须有 kill switch；
6. 默认配置为 dry-run；
7. 真实提交必须显式开启。

限制：
- 不允许默认自动交易；
- 不允许绕过人工确认；
- 不允许绕过风控；
- 不允许保存明文密钥。

完成标准：
- dry-run 测试通过；
- 风控拒绝时无法提交；
- kill switch 开启时无法提交；
- RUNBOOK.md 写清紧急停止流程。
```

---

## 5. `TASKS.md` 模板

每个任务都用这个格式：

```markdown
## Task ID: QTS-001

Status: Pending
Phase: 1
Title: Define core Protocol interfaces

Scope:
- Create interface definitions only.
- No implementation.
- No strategy.
- No real data.

Files likely touched:
- src/qts/contracts.py
- tests/test_contracts.py
- CONTRACTS.md
- CHANGELOG.md

Acceptance criteria:
- Interfaces import successfully.
- Docstrings explain time semantics.
- pytest passes.
- mypy passes.
- CONTRACTS.md matches code.

Agent instructions:
- Read PROJECT.md, ARCHITECTURE.md, CONTRACTS.md first.
- State your plan before editing.
- Write tests first.
- Update docs before final response.
```

---

## 6. `REVIEW.md` 最低检查清单

每次合并前检查：

- 本次是否只做了一个任务？
- 是否有测试？
- 是否跑了 `pytest`？
- 是否跑了 `ruff check`？
- 是否跑了 `mypy`？
- 是否更新了相关文档？
- 是否有未来数据风险？
- 是否改变了接口？如果改变，`DECISIONS.md` 是否记录？
- 是否影响风控？
- 是否影响记账？
- 是否能从 `RUNBOOK.md` 重新运行？
- 是否记录了实验结果？

---

## 7. 你日常给 agent 的短指令模板

### 新任务开始

```text
请不要依赖聊天历史。先读根目录文档，尤其是 PROJECT.md、TASKS.md、CONTRACTS.md、REVIEW.md。
只执行 TASKS.md 中状态为 Pending 的第一个任务。
先复述你的理解和边界，我确认后再写代码。
```

### 防止 agent 越界

```text
本次只允许改任务指定文件。不要顺手重构，不要加新功能，不要修改回测引擎，除非 TASKS.md 明确要求。
如果你认为必须越界，先停止并在 DECISIONS.md 草拟原因，等我确认。
```

### 要求测试优先

```text
请先写失败测试，运行并展示失败原因，然后写最小实现，再运行测试。
不要先写实现再补测试。
```

### 要求文档收尾

```text
代码完成后，请更新 TASKS.md、CHANGELOG.md，以及本次涉及的 CONTRACTS.md / DATA_POLICY.md / RISK_POLICY.md / RUNBOOK.md / EXPERIMENTS.md。
最后按 REVIEW.md 自查一遍。
```

---

## 8. 什么时候停止扩张

如果出现以下情况，暂停新增功能：

- 回测结果无法复现；
- 文档和代码不一致；
- agent 需要靠聊天历史才知道项目状态；
- 某个模块开始直接访问另一个模块内部数据；
- 策略为了变好看而要求修改回测引擎；
- 风控测试失败；
- 记账不平；
- 模拟盘连续运行不稳定；
- 你已经不明白系统为什么买或卖。

---

## 9. 生产实践底线

即使是个人项目，也应该模仿机构的风险控制思想：

- 下单前风控，而不是亏了再复盘；
- 所有规则文档化；
- 所有订单可追溯；
- 所有自动化都能停；
- 任何模型输出都要被监督；
- 任何实盘前都要经历模拟盘。

参考资料：

- SEC Market Access Rule 15c3-5: https://www.sec.gov/rules-regulations/2011/06/risk-management-controls-brokers-or-dealers-market-access
- FINRA Algorithmic Trading: https://www.finra.org/rules-guidance/key-topics/algorithmic-trading
- FINRA Regulatory Notice 15-09: https://www.finra.org/rules-guidance/notices/15-09

---

## 10. 第一周建议

第一周只做这几件事：

1. 第 1 天：阶段 0，脚手架和文档。
2. 第 2 天：阶段 1，接口契约。
3. 第 3-4 天：阶段 2，假数据端到端闭环。
4. 第 5 天：阶段 3，诚实探针。
5. 周末：只复盘文档和测试，不加新功能。

第一周成功标准：

- 系统能运行；
- 测试能运行；
- 文档能让新 agent 接手；
- 没有真实数据；
- 没有 ML；
- 没有实盘；
- 你能用大白话解释每个模块负责什么。

