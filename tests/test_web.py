import pytest

pytest.importorskip("fastapi")
pytest.importorskip("prometheus_client")
pytest.importorskip("pydantic")

from architect.web import app
from architect.metrics import agent_invocations
from fastapi.testclient import TestClient

def test_metrics_endpoint():
    client = TestClient(app)
    agent_invocations.inc()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "agent_invocations_total" in resp.text
