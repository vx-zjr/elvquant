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

Status: Completed
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

## Task ID: QTS-004

Status: Completed
Phase: 4
Title: Add read-only historical data source

Scope:
- Implement a real historical-data `DataSource`.
- Replace only the data source for a smoke run.
- Do not modify `SimpleBacktester`.
- Do not modify strategies, risk, execution, or accounting behavior.
- Do not add ML.
- Do not connect to live broker APIs.

Files likely touched:
- `src/qts/`
- `tests/`
- `DATA_POLICY.md`
- `EXPERIMENTS.md`
- `RUNBOOK.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- `DATA_POLICY.md` documents source, fields, timezone, adjustment, missing data,
  and versioning before implementation.
- A read-only historical data source can run the equal-weight strategy.
- Honesty probes continue passing.
- Missing data raises or is explicitly handled; no silent filling.
- `EXPERIMENTS.md` records one real-data smoke run.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Update `DATA_POLICY.md` before code.
- Write tests before implementation.
- Preserve backtester, strategy, risk, execution, and accounting modules unless
  a test proves a narrow compatibility fix is required.

## Task ID: QTS-005

Status: Completed
Phase: 5
Title: Add first rule-based momentum strategy

Scope:
- Add a simple daily momentum `SignalModel`.
- Compare momentum results with the equal-weight baseline.
- Do not modify `SimpleBacktester`.
- Do not modify `SimpleAccountingLedger`.
- Do not modify `SimpleExecutionSimulator`.
- Do not add ML.
- Do not connect to live data or broker APIs.

Files likely touched:
- `src/qts/`
- `tests/`
- `CONTRACTS.md`
- `PROJECT.md`
- `EXPERIMENTS.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Strategy test uses known prices and verifies the strongest past performer is
  selected.
- Strategy reads only from `DataSnapshot`.
- End-to-end backtest passes.
- Report can compare momentum and equal-weight baseline metrics.
- `EXPERIMENTS.md` records parameters, results, and observations.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write the strategy test before implementation.
- Keep the strategy behind the `SignalModel` contract.
- Do not use future prices or full future price tables.

## Task ID: QTS-006

Status: Completed
Phase: 6
Title: Add explicit cost model and execution assumptions

Scope:
- Define a `CostModel` contract.
- Add fixed commission, proportional commission, and slippage assumptions.
- Ensure all costs enter `AccountingLedger`.
- Show total cost, cost-to-return ratio, and turnover in reports.
- Do not change strategy logic.
- Do not optimize parameters.
- Do not add ML.

Files likely touched:
- `src/qts/`
- `tests/`
- `CONTRACTS.md`
- `DATA_POLICY.md`
- `EXPERIMENTS.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Cost non-negative tests pass.
- No-cost and cost-enabled runs differ.
- Cost-enabled return is not higher than no-cost return.
- End-to-end backtest passes.
- `EXPERIMENTS.md` records cost assumptions.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing cost tests before implementation.
- Keep strategy code unchanged.
- Update contracts before implementing new cost interfaces.

## Task ID: QTS-007

Status: Completed
Phase: 7
Title: Expand basic risk controls

Scope:
- Strengthen `RiskManager` so any target or order path passes documented risk
  checks.
- Add tests for each risk rule.
- Report risk rejection counts and reasons.
- Do not change strategy logic.
- Do not add ML.
- Do not connect to live broker APIs.

Risk rules:
- No short positions.
- Single asset maximum weight 20%.
- Total target exposure maximum 95%.
- Daily turnover maximum 50%.
- Stop new opens after daily loss exceeds threshold.
- Reject missing or abnormal prices.

Files likely touched:
- `src/qts/`
- `tests/`
- `RISK_POLICY.md`
- `REVIEW.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Every risk rule has a passing test.
- Backtests still call `RiskManager`.
- Reports show risk rejection counts and reasons.
- `REVIEW.md` includes risk checks.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Update `RISK_POLICY.md` before implementation.
- Write failing risk tests before code changes.
- Keep strategy behavior unchanged.

## Task ID: QTS-008

Status: Completed
Phase: 8
Title: Add structured experiment records and report files

Scope:
- Generate run IDs.
- Record git commit, config hash, data version, random seed, and date range.
- Save machine-readable JSON and human-readable Markdown reports.
- Keep `EXPERIMENTS.md` as a summary linking to concrete report files.
- Do not change strategy logic.
- Do not make metrics look better by changing definitions.

Files likely touched:
- `src/qts/`
- `tests/`
- `reports/`
- `EXPERIMENTS.md`
- `RUNBOOK.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Same configuration produces a stable config hash.
- Report files are written to disk.
- JSON and Markdown report contents include required metadata and metrics.
- `RUNBOOK.md` explains report generation.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing report-file tests before implementation.
- Do not alter strategy logic or metrics definitions.

## Task ID: QTS-009

Status: Pending
Phase: 9
Title: Add paper trading mode

Scope:
- Add paper trading configuration.
- Generate target positions, simulated orders, risk results, and daily reports.
- Write orders only to local logs or files.
- Do not connect to real broker APIs.
- Do not submit real-money orders.
- Do not bypass risk.

Files likely touched:
- `src/qts/`
- `tests/`
- `RUNBOOK.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Multiple trading days can run without manual code changes.
- Failures are explicit and logged.
- Orders are written locally only.
- Daily paper reports are generated.
- `RUNBOOK.md` explains start, stop, and troubleshooting.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing paper-mode tests before implementation.
- Do not add broker keys or broker API clients.
- Keep risk checks mandatory.
