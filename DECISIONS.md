# Decisions

## ADR-000: Start With Documentation and Tooling Only

Date: 2026-06-09

Decision: Phase 0 creates only the package scaffold, quality gates, CircleCI
configuration, and governance documents.

Rationale: The project must be understandable and testable before any trading
logic exists. This keeps the first commit low risk and gives later agents a
stable handoff point.

Consequences:
- No market data, strategy, risk, accounting, backtest, report, ML, or live
  trading implementation exists yet.
- Phase 1 must define contracts before implementations are added.
