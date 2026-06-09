# Data Policy

## Current Data State

No data source exists in Phase 0.

## Rules

- No real market data may be used before the task that explicitly allows it.
- Synthetic data may be introduced only by the Phase 2 task.
- Every future data source must define time zone, adjustment, missing-value, and
  data-visibility semantics before implementation.
- Data visible at a decision time must not include future prices, future
  corporate actions, or future corrections.
- Secrets and account data must never be stored in repository files.
