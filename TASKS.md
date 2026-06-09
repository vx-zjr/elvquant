# Tasks

## Task ID: QTS-000

Status: Completed
Phase: 0
Title: Create project scaffold and documentation foundation

Scope:
- Create Python package structure.
- Configure pytest, Ruff, mypy, and CircleCI quality gates.
- Create required root project documents.
- Add a minimal scaffold test.
- Do not implement quantitative trading business logic.

Files touched:
- `.circleci/config.yml`
- `.gitignore`
- `README.md`
- `pyproject.toml`
- `src/qts/__init__.py`
- `src/qts/py.typed`
- `tests/test_scaffold.py`
- Root project documents

Acceptance criteria:
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.
- No real trading logic exists.
- Documentation lets the next agent understand the current stage.

## Task ID: QTS-001

Status: Completed
Phase: 1
Title: Define core Protocol interfaces

Scope:
- Create interface definitions only.
- No implementation.
- No strategy.
- No real data.
- No backtest loop.

Files likely touched:
- `src/qts/contracts.py`
- `tests/test_contracts.py`
- `CONTRACTS.md`
- `CHANGELOG.md`
- `DECISIONS.md`
- `TASKS.md`

Acceptance criteria:
- Interfaces import successfully.
- Docstrings explain time semantics and forbid future data.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.
- `CONTRACTS.md` matches code.

Agent instructions:
- Read `PROJECT.md`, `ARCHITECTURE.md`, `CONTRACTS.md`, and `DATA_POLICY.md`
  first.
- State the task boundary before editing.
- Write tests first.
- Update docs before final response.

## Task ID: QTS-002

Status: Completed
Phase: 2
Title: Implement thinnest synthetic end-to-end loop

Scope:
- Implement synthetic data only.
- Implement simple equal-weight signal behavior.
- Implement the minimum portfolio, risk, execution, ledger, backtest, and report
  components needed for one end-to-end run.
- Add `run.py` or a CLI entrypoint.
- Do not use real market data.
- Do not add ML.

Files likely touched:
- `src/qts/`
- `tests/`
- `run.py`
- `CHANGELOG.md`
- `RUNBOOK.md`
- `EXPERIMENTS.md`
- `TASKS.md`

Acceptance criteria:
- End-to-end test passes.
- `python run.py` or documented equivalent prints net value, total return,
  max drawdown, and turnover.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.
- Results use only synthetic data.

Agent instructions:
- Read root documents first.
- Write the end-to-end test before implementation.
- Keep implementations behind the contracts.
- Update docs before final response.

## Task ID: QTS-003

Status: Pending
Phase: 3
Title: Add honesty probe tests

Scope:
- Add tests that catch self-deception and low-level accounting/risk mistakes.
- Do not add new strategies.
- Do not use real market data.
- Do not add ML.

Required probes:
- Zero-signal or equal-weight behavior does not get rich from nowhere after
  costs.
- A cheating future-price strategy must be caught by tests.
- Cash plus position market value equals total equity.
- Costs cannot be negative.
- Positions do not change when there are no trades.
- Risk rejects targets above the maximum position.
- Backtest results include `run_id` and config summary.

Files likely touched:
- `tests/`
- `src/qts/`
- `CONTRACTS.md`
- `DECISIONS.md`
- `REVIEW.md`
- `TASKS.md`
- `CHANGELOG.md`

Acceptance criteria:
- All honesty probes pass.
- `REVIEW.md` requires honesty probes before completion.
- `TASKS.md` next task allows real historical data only after probes pass.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing probe tests before changing implementation.
- If interfaces cannot express a rule, update `CONTRACTS.md` and
  `DECISIONS.md` before code changes.
- Keep the scope limited to probes and minimum fixes.
