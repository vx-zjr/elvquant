"""Local-only paper trading mode."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from qts.contracts import (
    AccountingLedger,
    DataSnapshot,
    DataSource,
    ExecutionSimulator,
    LedgerState,
    Order,
    PortfolioConstructor,
    Report,
    RiskDecision,
    RiskManager,
    SignalModel,
    TargetPortfolio,
)
from qts.portfolio_math import orders_for_target, position_value
from qts.simple import (
    BasicRiskManager,
    EqualWeightSignal,
    SimpleAccountingLedger,
    SimpleExecutionSimulator,
    SimplePortfolioConstructor,
    SyntheticDataSource,
)

_EPSILON = 1e-9


@dataclass(frozen=True)
class PaperTradingConfig:
    """Configuration for local-only paper trading."""

    output_dir: Path
    initial_cash: float
    broker_submission: str = "disabled"

    def __post_init__(self) -> None:
        if self.initial_cash <= 0.0:
            raise ValueError("initial_cash must be positive")
        if self.broker_submission != "disabled":
            raise ValueError("paper trading broker submission must remain disabled")


@dataclass(frozen=True)
class PaperTradingDayResult:
    """Result of one paper trading day."""

    decision_time: datetime
    target: TargetPortfolio
    orders: tuple[Order, ...]
    risk_decision: RiskDecision
    daily_report_path: Path
    order_log_path: Path
    state: LedgerState


@dataclass
class PaperTradingEngine:
    """Run local-only paper trading days without broker connectivity."""

    data_source: DataSource
    signal_model: SignalModel
    portfolio_constructor: PortfolioConstructor
    risk_manager: RiskManager
    execution_simulator: ExecutionSimulator
    ledger: AccountingLedger
    config: PaperTradingConfig
    state: LedgerState = field(init=False)

    def __post_init__(self) -> None:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "daily_reports").mkdir(parents=True, exist_ok=True)
        self.state = LedgerState(
            as_of=datetime.min,
            cash=self.config.initial_cash,
            positions={},
            equity=self.config.initial_cash,
            cumulative_cost=0.0,
        )

    def run_days(self, decision_times: Sequence[datetime]) -> tuple[PaperTradingDayResult, ...]:
        return tuple(self.run_day(decision_time) for decision_time in decision_times)

    def run_day(self, decision_time: datetime) -> PaperTradingDayResult:
        try:
            return self._run_day(decision_time)
        except Exception as exc:
            self._append_failure(decision_time, exc)
            raise

    def _run_day(self, decision_time: datetime) -> PaperTradingDayResult:
        snapshot = self.data_source.snapshot(decision_time)
        current_equity = self.state.cash + position_value(self.state.positions, snapshot.prices)
        signals = self.signal_model.generate(snapshot)
        target = self.portfolio_constructor.construct(snapshot, signals)
        orders = orders_for_target(
            state=self.state,
            equity=current_equity,
            asset_ids=snapshot.asset_ids,
            prices=snapshot.prices,
            target=target,
        )
        risk_decision = self.risk_manager.evaluate(
            snapshot,
            target,
            orders,
            portfolio_state=self.state,
        )
        order_log_path = self.config.output_dir / "orders.jsonl"
        self._append_orders(order_log_path, snapshot, orders, risk_decision)

        if risk_decision.allowed:
            fills = self.execution_simulator.simulate(snapshot, orders)
            self.state = self.ledger.apply_fills(self.state, fills, snapshot)
        else:
            self.state = LedgerState(
                as_of=snapshot.as_of,
                cash=self.state.cash,
                positions=self.state.positions,
                equity=current_equity,
                cumulative_cost=self.state.cumulative_cost,
            )

        daily_report_path = self._write_daily_report(snapshot, target, orders, risk_decision)
        return PaperTradingDayResult(
            decision_time=snapshot.as_of,
            target=target,
            orders=orders,
            risk_decision=risk_decision,
            daily_report_path=daily_report_path,
            order_log_path=order_log_path,
            state=self.state,
        )

    def _append_orders(
        self,
        path: Path,
        snapshot: DataSnapshot,
        orders: Sequence[Order],
        risk_decision: RiskDecision,
    ) -> None:
        with path.open("a", encoding="utf-8") as handle:
            for order in orders:
                payload = {
                    "decision_time": snapshot.as_of.isoformat(),
                    "asset_id": order.asset_id,
                    "quantity": order.quantity,
                    "reason": order.reason,
                    "risk_allowed": risk_decision.allowed,
                    "risk_reasons": list(risk_decision.reasons),
                    "broker_submission": self.config.broker_submission,
                }
                handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _append_failure(self, decision_time: datetime, exc: Exception) -> None:
        path = self.config.output_dir / "failures.jsonl"
        payload = {
            "decision_time": decision_time.isoformat(),
            "status": "failed",
            "error": str(exc),
            "broker_submission": self.config.broker_submission,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _write_daily_report(
        self,
        snapshot: DataSnapshot,
        target: TargetPortfolio,
        orders: Sequence[Order],
        risk_decision: RiskDecision,
    ) -> Path:
        path = self.config.output_dir / "daily_reports" / f"{snapshot.as_of:%Y-%m-%d}.md"
        status = "risk_allowed" if risk_decision.allowed else "risk_rejected"
        lines = [
            f"# Paper Trading {snapshot.as_of:%Y-%m-%d}",
            "",
            f"- broker: {self.config.broker_submission}",
            f"- status: {status}",
            f"- equity: {self.state.equity:.6f}",
            f"- orders: {len(orders)}",
            f"- risk_reasons: {', '.join(risk_decision.reasons) or 'none'}",
            "",
            "## Target Weights",
        ]
        lines.extend(f"- {asset_id}: {weight:.6f}" for asset_id, weight in target.weights.items())
        lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


def run_synthetic_paper_demo(output_dir: Path | None = None) -> Report:
    """Run a deterministic local paper-trading demo without broker connectivity."""

    from datetime import UTC, timedelta

    start = datetime(2026, 1, 1, tzinfo=UTC)
    run_output_dir = output_dir or Path("paper_runs/synthetic-paper-demo")
    engine = PaperTradingEngine(
        data_source=SyntheticDataSource(asset_ids=("AAA", "BBB"), start=start, periods=6),
        signal_model=EqualWeightSignal(),
        portfolio_constructor=SimplePortfolioConstructor(),
        risk_manager=BasicRiskManager(),
        execution_simulator=SimpleExecutionSimulator(cost_rate=0.001),
        ledger=SimpleAccountingLedger(),
        config=PaperTradingConfig(output_dir=run_output_dir, initial_cash=10_000.0),
    )
    results = engine.run_days(tuple(start + timedelta(days=offset) for offset in range(5)))
    return _build_paper_report(results, run_output_dir)


def _build_paper_report(
    results: Sequence[PaperTradingDayResult],
    output_dir: Path,
) -> Report:
    first = results[0]
    last = results[-1]
    initial_equity = 10_000.0
    ending_equity = last.state.equity
    total_orders = sum(len(result.orders) for result in results)
    risk_rejections = sum(0 if result.risk_decision.allowed else 1 for result in results)
    run_id = f"paper-synthetic-{first.decision_time:%Y%m%d}-{last.decision_time:%Y%m%d}"
    order_log_path = output_dir / "orders.jsonl"
    lines = [
        f"run_id: {run_id}",
        "mode: local_paper",
        "broker_submission: disabled",
        f"output_dir: {output_dir.resolve()}",
        f"order_log: {order_log_path.resolve()}",
        f"latest_daily_report: {last.daily_report_path.resolve()}",
        f"ending_equity: {ending_equity:.6f}",
        f"total_return: {ending_equity / initial_equity - 1.0:.6f}",
        f"total_orders: {total_orders}",
        f"risk_rejections: {risk_rejections}",
        "",
        "## Daily Results",
        "",
        "| date | equity | orders | risk_allowed | daily_report |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    lines.extend(
        "| "
        f"{result.decision_time:%Y-%m-%d} | "
        f"{result.state.equity:.6f} | "
        f"{len(result.orders)} | "
        f"{str(result.risk_decision.allowed).lower()} | "
        f"{result.daily_report_path.resolve()} |"
        for result in results
    )
    return Report(
        run_id=run_id,
        text="\n".join(lines),
        metrics={
            "ending_equity": ending_equity,
            "total_return": ending_equity / initial_equity - 1.0,
            "total_orders": float(total_orders),
            "risk_rejections": float(risk_rejections),
        },
    )


__all__ = [
    "PaperTradingConfig",
    "PaperTradingDayResult",
    "PaperTradingEngine",
    "run_synthetic_paper_demo",
]
