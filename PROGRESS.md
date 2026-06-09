# Progress

## 2026-06-09

- Core and Streamlit UI were split into separate repositories.
- Streamlit remains a replaceable thin client; business logic stays in core.
- Local paper trading and manual dry-run workflows exist, with broker
  submission disabled.
- Stooq EOD was selected as the first real-data test source.
- Added the next implementation target: cache Stooq daily CSV, normalize it to
  the existing historical CSV shape, and run equal-weight versus momentum
  research on local normalized data.
- Stooq scripted downloads in this environment now require either a provider
  `apikey` or manual browser download. Core supports optional `STOOQ_API_KEY`
  without committing secret values.

## Current Focus

Move the project from synthetic/FRED smoke tests to a reproducible real-data
research workflow while keeping secrets out of committed configuration and
keeping provider validation at the `DataSource` boundary.

## Still Deferred

- Broker integration.
- Real order submission.
- Intraday or streaming market data.
- React frontend rewrite.
- Additional real providers beyond the first concrete need.
