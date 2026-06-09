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

## ADR-001: Use Protocols and Frozen Dataclasses for Core Boundaries

Date: 2026-06-09

Decision: Core module boundaries are expressed as `typing.Protocol`
interfaces, and cross-module payloads are frozen dataclasses.

Rationale: Protocols keep implementations swappable without inheritance, while
frozen dataclasses make payloads explicit and easy to inspect in tests and
reports. The contracts also force each module to receive only visible data for a
decision time.

Consequences:
- Later implementations must conform to the Protocol method signatures.
- Interface changes must update `CONTRACTS.md`, tests, and this decision log.
- Runtime behavior remains absent until the Phase 2 task.

## ADR-002: Use a Deterministic Synthetic Loop Before Real Data

Date: 2026-06-09

Decision: Phase 2 implements a deterministic synthetic end-to-end loop with
equal-weight signals, basic no-short/no-overallocation risk checks, next-day
synthetic execution, simple accounting, and a compact text report.

Rationale: A small fake-data loop proves the pipeline can run without
introducing real market data, broker dependencies, ML, or production strategy
logic.

Consequences:
- Results are engineering smoke tests, not trading evidence.
- `SyntheticDataSource` is the only data source allowed until the Phase 4 task.
- Phase 3 must add honesty probes before any real historical data is introduced.

## ADR-003: Add Honesty Probes Before Real Data

Date: 2026-06-09

Decision: Phase 3 adds automated honesty probes for cost drag, future data
absence, accounting identity, non-negative costs, no-trade position stability,
risk rejection, and run metadata.

Rationale: The project should prove it can catch low-level mistakes before any
real historical data is introduced.

Consequences:
- `REVIEW.md` now requires honesty probes to pass.
- `SimpleExecutionSimulator` accepts a non-negative `cost_rate` so tests can
  prove flat-price equal-weight runs do not get rich after costs.
- Real historical data work may begin only after these probes remain green.

## ADR-004: Use a Fixed FRED CSV Sample for Historical Smoke Runs

Date: 2026-06-09

Decision: Phase 4 uses a small normalized CSV sample from FRED series `SP500`
and `NASDAQCOM` for a read-only historical data smoke test.

Rationale: A fixed local sample keeps tests deterministic and avoids runtime
network access, API keys, and broker dependencies while proving the pipeline can
consume real historical index levels.

Consequences:
- The sample is engineering test data, not live trading input.
- Missing dates and missing values raise explicit errors.
- Future real data sources must document source, fields, timezone, adjustment,
  missing-value, and versioning rules before implementation.

## ADR-005: Keep Momentum as a Snapshot-Only Research Signal

Date: 2026-06-09

Decision: The first rule strategy is `MomentumSignal`, which ranks assets using
trailing-return features already present in `DataSnapshot`.

Rationale: This keeps strategy logic behind the `SignalModel` contract and
prevents the strategy from reading full price tables or future observations.

Consequences:
- `TrailingReturnFeatureDataSource` is responsible for deriving visible past
  return features.
- Momentum is compared with equal weight as an engineering research comparison,
  not as trading advice.
- Backtester, execution, accounting, and risk modules remain unchanged.

## ADR-006: Model Costs Explicitly Before More Risk Expansion

Date: 2026-06-09

Decision: Phase 6 introduces a `CostModel` contract with fixed commission,
proportional commission, slippage, and composite implementations.

Rationale: Cost assumptions must be visible and testable before interpreting
strategy results or strengthening risk controls.

Consequences:
- Execution fills carry explicit non-negative costs.
- Accounting accumulates costs without strategy involvement.
- Reports include `total_cost` and `cost_to_return`.
- Strategy modules remain unchanged.

## ADR-007: Make Risk Rejections Reportable

Date: 2026-06-09

Decision: Phase 7 keeps risk checks configurable in `BasicRiskManager` and
records rejection counts and reason counts in backtest metrics.

Rationale: Risk controls are only useful if a report can explain what was
blocked and why.

Consequences:
- `RiskManager.evaluate` accepts optional portfolio state for turnover and daily
  loss checks.
- `SimpleBacktester` passes current ledger state to risk evaluation.
- `SimpleReporter` includes `risk_rejections` and reason metrics.

## ADR-008: Store Structured Reports as Versioned Artifacts

Date: 2026-06-09

Decision: Phase 8 writes JSON and Markdown report artifacts under
`reports/<run_id>/` and tracks them in git.

Rationale: Report files make experiments reviewable without rerunning code and
connect results to code version, config hash, data version, and seed.

Consequences:
- `reports/` is no longer ignored.
- `EXPERIMENTS.md` remains a summary and links to concrete report files.
- Future report generators must avoid changing metric definitions to improve
  presentation.

## ADR-009: Paper Trading Is Local-Only

Date: 2026-06-09

Decision: Phase 9 paper trading writes simulated orders, daily reports, and
failure logs to local files only.

Rationale: The project must rehearse daily operation before any broker
integration or real-money order path exists.

Consequences:
- `PaperTradingConfig` rejects broker submission modes other than `disabled`.
- Paper orders include `broker_submission: disabled`.
- Risk checks remain mandatory before simulated orders are logged.

## ADR-010: Keep ML Behind SignalModel

Date: 2026-06-09

Decision: Phase 10 adds a deterministic ML-style research signal that still
returns `SignalSet` through the `SignalModel` contract.

Rationale: ML can be evaluated as one signal source without changing execution,
accounting, risk, or backtest mechanics.

Consequences:
- Chronological split and feature-visibility tests are mandatory.
- ML comparison reports are research observations, not trading advice.
- The system remains unable to submit live orders.

## ADR-011: Block Live Trading Until Readiness Gaps Are Remediated

Date: 2026-06-09

Decision: The readiness review marks live trading as blocked and forbids moving
to live order submission work.

Rationale: Required controls such as kill switch, order amount limits, abnormal
alerting, order traceability, recovery, human confirmation, and sufficient paper
observation are incomplete.

Consequences:
- `reports/readiness/live_readiness.md` is the current readiness authority.
- The next task must remediate blockers without adding broker integration.
- Phase 12 live-order workflow remains blocked until readiness passes.
