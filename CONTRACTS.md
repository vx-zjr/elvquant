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
- `RiskManager.evaluate(snapshot, target, orders, portfolio_state=None) -> RiskDecision`
- `Backtester.run(start, end, config) -> BacktestResult`
- `ExecutionSimulator.simulate(snapshot, orders) -> Sequence[Fill]`
- `CostModel.estimate(order, price) -> float`
- `AccountingLedger.apply_fills(previous_state, fills, snapshot) -> LedgerState`
- `Reporter.build(result) -> Report`

## CostModel Semantics

`CostModel.estimate(order, price)` returns a non-negative cost estimate for a
visible order and execution price. Cost models must not inspect future prices,
strategy internals, or account secrets. All estimated costs must enter `Fill.cost`
and then `AccountingLedger.cumulative_cost`.

## RiskManager Semantics

`RiskManager.evaluate(...)` may receive the latest `LedgerState` as
`portfolio_state`. Risk checks that need turnover, held positions, or daily loss
must use only this state plus the current visible `DataSnapshot`; they must not
query future prices or strategy internals.

## SignalModel Semantics

`SignalModel.generate(snapshot)` may only use fields present in the supplied
`DataSnapshot`. For Phase 5, `MomentumSignal` reads a trailing-return feature
such as `momentum_1` from `DataSnapshot.features[asset_id]` and returns positive
scores only for the selected top-ranked assets. It must not load a full price
table, query a data source, or inspect future prices.

For Phase 10, `SimpleMLSignalModel` is an ML-style research model that still
obeys the same `SignalModel` contract. Training helpers must use chronological
splits and must reject features whose visible time is after the snapshot time.

## Time Semantics

Every Protocol docstring must mention decision time, visible data, and the ban
on future data. A caller may only pass data that would have been visible at the
decision time being evaluated. Implementations added in later phases must keep
that invariant and add tests when they introduce behavior.

## Provider Boundary Semantics

Every real data provider must be validated at the interface boundary before
strategy code can consume its output. `ValidatedDataSource` enforces that a
snapshot is visible at the requested decision time, carries a non-empty
`data_version`, and includes finite positive prices for all declared assets.

Synthetic and CSV sources are stubs behind the same `DataSource` contract. Add
one real provider only when there is a concrete need; do not create unused
adapters in advance.

## UI Boundary Semantics

UI clients are not core modules. A UI may choose a commit-safe config, call a
public core entrypoint, and render returned reports or local artifacts. It must
not implement strategy selection logic, data normalization, risk decisions,
order generation, broker routing, accounting, metric calculation, or secret
loading.
