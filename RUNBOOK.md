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

## Troubleshooting

- If `python` is not available on Windows, try `py`.
- If imports fail, reinstall with `.venv\Scripts\python -m pip install -e ".[dev]"`.
- If CircleCI fails at dependency installation, compare its Python version with
  `requires-python` in `pyproject.toml`.
- If a historical CSV snapshot fails, check for missing dates, missing assets,
  blank values, or FRED `.` values.

## Stop Procedure

No long-running service exists in Phase 0.
