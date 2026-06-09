# Experiments

## 2026-06-09 Synthetic Smoke Run

- Task: QTS-002
- Command: `.venv\Scripts\python run.py`
- run_id: `synthetic-20260101-20260106`
- Data source: `SyntheticDataSource`
- Data version: `synthetic-v1`
- Data range: 2026-01-01 UTC through 2026-01-06 UTC
- Config: `seed=deterministic`, `initial_cash=10000.00`
- Metrics:
  - net_value: 1.053166
  - total_return: 0.053166
  - max_drawdown: 0.000000
  - turnover: 1.033690
- Observation: This is only a synthetic engineering smoke test, not evidence of
  a profitable strategy.

## 2026-06-09 FRED Historical Smoke Run

- Task: QTS-004
- Command: `.venv\Scripts\python -c "from qts.historical import run_historical_smoke; print(run_historical_smoke().text)"`
- run_id: `historical-fred-20240102-20240110`
- Data source: `CsvHistoricalDataSource`
- Raw source: FRED CSV export for `SP500` and `NASDAQCOM`
- Repository sample: `data/historical/fred_index_sample.csv`
- Data version: `fred-index-sample-20240102-20240110-v1`
- Data range: 2024-01-02 UTC through 2024-01-10 UTC
- Config: `seed=fred-smoke`, `initial_cash=10000.00`
- Metrics:
  - net_value: 1.021342
  - total_return: 0.021342
  - max_drawdown: -0.004474
  - turnover: 1.005773
- Observation: The existing equal-weight smoke run works on fixed real
  historical index levels. This is not a production strategy or trading advice.

## 2026-06-09 Momentum Strategy Smoke Run

- Task: QTS-005
- Command: `.venv\Scripts\python -c "from qts.strategies import run_momentum_smoke; print(run_momentum_smoke().text)"`
- run_id: `momentum-fred-20240102-20240110`
- Data source: `CsvHistoricalDataSource` plus `TrailingReturnFeatureDataSource`
- Data version: `fred-index-sample-20240102-20240110-v1`
- Strategy: `MomentumSignal`
- Parameters: `feature_name=momentum_1`, `lookback_observations=1`, `top_n=1`
- Metrics:
  - net_value: 1.022120
  - total_return: 0.022120
  - max_drawdown: 0.000000
  - turnover: 3.033859
- Equal-weight comparison:
  - equal_weight_net_value: 1.021342
  - momentum_net_value: 1.022120
  - equal_weight_total_return: 0.021342
  - momentum_total_return: 0.022120
  - momentum_minus_equal_weight_return: 0.000778
- Observation: Momentum was slightly higher on this tiny sample, but the sample
  is far too small for investment conclusions.
