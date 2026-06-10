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

Status: Completed
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

## Task ID: QTS-010

Status: Completed
Phase: 10
Title: Add ML signal research module

Scope:
- Add an ML-style research signal module that still obeys `SignalModel`.
- Use time-based train, validation, and test splits.
- Record feature version, data version, model parameters, and random seed.
- Compare ML output with the rule-based momentum strategy.
- Do not modify `SimpleBacktester`.
- Do not modify risk, execution, or accounting.
- Do not connect to live trading.

Files likely touched:
- `src/qts/`
- `tests/`
- `PROJECT.md`
- `CONTRACTS.md`
- `EXPERIMENTS.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Time split tests pass.
- Feature no-future-data tests pass.
- Model results are reproducible.
- Report compares ML versus rule strategy.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing ML research tests before implementation.
- Keep ML behind `SignalModel`.
- Do not tune on the test set.

## Task ID: QTS-011

Status: Completed
Phase: 11
Title: Generate live-readiness review

Scope:
- Generate a readiness report from `REVIEW.md`, `RISK_POLICY.md`, and
  `RUNBOOK.md`.
- Do not implement automated live trading.
- List blockers that prevent live trading.
- Stop further live-order development if blockers exist.

Files likely touched:
- `src/qts/`
- `tests/`
- `reports/`
- `REVIEW.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Readiness report is generated.
- Report states whether tests pass.
- Report covers kill switch, order limits, loss limits, alerts, order
  traceability, recovery, API key management, human confirmation, and paper
  observation.
- Blocking items are explicit.
- No live order implementation is added.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing readiness-report tests before implementation.
- Do not add broker APIs or live order submission.

## Task ID: QTS-012

Status: Completed
Phase: 11 remediation
Title: Remediate live-readiness blockers without broker integration

Scope:
- Add non-broker controls for readiness blockers.
- Implement kill switch design.
- Add order amount limits.
- Add abnormal alert logging.
- Improve order source traceability.
- Add stop and recovery state handling.
- Add human confirmation records for simulated/manual review only.
- Do not connect to broker APIs.
- Do not submit real-money orders.

Files likely touched:
- `src/qts/`
- `tests/`
- `RISK_POLICY.md`
- `RUNBOOK.md`
- `REVIEW.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Readiness report blockers are reduced or resolved without live broker code.
- Kill switch tests pass.
- Order limit tests pass.
- Alert log tests pass.
- Order traceability tests pass.
- Recovery tests pass.
- Human confirmation record tests pass.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing remediation tests before implementation.
- Keep broker submission disabled.
- Do not implement real live order submission.

## Task ID: QTS-013

Status: Completed
Phase: 12
Title: Add manual-confirmation dry-run order workflow

Scope:
- Generate order recommendations.
- Run risk checks before confirmation.
- Require human confirmation records before submit.
- Keep default mode as dry-run.
- Add kill switch enforcement.
- Real submission must remain disabled unless explicitly enabled in future work.
- Do not store plaintext secrets.
- Do not add broker API clients.

Files likely touched:
- `src/qts/`
- `tests/`
- `RUNBOOK.md`
- `CHANGELOG.md`
- `TASKS.md`

Acceptance criteria:
- Dry-run tests pass.
- Risk rejection prevents submit.
- Kill switch prevents submit.
- Missing human confirmation prevents submit.
- Confirmed dry-run records source strategy, signal, target, risk result,
  confirmer, and confirmation time.
- `RUNBOOK.md` documents emergency stop.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Agent instructions:
- Write failing manual-confirmation tests before implementation.
- Keep broker submission disabled by default.
- Do not add real broker clients or secrets.

Completion note:
- All tasks defined in the source plan are complete.
- Future work must start as a new documented task and must not enable broker
  submission without explicit new scope, tests, risk review, and secret
  management design.

## Task ID: QTS-014

Status: Completed
Phase: Core split
Title: Establish core/UI boundary and commit-safe configuration

Scope:
- Reframe the repository as `elvquant_core`.
- Document that UI clients are thin replaceable adapters and cannot contain
  trading business logic.
- Add commit-safe config loading that rejects secret-like keys.
- Add provider visibility validation at the data interface boundary.
- Do not connect real APIs or broker clients.

Acceptance criteria:
- Core boundary documentation exists.
- Example config loads without secrets.
- Secret-like config keys are rejected.
- Future-dated provider snapshots are rejected.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

## Task ID: QTS-015

Status: Completed
Phase: Real data research
Title: Add Stooq EOD local-cache research workflow

Scope:
- Add one real historical data source path behind the existing `DataSource`
  boundary.
- Cache raw Stooq CSV outside tracked source data.
- Normalize Stooq daily CSV into the existing historical CSV shape.
- Keep runtime snapshots local-only and validated by `ValidatedDataSource`.
- Add a commit-safe Stooq ETF momentum configuration.
- Compare momentum with equal weight across train, validation, and test splits.
- Do not add broker APIs, live data streams, React UI work, or secrets.

Acceptance criteria:
- Stooq normalized CSV can return visible snapshots.
- Runtime snapshots do not download data.
- Non-CSV Stooq responses are rejected.
- Non-positive closes fail explicitly.
- Stooq typed config loads without secrets.
- Research reports include config hash, data file hash, data version, sample
  splits, and costs.
- `pytest` passes.
- `ruff check` passes.
- `mypy` passes.

Completion note:
- Scripted Stooq downloads may return browser verification HTML in this
  environment. The downloader rejects those responses; full research should run
  once valid raw Stooq CSV files are cached or manually downloaded.

## Task ID: QTS-016

Status: Pending
Phase: Audit hardening
Title: Fix review findings in Python boundary and shared utilities

Scope:
- Use shared portfolio math in paper trading.
- Share drawdown and ISO conversion helpers instead of duplicating them.
- Make the in-memory API run store thread-safe.
- Prevent accidental double charging when both legacy `cost_rate` and a
  `CostModel` are provided.
- Stop hardcoding readiness test status as passed in structured reports.

Acceptance criteria:
- Targeted regression tests fail before implementation and pass after.
- `pytest`, `ruff check`, and `mypy` pass.
- Relevant docs mention the changed behavior.

## Task ID: QTS-017

Status: Pending
Phase: Rust-led core reconstruction
Title: Establish Rust contracts, math, and API service foundation

Scope:
- Add a Rust workspace under `rust/` with typed report contracts, deterministic
  math helpers, and a minimal service boundary.
- Implement `/health`, `/workflows`, and synthetic-demo `/runs` behavior in the
  Rust service using the same JSON contract as Python.
- Keep Python as the reference implementation until parity tests prove migrated
  behavior.

Acceptance criteria:
- Rust unit tests cover position value, target order deltas, total return, and
  max drawdown.
- Python tests verify the Rust contract source and document local `cargo`
  availability.
- No broker, live market data, or secrets are introduced.
