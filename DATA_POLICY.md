# Data Policy

## Current Data State

Phase 2 includes `SyntheticDataSource`, a deterministic fake price source used
only for testing the pipeline shape.

## Rules

- No real market data may be used before the task that explicitly allows it.
- Synthetic data is allowed for Phase 2 and Phase 3 honesty probes.
- Every future data source must define time zone, adjustment, missing-value, and
  data-visibility semantics before implementation.
- Data visible at a decision time must not include future prices, future
  corporate actions, or future corrections.
- Secrets and account data must never be stored in repository files.

## Synthetic Data Rules

- Source name: `SyntheticDataSource`.
- Data version: `synthetic-v1`.
- Time zone: timezone-aware UTC datetimes.
- Adjustment rule: no corporate actions, no adjustments.
- Missing values: exact decision-time lookup only; missing timestamps raise an
  explicit error.
- Visibility: a snapshot exposes only prices for the requested decision time.
