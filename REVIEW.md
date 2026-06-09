# Review Checklist

Before completing any task, verify:

- The task changed only one task scope.
- Tests were added or updated.
- `pytest` was run.
- `ruff check` was run.
- `mypy` was run.
- Relevant documents were updated.
- No future-data risk was introduced.
- Interface changes were recorded in `DECISIONS.md`.
- Risk behavior was not bypassed.
- Accounting behavior was not weakened.
- The project can be run from `RUNBOOK.md`.
- Experiment results were recorded when a backtest or paper run occurred.
- Honesty probes were run and passed before any real data, strategy, or live
  trading expansion.

## Phase 0 Review

- No real trading logic exists.
- Required root documents exist.
- Quality gates are configured locally and in CircleCI.

## Phase 3 Review

- Honesty probes cover future-data absence, cost drag, accounting identity,
  non-negative costs, no-trade position stability, risk rejection, and run
  metadata.
