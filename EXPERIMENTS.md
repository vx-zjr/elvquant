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
- Structured reports:
  - JSON: `reports/momentum-fred-20240102-20240110/momentum-fred-20240102-20240110.json`
  - Markdown: `reports/momentum-fred-20240102-20240110/momentum-fred-20240102-20240110.md`
- config_hash: `1f779b266139`
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

## 2026-06-09 Explicit Cost Smoke Run

- Task: QTS-006
- Command: inline Python smoke run using `CompositeCostModel`
- run_id: `synthetic-20260101-20260106`
- Data source: `SyntheticDataSource`
- Cost assumptions:
  - fixed commission: 1.0 per non-zero order
  - proportional commission: 0.001 of absolute traded notional
  - slippage: 0.002 of absolute traded notional
- Metrics:
  - net_value: 1.048410
  - total_return: 0.048410
  - max_drawdown: -0.003340
  - turnover: 1.037360
  - total_cost: 46.120798
  - cost_to_return: 0.095272
- Observation: Cost-enabled return is lower than the no-cost synthetic run, as
  expected.

## 2026-06-09 Strict Risk Smoke Run

- Task: QTS-007
- Command: inline Python smoke run using strict `BasicRiskManager`
- run_id: `synthetic-20260101-20260104`
- Risk settings:
  - max_asset_weight: 0.2
  - max_gross_exposure: 0.95
  - max_daily_turnover: 0.5
  - daily_loss_limit: 0.05
- Metrics:
  - net_value: 1.000000
  - total_return: 0.000000
  - risk_rejections: 3
  - risk_rejection_reason_daily_turnover_exceeds_limit: 3
  - risk_rejection_reason_single_asset_target_weight_exceeds_limit__aaa__bbb__ccc: 3
  - risk_rejection_reason_total_exposure_exceeds_100__or_configured_limit: 3
- Observation: Strict limits blocked all equal-weight rebalance attempts for the
  three-asset synthetic demo, and the report exposed the reasons.

## 2026-06-09 Synthetic Paper Trading Smoke Run

- Task: QTS-009
- Command: inline Python paper run over three synthetic days
- Output directory: `paper_runs/synthetic-paper-demo`
- Order log: `paper_runs/synthetic-paper-demo/orders.jsonl`
- Daily reports:
  - `paper_runs/synthetic-paper-demo/daily_reports/2026-01-01.md`
  - `paper_runs/synthetic-paper-demo/daily_reports/2026-01-02.md`
  - `paper_runs/synthetic-paper-demo/daily_reports/2026-01-03.md`
- Broker submission: disabled
- Observation: Multiple paper days ran without manual code changes, generated
  local simulated orders, and produced daily reports.

## 2026-06-09 ML Research Comparison

- Task: QTS-010
- Command: `.venv\Scripts\python -c "from qts.ml import compare_ml_to_momentum; print(compare_ml_to_momentum().text)"`
- run_id: `comparison-ml-momentum-20240102-20240110`
- Data version: `fred-index-sample-20240102-20240110-v1`
- Feature version: `momentum_1-v1`
- Seed: 11
- Metrics:
  - ml_net_value: 1.029725
  - momentum_net_value: 1.022120
  - ml_total_return: 0.029725
  - momentum_total_return: 0.022120
  - ml_minus_momentum_return: 0.007605
- Observation: The ML-style model is deterministic and slightly higher on this
  tiny sample. This is not sufficient evidence for live trading.

## 2026-06-09 Stooq Real-Data Workflow Implementation

- Task: Real-data provider v1
- Config: `configs/stooq_etf_momentum.example.toml`
- Provider: Stooq EOD, normalized local CSV
- Intended universe: `SPY.US`, `QQQ.US`, `IWM.US`, `TLT.US`, `GLD.US`
- Intended data range: 2015-01-01 through 2025-12-31
- Sample split:
  - train: 2015-01-01 to 2022-01-01
  - validation: 2022-01-01 to 2024-01-01
  - test: 2024-01-01 to 2025-12-31
- Strategy: `MomentumSignal` versus `EqualWeightSignal`
- Costs:
  - fixed commission: 1.0 per non-zero order
  - proportional commission: 0.0005 of absolute traded notional
  - slippage: 0.001 of absolute traded notional
- Report path when local data exists:
  `reports/stooq-etf-momentum-20150101-20251231/`
- Observation: Stooq direct scripted requests can return a browser verification
  page in this environment. The downloader rejects non-CSV responses. Full
  research should be run after valid Stooq CSV files are cached or manually
  downloaded into `data/raw/stooq/` and normalized into
  `data/processed/stooq_etf_eod.csv`.

## 2026-06-09 Live Readiness Review

- Task: QTS-011
- Command: `.venv\Scripts\python -c "from pathlib import Path; from qts.readiness import generate_readiness_report; print(generate_readiness_report(Path('reports/readiness'), tests_passed=True).markdown_path)"`
- Report: `reports/readiness/live_readiness.md`
- Status: ready
- Live trading allowed: true
- Blocker count: 0
- Observation: Non-broker readiness controls are present. Broker integration and
  real order submission still remain out of scope.
