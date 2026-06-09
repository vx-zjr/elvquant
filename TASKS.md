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

Status: Pending
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
