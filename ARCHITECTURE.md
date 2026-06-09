# Architecture

## Phase 2 Boundary

The repository contains scaffolding, governance documents, typed interface
contracts, and the thinnest runnable synthetic research loop. Runtime behavior is
limited to deterministic synthetic data and simple equal-weight research logic.

## Planned Modules

- `DataSource`: returns data visible at a requested decision time.
- `SignalModel`: converts a data snapshot into research signals.
- `PortfolioConstructor`: converts signals into target positions.
- `RiskManager`: approves or rejects targets and orders before execution.
- `ExecutionSimulator`: simulates fills without broker access.
- `AccountingLedger`: tracks cash, positions, costs, and equity.
- `Backtester`: coordinates the research workflow.
- `Reporter`: produces diagnostics and reproducible reports.

## Boundary Rules

- Strategies must not bypass `RiskManager`.
- Strategies must not inspect future data.
- Execution must not connect to a real broker until explicitly allowed by a
  later readiness task.
- Accounting must not be modified to make a strategy look better.
- Documentation is the source of project context, not chat history.

## Contract Location

Core Protocols and dataclass payloads live in `src/qts/contracts.py`.

## Phase 2 Implementation Location

Minimal synthetic implementations live in `src/qts/simple.py`:

- `SyntheticDataSource`
- `EqualWeightSignal`
- `SimplePortfolioConstructor`
- `BasicRiskManager`
- `SimpleExecutionSimulator`
- `SimpleAccountingLedger`
- `SimpleBacktester`
- `SimpleReporter`

`run.py` runs the deterministic synthetic demo. It does not access real data,
broker APIs, account state, or secrets.

## Phase 4 Historical Data Location

Historical CSV support lives in `src/qts/historical.py`:

- `CsvHistoricalDataSource` reads normalized local CSV files.
- `build_historical_smoke_backtester` wires the existing equal-weight pipeline to
  the FRED sample data.
- `run_historical_smoke` produces a report for the fixed FRED smoke run.

The historical data source is read-only and does not change strategy, risk,
execution, accounting, or `SimpleBacktester` behavior.

## Phase 5 Strategy Location

Research strategies and strategy comparisons live in `src/qts/strategies.py`:

- `MomentumSignal` reads visible trailing-return features from `DataSnapshot`.
- `TrailingReturnFeatureDataSource` decorates a data source with past-observation
  return features.
- `run_momentum_smoke` runs the FRED sample momentum smoke test.
- `compare_momentum_to_equal_weight` reports momentum versus equal-weight
  baseline metrics.

The strategy does not access full future price tables and does not modify the
backtester, ledger, execution simulator, or risk manager.

## Phase 6 Cost Model Location

Cost models live in `src/qts/costs.py`:

- `FixedCommissionCostModel`
- `ProportionalCommissionCostModel`
- `SlippageCostModel`
- `CompositeCostModel`

`SimpleExecutionSimulator` estimates costs through the `CostModel` contract and
stores the resulting total cost in each `Fill`. `SimpleAccountingLedger` already
accumulates fill costs, and reports now include `total_cost` and
`cost_to_return`.

## Phase 7 Risk Location

`BasicRiskManager` in `src/qts/simple.py` now supports configurable checks for:

- no short target weights
- per-asset max weight
- total exposure
- daily turnover
- daily loss stop for new buys
- missing or abnormal prices

`SimpleBacktester` passes the latest ledger state into `RiskManager` and records
rejection counts and reason counts in result metrics. `SimpleReporter` includes
those risk metrics in text output.
