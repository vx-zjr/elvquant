# Contracts

Core contracts live in `src/qts/contracts.py`. They define payload dataclasses
and Protocol interfaces only; they do not include implementations, strategies,
data sources, or a backtest loop.

## Payload Types

- `DataSnapshot`: data visible at one decision time, including asset IDs,
  prices, data version, and optional features.
- `SignalSet`: research scores produced from one visible snapshot.
- `TargetPortfolio`: target asset weights for one decision time.
- `Order`: simulated order intent derived from approved targets.
- `RiskDecision`: risk approval status and explicit reasons.
- `Fill`: simulated execution fill and non-negative cost field.
- `LedgerState`: cash, positions, equity, and cumulative cost at one time.
- `BacktestResult`: run ID, config summary, equity curve, and metrics.
- `Report`: human-readable text and metrics for one run.

## Protocol Interfaces

- `DataSource.snapshot(decision_time) -> DataSnapshot`
- `SignalModel.generate(snapshot) -> SignalSet`
- `PortfolioConstructor.construct(snapshot, signals) -> TargetPortfolio`
- `RiskManager.evaluate(snapshot, target, orders) -> RiskDecision`
- `Backtester.run(start, end, config) -> BacktestResult`
- `ExecutionSimulator.simulate(snapshot, orders) -> Sequence[Fill]`
- `AccountingLedger.apply_fills(previous_state, fills, snapshot) -> LedgerState`
- `Reporter.build(result) -> Report`

## Time Semantics

Every Protocol docstring must mention decision time, visible data, and the ban
on future data. A caller may only pass data that would have been visible at the
decision time being evaluated. Implementations added in later phases must keep
that invariant and add tests when they introduce behavior.
