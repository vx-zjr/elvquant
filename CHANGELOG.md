# Changelog

## 2026-06-09

- Added a manual-confirmation dry-run order workflow that enforces kill switch,
  risk approval, and human confirmation before writing traceable local order
  records with broker submission disabled.
- Added non-broker readiness controls: kill switch, order amount limits, local
  confirmation records, and readiness controls.
- Updated readiness report to ready after blocker remediation, while keeping
  broker integration out of scope.
- Added live-readiness review generation and a tracked blocked readiness report.
- Explicitly blocked live trading until readiness gaps are remediated.
- Added a deterministic ML-style research signal layer with chronological split,
  feature-visibility checks, reproducible training, and ML-vs-momentum
  comparison reporting.
- Added local-only paper trading mode with simulated orders, mandatory risk
  checks, local JSONL order logs, Markdown daily reports, and explicit failure
  logs.
- Added structured JSON and Markdown experiment report generation with git
  commit, config hash, data version, seed, date range, metrics, holdings, equity
  curve, and monthly returns.
- Added a tracked momentum smoke report under `reports/`.
- Expanded configurable risk controls for single-asset exposure, total exposure,
  turnover, daily loss stops, and missing or abnormal prices.
- Added risk rejection counts and reason metrics to backtest reports.
- Added explicit fixed commission, proportional commission, slippage, and
  composite cost models behind a `CostModel` contract.
- Updated execution/reporting so costs enter fills, ledger cumulative cost,
  `total_cost`, and `cost_to_return`.
- Added a research-only momentum signal that ranks assets from visible trailing
  return features in `DataSnapshot`.
- Added a trailing-return feature data source wrapper and a report comparing
  momentum with the equal-weight baseline on the fixed FRED sample.
- Added a read-only historical CSV data source and a fixed FRED sample covering
  `SP500` and `NASDAQCOM` index levels from 2024-01-02 to 2024-01-10.
- Added a historical smoke run that reuses the equal-weight pipeline without
  changing the backtester, strategy, risk, execution, or accounting modules.
- Added honesty probe tests for cost drag, future-data absence, accounting
  identity, non-negative costs, no-trade position stability, risk rejection, and
  run metadata.
- Added a non-negative `cost_rate` option to the simple execution simulator so
  cost-drag probes can run without a full cost model.
- Added the thinnest synthetic end-to-end loop with deterministic fake prices,
  equal-weight signals, basic no-short/no-overallocation risk checks, simulated
  fills, simple accounting, backtest metrics, and a text report.
- Added `run.py`, which prints `net_value`, `total_return`, `max_drawdown`, and
  `turnover` for the synthetic demo.
- Defined core Protocol interfaces and dataclass payloads for data snapshots,
  signals, target portfolios, risk decisions, orders, fills, ledger states,
  backtest results, and reports.
- Documented contract-level time semantics requiring visible data only and
  forbidding future data.
- Created the initial project scaffold.
- Added pytest, Ruff, mypy, and CircleCI quality-gate configuration.
- Added required root documents for project context, architecture, contracts,
  data policy, risk policy, tasks, decisions, review, runbook, experiments, and
  changelog.
- Added a minimal scaffold test proving the package imports and required
  documents exist.
