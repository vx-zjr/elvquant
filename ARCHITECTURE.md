# Architecture

## Core Boundary

This repository is `elvquant_core`. It owns trading-system business logic:
provider validation, strategy execution, portfolio construction, risk checks,
execution simulation, accounting, reporting, readiness, paper trading, and
manual dry-run order records. UI clients are replaceable thin adapters above the
core and must not reimplement business logic.

The first UI client is planned as `elvquant_front`, a Streamlit local debugging
console. It should call public core entrypoints and render outputs only.

## Phase 2 Boundary

The repository contains scaffolding, governance documents, typed interface
contracts, and the thinnest runnable synthetic research loop. Runtime behavior is
limited to deterministic synthetic data and simple equal-weight research logic.

## Planned Modules

- `DataSource`: returns data visible at a requested decision time.
- `ValidatedDataSource`: wraps a data source and enforces point-in-time
  visibility at the provider boundary.
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
- UI clients must not contain strategy, risk, data-provider, broker, accounting,
  metric, or secret-handling logic.
- Configuration and secrets are separate: commit-safe run configuration can live
  in the repository; secret values must come from environment variables,
  gitignored `.env` files, or a secret manager.
- Execution must not connect to a real broker until explicitly allowed by a
  later readiness task.
- Accounting must not be modified to make a strategy look better.
- Documentation is the source of project context, not chat history.

## Contract Location

Core Protocols and dataclass payloads live in `src/qts/contracts.py`.
Commit-safe configuration loading lives in `src/qts/config.py`. Provider
visibility helpers live in `src/qts/providers.py`.

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

## Phase 8 Reporting Location

Structured report generation lives in `src/qts/reporting.py`:

- `stable_config_hash` produces stable hashes for config maps.
- `write_experiment_report` writes JSON and Markdown reports.
- Report payloads include git commit, config hash, data version, seed, date
  range, metrics, equity curve, final positions, and monthly returns.

Generated report artifacts live under `reports/<run_id>/`.

## Phase 9 Paper Trading Location

Paper trading lives in `src/qts/paper.py`:

- `PaperTradingConfig` requires `broker_submission="disabled"`.
- `PaperTradingEngine` reads data, generates signals and targets, creates
  simulated orders, runs risk checks, and writes local files.
- Orders are appended to `orders.jsonl`.
- Daily reports are written under `daily_reports/`.
- Failures are appended to `failures.jsonl` and re-raised.

No broker API client or real order submission path exists.
