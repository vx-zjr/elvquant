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
- Risk checks were run when targets, orders, or execution paths changed.
- Reports include risk rejection counts and reasons when rejections occur.
- Paper trading writes local files only and keeps broker submission disabled.

## Phase 0 Review

- No real trading logic exists.
- Required root documents exist.
- Quality gates are configured locally and in CircleCI.

## Phase 3 Review

- Honesty probes cover future-data absence, cost drag, accounting identity,
  non-negative costs, no-trade position stability, risk rejection, and run
  metadata.

## Phase 7 Review

- Risk rules cover short targets, single-asset exposure, total exposure, daily
  turnover, daily loss stops, and missing or abnormal prices.

## Phase 9 Review

- Paper trading logs orders locally with `broker_submission: disabled`.
- Paper daily reports are generated.
- Paper failures are logged explicitly.

## Phase 11 Remediation Review

- Kill switch, order amount limits, alert logging, traceability, recovery,
  human confirmation records, and paper observation controls exist without
  broker integration.

## Phase 12 Review

- Manual order workflow defaults to dry-run and rejects real broker submission.
- Risk rejection prevents manual submit.
- Kill switch prevents manual submit.
- Human confirmation is required before local order recording.
- Manual order records include source strategy, signal, target weights, risk
  result, confirmer, confirmation time, and `broker_submission: disabled`.
