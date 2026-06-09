# Project

## Goal

Build a modular, document-driven quantitative trading research system that can
grow in small, audited steps. The first priority is trustworthiness: no
look-ahead bias, explicit risk controls, reproducible results, and a project
state that a new code agent can understand from repository documents.

## Current Stage

Phase 9 is complete once paper trading can run across multiple days, write local
simulated orders and daily reports, log failures explicitly, and keep broker
submission disabled. The next task is Phase 10: add an ML research signal layer
that still obeys the `SignalModel` boundary.

## Explicit Non-Goals

- No real market data.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven signal generation.
- No production strategy implementation.
- No broker data source implementation.
- No secrets, API keys, account identifiers, or passwords in code or docs.

## Strategy Disclaimer

The momentum strategy is a research fixture for exercising the pipeline. It is
not trading advice and must not be used for live orders.

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
