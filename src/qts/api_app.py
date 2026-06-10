"""Independent FastAPI boundary for remote UI clients."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from qts import __version__
from qts.reports import public_structured_workflows, run_structured_workflow


class RunCreateRequest(BaseModel):
    workflowId: str
    configId: str | None = None


@dataclass(frozen=True)
class ApiContext:
    owner_user_id: str


class InMemoryRunStore:
    """Small owner-isolated store for the first deployable API slice."""

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, object]] = {}
        self._lock = RLock()

    def put(self, owner_user_id: str, payload: dict[str, object]) -> None:
        with self._lock:
            self._runs[str(payload["run_id"])] = {
                "owner_user_id": owner_user_id,
                "payload": payload,
            }

    def list_for_owner(self, owner_user_id: str) -> list[dict[str, object]]:
        with self._lock:
            return [
                self._summary(record["payload"])
                for record in tuple(self._runs.values())
                if record["owner_user_id"] == owner_user_id
            ]

    def get_for_owner(self, owner_user_id: str, run_id: str) -> dict[str, object] | None:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None or record["owner_user_id"] != owner_user_id:
                return None
            payload = record["payload"]
            if not isinstance(payload, dict):
                raise TypeError("run payload must be a dictionary")
            return dict(payload)

    def artifacts_for_owner(
        self,
        owner_user_id: str,
        run_id: str,
    ) -> list[dict[str, object]] | None:
        payload = self.get_for_owner(owner_user_id, run_id)
        if payload is None:
            return None
        artifacts = payload.get("artifacts", [])
        if not isinstance(artifacts, list):
            raise TypeError("artifacts must be a list")
        return artifacts

    def _summary(self, payload: object) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise TypeError("run payload must be a dictionary")
        return {
            "runId": payload["run_id"],
            "workflow": payload["workflow"],
            "status": payload["status"],
            "metrics": payload.get("metrics", {}),
        }


def create_app(
    service_token: str | None = None,
    core_root: Path | None = None,
    store: InMemoryRunStore | None = None,
) -> FastAPI:
    """Create the API app with explicit service-token and owner isolation."""

    expected_token = service_token or os.environ.get("ELVQUANT_API_SERVICE_TOKEN", "dev-token")
    run_store = store or InMemoryRunStore()
    app = FastAPI(title="elvquant API", version=__version__)

    def context(
        x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
        x_owner_user_id: str | None = Header(default=None, alias="X-Owner-User-Id"),
    ) -> ApiContext:
        if x_service_token != expected_token:
            raise HTTPException(status_code=401, detail="invalid service token")
        if not x_owner_user_id:
            raise HTTPException(status_code=401, detail="missing owner user id")
        return ApiContext(owner_user_id=x_owner_user_id)

    context_dependency = Depends(context)

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"ok": True, "version": __version__}

    @app.get("/workflows")
    def workflows(_context: ApiContext = context_dependency) -> dict[str, object]:
        return {
            "workflows": [
                {
                    "id": workflow.workflow_id,
                    "label": workflow.label,
                    "description": workflow.description,
                    "requiresData": workflow.requires_data,
                }
                for workflow in public_structured_workflows()
            ]
        }

    @app.post("/runs")
    def create_run(
        request: RunCreateRequest,
        context: ApiContext = context_dependency,
    ) -> dict[str, object]:
        report = run_structured_workflow(request.workflowId, core_root=core_root)
        payload = report.to_payload()
        run_store.put(context.owner_user_id, payload)
        return {"runId": report.run_id, "status": report.status}

    @app.get("/runs")
    def list_runs(context: ApiContext = context_dependency) -> dict[str, object]:
        return {"runs": run_store.list_for_owner(context.owner_user_id)}

    @app.get("/runs/{run_id}")
    def get_run(run_id: str, context: ApiContext = context_dependency) -> dict[str, object]:
        payload = run_store.get_for_owner(context.owner_user_id, run_id)
        if payload is None:
            raise HTTPException(status_code=404, detail="run not found")
        return payload

    @app.get("/runs/{run_id}/artifacts")
    def get_artifacts(
        run_id: str,
        context: ApiContext = context_dependency,
    ) -> dict[str, object]:
        artifacts = run_store.artifacts_for_owner(context.owner_user_id, run_id)
        if artifacts is None:
            raise HTTPException(status_code=404, detail="run not found")
        return {"artifacts": artifacts}

    return app


app = create_app()


__all__ = ["InMemoryRunStore", "app", "create_app"]
