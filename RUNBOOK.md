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

## Troubleshooting

- If `python` is not available on Windows, try `py`.
- If imports fail, reinstall with `.venv\Scripts\python -m pip install -e ".[dev]"`.
- If CircleCI fails at dependency installation, compare its Python version with
  `requires-python` in `pyproject.toml`.

## Stop Procedure

No long-running service exists in Phase 0.
