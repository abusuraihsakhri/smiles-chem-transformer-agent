"""Security and end-to-end regression tests for the public interfaces."""
import json

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail
from cli import main as enterprise_cli
from smiles_transformer.cli import main as classic_cli


@pytest.fixture()
def client():
    return TestClient(app)


def test_molecular_api_and_invalid_input(client):
    response = client.post("/api/molecule", json={"smiles": "OCC"})
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_smiles"] == "CCO"
    assert data["molecular_formula"] == "C2H6O"

    for payload in ({"smiles": "not a smiles"}, {"smiles": ""}, {"smiles": "C", "max_tautomers": 0}):
        assert client.post("/api/molecule", json=payload).status_code == 422


def test_existing_audit_api_and_dashboard(client):
    assert client.get("/health").status_code == 200
    assert "SMILES Molecular Workbench" in client.get("/").text
    response = client.post("/api/audit", json={
        "task_id": "REGRESSION-1",
        "target_identifier": "TEST-1",
        "primary_metric": 10,
        "secondary_metric": 1,
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    assert client.get("/api/audit/logs").json()["verified"] is True


def test_sensitive_identifier_and_bad_metric_rejection(client):
    response = client.post("/api/audit", json={
        "task_id": "MRN-123456",
        "target_identifier": "TEST-1",
        "primary_metric": 10,
    })
    assert response.status_code == 422
    assert "pattern" not in response.text
    for value in ("NaN", "Infinity"):
        response = client.post("/api/audit", json={
            "task_id": "TEST",
            "target_identifier": "TARGET",
            "primary_metric": value,
        })
        assert response.status_code == 422


def test_audit_signatures_detect_tampering():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("actor", "tier", "EVENT", {"result": "ok"})
    trail.log("actor", "tier", "EVENT", {"result": "also-ok"})
    assert trail.verify_integrity()
    cloned = trail.get_trail()
    cloned[0]["actor"] = "changed"
    assert trail.verify_integrity(), "Public API must not return mutable audit state"
    trail.logs[0]["payload_hash"] = "0" * 64
    assert not trail.verify_integrity(), "HMAC must detect record modification"


def test_production_requires_audit_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        AuditTrail()
    with pytest.raises(RuntimeError):
        AuditTrail(secret_key="change-me-in-production")


def test_chemistry_commands(capsys):
    assert enterprise_cli(["molecule", "OCC"]) == 0
    assert json.loads(capsys.readouterr().out)["canonical_smiles"] == "CCO"
    assert classic_cli(["molecule", "C(C)(C)(C)(C)C"]) == 2
