# Architecture

## Phase 0 Boundary

The repository contains only scaffolding and governance documents. There are no
runtime trading modules yet.

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
