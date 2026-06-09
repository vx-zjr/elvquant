# Runbook

## Local Setup

Windows:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[dev]"
```

macOS or Linux:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality Checks

Windows:

```powershell
.venv\Scripts\python -m pytest
.venv\Scripts\python -m ruff check
.venv\Scripts\python -m mypy
```

## Synthetic Demo

Windows:

```powershell
.venv\Scripts\python run.py
```

Expected output includes:

- `net_value`
- `total_return`
- `max_drawdown`
- `turnover`
- `total_cost`
- `cost_to_return`

## Historical FRED Smoke Run

Windows:

```powershell
.venv\Scripts\python -c "from qts.historical import run_historical_smoke; print(run_historical_smoke().text)"
```

This reads `data/historical/fred_index_sample.csv` and does not connect to FRED
or any broker at runtime.

## Momentum Smoke Run

Windows:

```powershell
.venv\Scripts\python -c "from qts.strategies import run_momentum_smoke; print(run_momentum_smoke().text)"
.venv\Scripts\python -c "from qts.strategies import compare_momentum_to_equal_weight; print(compare_momentum_to_equal_weight().text)"
```

These commands use the fixed FRED sample and do not connect to live data or a
broker.

## Cost Smoke Run

Use the Python API to create `CompositeCostModel` with fixed commission,
proportional commission, and slippage. A minimal command is:

```powershell
.venv\Scripts\python -c "from qts.costs import CompositeCostModel, FixedCommissionCostModel, ProportionalCommissionCostModel, SlippageCostModel; print('cost models import ok')"
```

## Structured Report Generation

Windows:

```powershell
.venv\Scripts\python -c "from dataclasses import replace; from pathlib import Path; from qts.reporting import write_experiment_report; from qts.strategies import build_momentum_smoke_backtester; bt,start,end,ds=build_momentum_smoke_backtester(); result=bt.run(start=start,end=end,config={'seed':'momentum-fred-smoke','data_source':'fred_csv_trailing_return','strategy':'momentum','feature_name':'momentum_1','lookback_observations':'1','data_version':ds.data_version}); result=replace(result, run_id=f'momentum-fred-{start:%Y%m%d}-{end:%Y%m%d}'); print(write_experiment_report(result, Path('reports'), start, end))"
```

This writes both JSON and Markdown report files under `reports/<run_id>/`.

## Paper Trading

Start a local synthetic paper run:

```powershell
.venv\Scripts\python -c "from datetime import UTC, datetime, timedelta; from pathlib import Path; from qts.paper import PaperTradingConfig, PaperTradingEngine; from qts.simple import BasicRiskManager, EqualWeightSignal, SimpleAccountingLedger, SimpleExecutionSimulator, SimplePortfolioConstructor, SyntheticDataSource; start=datetime(2026,1,1,tzinfo=UTC); engine=PaperTradingEngine(data_source=SyntheticDataSource(asset_ids=('AAA','BBB'), start=start, periods=4), signal_model=EqualWeightSignal(), portfolio_constructor=SimplePortfolioConstructor(), risk_manager=BasicRiskManager(), execution_simulator=SimpleExecutionSimulator(), ledger=SimpleAccountingLedger(), config=PaperTradingConfig(output_dir=Path('paper_runs/synthetic-paper-demo'), initial_cash=10000.0)); print(engine.run_days(tuple(start + timedelta(days=i) for i in range(3))))"
```

Stop procedure: no daemon is started; stop by not invoking the next run. Delete
or archive local paper output only after reviewing it.

Troubleshooting: inspect `paper_runs/<run>/failures.jsonl` for explicit failure
records. Paper mode must never require broker credentials.

## ML Research Comparison

Windows:

```powershell
.venv\Scripts\python -c "from qts.ml import compare_ml_to_momentum; print(compare_ml_to_momentum().text)"
```

This is a research comparison only and does not alter risk, execution,
accounting, or live trading behavior.

## Live Readiness Review

Windows:

```powershell
.venv\Scripts\python -c "from pathlib import Path; from qts.readiness import generate_readiness_report; print(generate_readiness_report(Path('reports/readiness'), tests_passed=True).markdown_path)"
```

Current status can be regenerated from the declared controls. Broker integration
and real order submission remain out of scope.

## Manual Confirmation Dry Run

Use `ManualOrderWorkflow` from `qts.manual` to record a manually confirmed order
recommendation locally. The workflow requires:

- a prior `RiskDecision` with `allowed=True`
- a `ManualConfirmation` with `decision="approved"`
- a disabled kill switch
- `dry_run=True`

Minimal Windows example:

```powershell
.venv\Scripts\python -c "from datetime import UTC, datetime; from pathlib import Path; from qts.contracts import Order, RiskDecision; from qts.manual import ManualConfirmation, ManualOrderWorkflow, OrderRecommendation; as_of=datetime(2026,1,1,tzinfo=UTC); rec=OrderRecommendation(order_id='manual-demo-1', order=Order(as_of=as_of, asset_id='AAA', quantity=1.0, reason='demo'), source_strategy='demo-strategy', signal={'AAA':1.0}, target_weights={'AAA':0.1}, risk_decision=RiskDecision(as_of=as_of, allowed=True, reasons=())); conf=ManualConfirmation(confirmed_by='operator', confirmed_at=as_of, decision='approved', notes='dry run only'); print(ManualOrderWorkflow(output_dir=Path('paper_runs/manual-demo')).submit(rec, conf))"
```

This writes `manual_orders.jsonl` and always records
`broker_submission: disabled`.

## Emergency Stop

Use `KillSwitch(enabled=True, reason="...")` from `qts.controls` in any manual
or paper workflow. A raised kill-switch error must stop submission attempts.

Manual dry-run workflows should be stopped by enabling the kill switch and by
not creating new confirmation records. No background daemon or broker session is
started by this project.

## Troubleshooting

- If `python` is not available on Windows, try `py`.
- If imports fail, reinstall with `.venv\Scripts\python -m pip install -e ".[dev]"`.
- If CircleCI fails at dependency installation, compare its Python version with
  `requires-python` in `pyproject.toml`.
- If a historical CSV snapshot fails, check for missing dates, missing assets,
  blank values, or FRED `.` values.

## Stop Procedure

No long-running service exists. Stop by not invoking the next paper or manual
run, and enable the kill switch before any review session that should reject
submissions.
