# Project

## Goal

Build a modular, document-driven quantitative trading research system that can
grow in small, audited steps. The first priority is trustworthiness: no
look-ahead bias, explicit risk controls, reproducible results, and a project
state that a new code agent can understand from repository documents.

## Current Stage

Phase 3 is complete once honesty probe tests guard against self-deception,
look-ahead access, accounting imbalance, negative costs, position drift, missing
run metadata, and basic risk bypasses. The next task is Phase 4: add a read-only
historical data source without changing strategy, backtest, risk, or accounting
behavior.

## Explicit Non-Goals

- No real market data.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven signal generation.
- No production strategy implementation.
- No real data source implementation.
- No secrets, API keys, account identifiers, or passwords in code or docs.

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
