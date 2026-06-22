"""End-to-end tests using FastAPI's TestClient.

These hit the real endpoints in-process (no server needed) and prove the contract
holds: auth is enforced, a backup runs through every stage to "completed", unknown
ids 404, and config round-trips. Run with:  pytest -q
"""

import time

from fastapi.testclient import TestClient

from backup_api.config import get_settings
from backup_api.main import app

client = TestClient(app)
KEY = get_settings().api_key
AUTH = {"X-API-Key": KEY}


def test_health_is_open():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_auth_required():
    # No key -> 401
    assert client.get("/v1/backups").status_code == 401
    # Bad key -> 401
    assert client.get("/v1/backups", headers={"X-API-Key": "wrong"}).status_code == 401


def test_bad_request_is_rejected():
    # Missing required "source_drive" -> 422 from Pydantic validation
    r = client.post("/v1/backups", json={"label": "oops"}, headers=AUTH)
    assert r.status_code == 422


def test_backup_runs_to_completion():
    r = client.post("/v1/backups", json={"source_drive": "C:"}, headers=AUTH)
    assert r.status_code == 202
    job = r.json()
    assert job["status"] == "queued"
    job_id = job["id"]

    # Background task finishes quickly with the stubs; poll until terminal.
    for _ in range(50):
        got = client.get(f"/v1/backups/{job_id}", headers=AUTH).json()
        if got["status"] in {"completed", "failed"}:
            break
        time.sleep(0.05)

    assert got["status"] == "completed"
    assert got["progress"] == 1.0
    assert got["s3_key"]


def test_unknown_job_is_404():
    assert client.get("/v1/backups/doesnotexist", headers=AUTH).status_code == 404


def test_config_round_trip():
    client.put("/v1/config", json={"retention_count": 7}, headers=AUTH)
    cfg = client.get("/v1/config", headers=AUTH).json()
    assert cfg["retention_count"] == 7
