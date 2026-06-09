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
