from __future__ import annotations

from fastapi.testclient import TestClient


def test_api_lists_public_workflows() -> None:
    from qts.api_app import create_app

    client = TestClient(create_app(service_token="test-token"))
    response = client.get(
        "/workflows",
        headers={"X-Service-Token": "test-token", "X-Owner-User-Id": "user-a"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["workflows"][0].keys() == {"id", "label", "description", "requiresData"}


def test_api_creates_and_reads_run_for_owner_only() -> None:
    from qts.api_app import create_app

    client = TestClient(create_app(service_token="test-token"))
    headers = {"X-Service-Token": "test-token", "X-Owner-User-Id": "user-a"}

    created = client.post("/runs", json={"workflowId": "synthetic_demo"}, headers=headers)

    assert created.status_code == 200
    run_id = created.json()["runId"]
    assert created.json()["status"] == "completed"

    own_read = client.get(f"/runs/{run_id}", headers=headers)
    other_read = client.get(
        f"/runs/{run_id}",
        headers={"X-Service-Token": "test-token", "X-Owner-User-Id": "user-b"},
    )

    assert own_read.status_code == 200
    assert own_read.json()["run_id"] == run_id
    assert other_read.status_code == 404


def test_api_rejects_missing_service_token() -> None:
    from qts.api_app import create_app

    client = TestClient(create_app(service_token="test-token"))

    response = client.get("/runs", headers={"X-Owner-User-Id": "user-a"})

    assert response.status_code == 401
