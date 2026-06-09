# Quant Trading Agent

A document-driven, test-first quantitative trading research system.

The first milestone is not profitability. The first milestone is a small,
auditable system that avoids look-ahead bias, keeps risk controls explicit, and
can be handed to a new agent through repository documents alone.

## Current Scope

The document-defined business plan is complete through Phase 12:

- Python package structure under `src/qts`
- pytest, Ruff, and mypy configuration
- required project governance documents
- CircleCI configuration for the same local quality gates
- deterministic synthetic backtests
- fixed historical CSV smoke data
- rule-based momentum and deterministic ML-style research signals
- explicit cost, risk, reporting, readiness, and local paper-trading controls
- manual-confirmation dry-run order recording

The project still has no broker integration, no live market data feed, no stored
secrets, and no real-money order submission path.

## Setup

On Windows:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -e ".[dev]"
```

On macOS or Linux:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality Gates

```powershell
.venv\Scripts\python -m pytest
.venv\Scripts\python -m ruff check
.venv\Scripts\python -m mypy
```

Use the equivalent activated-environment commands on macOS or Linux.

## Agent Protocol

Before starting a task, read the root documents listed in `PROJECT.md` and
`TASKS.md`. Execute only the first task in `TASKS.md` with `Status: Pending`.
Write tests first, keep the system runnable, and update the documents before
ending the task.
