import pytest
from fastapi.testclient import TestClient

from app.hardening import MAX_BODY_BYTES, check_configuration, key_problems
from app.main import app


def test_every_response_has_security_headers():
    response = TestClient(app).get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in response.headers["content-security-policy"]


def test_huge_bodies_are_rejected_before_reading_them():
    response = TestClient(app).post("/generate", content="x" * (MAX_BODY_BYTES + 1),
                                    headers={"Content-Type": "application/json"})
    assert response.status_code == 413
    assert response.headers["x-frame-options"] == "DENY"


def test_weak_keys_are_reported():
    assert key_problems("") == ["AI_SERVICE_KEY is not set"]
    assert any("32" in p for p in key_problems("short"))
    assert any("example" in p for p in key_problems("change-me-to-a-long-random-string-of-32-plus-chars"))
    assert key_problems("Zq8-vR3p_Lk2mN7xT5wY1bC9dF4gH6jK0aS") == []


def test_production_refuses_a_weak_key_but_development_only_warns(monkeypatch):
    monkeypatch.setenv("AI_SERVICE_KEY", "short")
    monkeypatch.setenv("ENVIRONMENT", "development")
    assert check_configuration()
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(RuntimeError):
        check_configuration()
