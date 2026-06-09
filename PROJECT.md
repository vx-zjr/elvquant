# Project

## Goal

Build a modular, document-driven quantitative trading research system that can
grow in small, audited steps. The first priority is trustworthiness: no
look-ahead bias, explicit risk controls, reproducible results, and a project
state that a new code agent can understand from repository documents.

## Current Stage

Phase 0 is complete once the scaffold, quality gates, and required documents are
present. The next task is Phase 1: define core interfaces only.

## Explicit Non-Goals

- No real market data.
- No live broker connection.
- No live trading or real-money order submission.
- No ML or AI-driven signal generation.
- No strategy implementation.
- No backtest engine implementation.
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
