# Data Policy

## Current Data State

Phase 2 includes `SyntheticDataSource`, a deterministic fake price source used
only for testing the pipeline shape. Phase 4 introduces a read-only CSV
historical data source backed by a small fixed FRED sample.

## Rules

- No real market data may be used before the task that explicitly allows it.
- Synthetic data is allowed for Phase 2 and Phase 3 honesty probes.
- Every future data source must define time zone, adjustment, missing-value, and
  data-visibility semantics before implementation.
- Data visible at a decision time must not include future prices, future
  corporate actions, or future corrections.
- Secrets and account data must never be stored in repository files.
- Provider adapters must validate point-in-time visibility at the data interface
  boundary before strategy code can consume snapshots.
- Commit-safe configuration may name providers, assets, parameters, dates, and
  seeds; secret values must remain outside committed configuration.

## Synthetic Data Rules

- Source name: `SyntheticDataSource`.
- Data version: `synthetic-v1`.
- Time zone: timezone-aware UTC datetimes.
- Adjustment rule: no corporate actions, no adjustments.
- Missing values: exact decision-time lookup only; missing timestamps raise an
  explicit error.
- Visibility: a snapshot exposes only prices for the requested decision time.

## Historical CSV Rules

- Source name: `CsvHistoricalDataSource`.
- Sample source: Federal Reserve Economic Data (FRED), public CSV export.
- Series:
  - `SP500`: S&P 500 index level.
  - `NASDAQCOM`: NASDAQ Composite index level.
- Source pages:
  - `https://fred.stlouisfed.org/series/SP500`
  - `https://fred.stlouisfed.org/series/NASDAQCOM`
- Source CSV URLs:
  - `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2024-01-02&coed=2024-01-10`
  - `https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM&cosd=2024-01-02&coed=2024-01-10`
- Repository sample file: `data/historical/fred_index_sample.csv`.
- Data version: `fred-index-sample-20240102-20240110-v1`.
- Fields: `date`, `asset_id`, `close`, `source`, `source_url`, `data_version`.
- Time zone: dates are interpreted as UTC midnight decision timestamps.
- Adjustment rule: no price adjustment is applied. FRED values are index levels,
  not broker-tradable adjusted security prices.
- Missing values: blank values or FRED `.` values are invalid and must raise an
  explicit error. Missing timestamps or missing asset values must also raise.
- Visibility: a snapshot returns only rows for the requested date. The data
  source may load the file into memory, but callers only receive the requested
  decision-time prices.

## Stooq EOD Rules

- Source name: `StooqHistoricalDataSource`.
- Intended universe: `SPY.US`, `QQQ.US`, `IWM.US`, `TLT.US`, `GLD.US`.
- Stooq v1 requires no project secret or API token.
- Stooq downloads are a data-preparation step. Runtime `snapshot()` calls read
  only normalized local CSV and must not access the network.
- Raw Stooq daily CSV fields used by the normalizer: `Date` and `Close`.
- Normalized fields: `date`, `asset_id`, `close`, `source`, `source_url`,
  `data_version`.
- Time zone: normalized dates are interpreted as UTC midnight decision
  timestamps.
- Adjustment rule: v1 records the Stooq `Close` field as delivered. The report
  must state this limitation before using results as investment evidence.
- Missing values, non-CSV responses, non-positive closes, missing dates, missing
  assets, and empty `data_version` values are invalid and must fail explicitly.
- Visibility: Stooq data is consumed through `StooqHistoricalDataSource`, which
  wraps the normalized CSV source with `ValidatedDataSource`.
- Network caveat: Stooq may return a browser verification page to scripted
  requests. Such responses must not be cached as data; the downloader must fail
  with a clear error so the operator can retry or provide a manually downloaded
  CSV.

## Derived Feature Rules

- `TrailingReturnFeatureDataSource` may derive trailing-return features from
  earlier observations in a declared calendar.
- Feature names must encode the lookback, such as `momentum_1`.
- If the requested decision time has insufficient prior observations, the feature
  is absent rather than filled with future data.
- Strategies may consume only the feature values present in the supplied
  `DataSnapshot`.

## Provider Interface Enforcement

Use `ValidatedDataSource` or an equivalent boundary check for every real
provider. A provider snapshot must:

- be timezone-aware
- not be after the requested decision time
- include a non-empty `data_version`
- include finite positive prices for all declared assets
- avoid exposing features for assets outside the snapshot asset universe

This rule keeps look-ahead risk closed when replacing synthetic or CSV data with
real provider data.

## Configuration And Secret Separation

Committed configuration belongs under `configs/` and must be safe to include in
run reports. It may include provider names, asset IDs, strategy parameters, risk
parameters, dates, and seeds. Secret values belong in environment variables,
gitignored `.env` files, or a secret manager, and must not be copied into
reports.

The Stooq example config is commit-safe and uses no secrets. Future providers
that require tokens must document only environment variable names in
`.env.example`; real values must remain outside git.

## Execution and Cost Assumptions

- Phase 6 execution still simulates fills at the provided execution snapshot
  price; no broker quotes or live order books are used.
- Fixed commission is charged per non-zero order.
- Proportional commission is charged on absolute traded notional.
- Slippage is represented as an additional cost on absolute traded notional, not
  as a modified market price.
- All cost estimates must be non-negative and must be recorded in `Fill.cost`.
