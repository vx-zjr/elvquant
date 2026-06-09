# Changelog

## 2026-06-09

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
