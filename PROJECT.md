# Project

## Goal

Build a modular, document-driven quantitative trading research system that can
grow in small, audited steps. The first priority is trustworthiness: no
look-ahead bias, explicit risk controls, reproducible results, and a project
state that a new code agent can understand from repository documents.

## Current Stage

The document-defined business plan is complete through Phase 12. The system can
generate traceable manual order recommendations, enforce risk and kill-switch
controls, require human confirmation, and record dry-run order submissions
locally. Broker integration and real-money order submission remain disabled.

## Explicit Non-Goals

- No live market data feed.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven live trading.
- No production strategy implementation.
- No broker data source implementation.
- No secrets, API keys, account identifiers, or passwords in code or docs.

## Strategy Disclaimer

The momentum strategy is a research fixture for exercising the pipeline. It is
not trading advice and must not be used for live orders.

The ML-style signal is also research-only. It cannot place orders, alter risk
checks, alter the backtest engine, or connect to live trading.

## Required Start Protocol

Every agent must read these files before editing:

- `PROJECT.md`
- `ARCHITECTURE.md`
- `CONTRACTS.md`
- `DATA_POLICY.md`
- `RISK_POLICY.md`
- `TASKS.md`
- `REVIEW.md`

Then execute only the first `Pending` task in `TASKS.md`.
