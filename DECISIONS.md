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
