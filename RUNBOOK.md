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

## Local Core API For Frontend Debugging

Start the independent API boundary used by `elvquant_front`:

```powershell
$env:ELVQUANT_API_SERVICE_TOKEN="dev-token"
.venv\Scripts\python -m uvicorn qts.api_app:app --reload --port 8000
```

The local frontend sends `X-Service-Token: dev-token` and
`X-Owner-User-Id: local-debug-user` by default. Change these values only through
environment variables, not committed source.

## Rust-Led Core Service Foundation

Rust source lives under `rust/`. The first service slice is intentionally small:
typed API/report contracts, deterministic portfolio math, workflow catalog, and
synthetic-demo compatible report JSON. Python remains the reference for trading
logic until parity tests cover the migrated behavior.

Expected command once Rust tooling is installed:

```powershell
cargo test --manifest-path rust\Cargo.toml
cargo run --manifest-path rust\Cargo.toml -p elvquant_core_service -- --host 127.0.0.1 --port 8010
```

If `cargo` is unavailable on this machine, record that limitation in the final
verification notes and keep Python tests as the active local gate.

## Commit-Safe Configuration

Load the example config without secrets:

```powershell
.venv\Scripts\python -c "from pathlib import Path; from qts.config import load_core_config; config=load_core_config(Path('configs/local.example.toml')); print(config.as_summary())"
```

Real API tokens must not be added to TOML/YAML config files. Use environment
variables, a gitignored `.env`, or a secret manager for secret values.

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
.venv\Scripts\python -c "from pathlib import Path; from qts.paper import run_synthetic_paper_demo; print(run_synthetic_paper_demo(output_dir=Path('paper_runs/synthetic-paper-demo')).text)"
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

## Stooq Real-Data Research

The example config is commit-safe and contains no API key. The current local
debug config uses `SPY.US`, `QQQ.US`, `IWM.US`, `TLT.US`, and `GLD.US` from
2015-01-01 through 2017-11-10, matching the available public Kaggle mirror of
Stooq-format US stocks and ETFs data.

```powershell
.venv\Scripts\python -c "from pathlib import Path; from qts.stooq import load_stooq_research_config; print(load_stooq_research_config(Path('configs/stooq_etf_momentum.example.toml')))"
```

Prepare normalized local CSV before research. Runtime snapshots must read only
the local normalized file. The easiest local-debug path is:

```powershell
.venv\Scripts\python -m pip install -e ".[data]"
.venv\Scripts\python scripts\prepare_kaggle_stooq_debug_data.py
.venv\Scripts\python -c "from pathlib import Path; from qts.stooq import load_stooq_research_config, run_stooq_etf_momentum_research; print(run_stooq_etf_momentum_research(load_stooq_research_config(Path('configs/stooq_etf_momentum.example.toml'))).text)"
```

This writes local, gitignored files:

- `data/raw/stooq/*_2015-01-01_2017-11-10.csv`
- `data/processed/stooq_etf_eod.csv`

Data source: `https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs`.
The data is Stooq-format daily OHLCV text. It is suitable for local debugging
and first research plumbing, not for production trading decisions.

Official Stooq direct downloads remain supported as a separate preparation
path:

```powershell
$env:STOOQ_API_KEY="<optional local key, never commit>"
.venv\Scripts\python -c "from pathlib import Path; from qts.stooq import cache_stooq_daily_csv; print(cache_stooq_daily_csv('SPY.US','2015-01-01','2017-11-10',Path('data/raw/stooq')))"
```

If Stooq returns a browser verification page or an API-key instruction page
instead of CSV, the downloader will fail intentionally. Get a key through
Stooq's account/download flow if you are allowed to use it, keep it in
`STOOQ_API_KEY` or a gitignored `.env`, use a browser/manual download for the
raw CSV, or switch to the next documented provider task. Never treat HTML as
market data.

If raw CSV files are manually available, normalize them into
`data/processed/stooq_etf_eod.csv` with `write_stooq_normalized_csv_from_files`,
then run:

```powershell
@'
from pathlib import Path
from qts.stooq import stooq_daily_csv_url, write_stooq_normalized_csv_from_files

assets = ("SPY.US", "QQQ.US", "IWM.US", "TLT.US", "GLD.US")
start = "2015-01-01"
end = "2017-11-10"
raw_paths = {
    asset: Path("data/raw/stooq") / f"{asset.lower().replace('.', '_')}_{start}_{end}.csv"
    for asset in assets
}
source_urls = {asset: stooq_daily_csv_url(asset, start, end) for asset in assets}
write_stooq_normalized_csv_from_files(
    raw_paths_by_asset=raw_paths,
    output_path=Path("data/processed/stooq_etf_eod.csv"),
    data_version=f"stooq-etf-eod-{start}-{end}-v1",
    source_urls=source_urls,
)
'@ | .venv\Scripts\python -

.venv\Scripts\python -c "from pathlib import Path; from qts.stooq import load_stooq_research_config, run_stooq_etf_momentum_research; print(run_stooq_etf_momentum_research(load_stooq_research_config(Path('configs/stooq_etf_momentum.example.toml'))).text)"
```

The Stooq research report records config hash, data file hash, data version,
sample splits, and cost assumptions. It is still research-only and not trading
advice.

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
