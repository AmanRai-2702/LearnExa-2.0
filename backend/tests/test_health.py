import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """A fake browser that talks to our app directly, with no real server.

    A fixture is a helper that pytest builds and hands to any test that lists
    its name as a parameter.
    """
    return TestClient(app)


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_has_the_expected_fields(client):
    body = client.get("/health").json()

    # The frontend's HealthResponse type (lib/types.ts) relies on exactly these fields.
    assert set(body) == {"status", "app", "environment", "gemini_configured"}
    assert isinstance(body["gemini_configured"], bool)


def test_health_reports_a_configured_key_without_leaking_it(client, monkeypatch):
    secret = "super-secret-test-key"
    # monkeypatch changes a value for this one test and restores it afterwards,
    # so your real .env is never touched.
    monkeypatch.setattr(get_settings(), "gemini_api_key", secret)

    response = client.get("/health")

    assert response.json()["gemini_configured"] is True
    # The key must never appear anywhere in the response.
    assert secret not in response.text


def test_health_reports_a_missing_key(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "gemini_api_key", "")

    assert client.get("/health").json()["gemini_configured"] is False


def test_cors_allows_the_frontend_origin(client):
    origin = get_settings().frontend_origin

    response = client.get("/health", headers={"Origin": origin})

    assert response.headers["access-control-allow-origin"] == origin


def test_cors_does_not_allow_other_origins(client):
    response = client.get("/health", headers={"Origin": "http://evil.example"})

    assert "access-control-allow-origin" not in response.headers