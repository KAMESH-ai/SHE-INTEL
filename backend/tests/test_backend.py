import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
import requests

os.environ.setdefault("DATABASE_URL", f"sqlite:///{Path(tempfile.gettempdir()) / 'she_intel_test.db'}")
os.environ.setdefault("XGB_MODEL_ARTIFACT_PATH", str(Path(tempfile.gettempdir()) / 'she_intel_xgb_model.joblib'))

from backend.app.main import app  # noqa: E402
from backend.app.ml.xgb_model import ARTIFACT_PATH, get_model_metadata  # noqa: E402
from backend.app.services import india_context as india_context_service  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_aqi_cache():
    india_context_service._AQI_CACHE.clear()
    yield
    india_context_service._AQI_CACHE.clear()


def create_user(email: str | None = None):
    if email is None:
        email = f"tester_{uuid4().hex[:8]}@example.com"
    else:
        local_part, _, domain = email.partition("@")
        domain = domain or "example.com"
        email = f"{local_part}_{uuid4().hex[:8]}@{domain}"
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "name": "Tester",
            "age": 28,
            "state": "Tamil Nadu",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_history(headers):
    client.post(
        "/periods/",
        headers=headers,
        json={
            "start_date": "2026-03-01T00:00:00",
            "end_date": "2026-03-05T00:00:00",
            "flow_level": "high",
            "symptoms": "heavy bleeding cramps",
        },
    )
    client.post(
        "/periods/",
        headers=headers,
        json={
            "start_date": "2026-02-01T00:00:00",
            "end_date": "2026-02-05T00:00:00",
            "flow_level": "medium",
            "symptoms": "dizziness fatigue",
        },
    )
    client.post(
        "/symptoms/",
        headers=headers,
        json={
            "description": "Feeling dizzy, pale, tired with heavy bleeding and cravings",
            "fatigue_level": 9,
            "sleep_quality": 4,
            "mood": "tired",
        },
    )


def test_analysis_response_includes_model_metrics_and_india_context():
    headers = create_user("analysis@example.com")
    seed_history(headers)

    response = client.post(
        "/analysis/analyze",
        headers=headers,
        json={
            "description": "Feeling dizzy, pale, tired with heavy bleeding and cravings",
            "fatigue_level": 9,
            "sleep_quality": 4,
            "mood": "tired",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["medical_disclaimer"] == "This is not a diagnosis. Please consult a doctor for confirmation."
    assert payload["model_metrics"]["accuracy"] >= 0.85
    assert payload["model_metrics"]["macro_f1"] >= 0.85
    assert isinstance(payload["aqi_enrichment"], dict)
    assert payload["aqi_enrichment"]["aqi_category"] in {"good", "satisfactory", "moderate", "poor", "very poor", "severe"}
    assert len(payload["diet_recommendations"]) >= 1
    assert len(payload["government_schemes"]) >= 1
    assert len(payload["lab_test_cost_estimates"]) >= 1
    assert isinstance(payload["bias_awareness"], str)


def test_aqi_fallback_is_cached_for_repeated_requests(monkeypatch):
    calls = {"count": 0}

    def fake_get(*args, **kwargs):
        calls["count"] += 1
        raise requests.RequestException("network down")

    monkeypatch.setattr(india_context_service.requests, "get", fake_get)

    first = india_context_service.get_aqi_enrichment("delhi")
    second = india_context_service.get_aqi_enrichment("delhi")

    assert calls["count"] == 1
    assert first == second
    assert first["source"] == "local_estimate"
    assert first["city"] == "Delhi"


def test_model_artifact_is_persisted_and_loaded():
    metadata = get_model_metadata()
    assert ARTIFACT_PATH.exists()
    assert metadata["accuracy"] >= 0.85
    assert metadata["macro_f1"] >= 0.85


def test_api_smoke_for_history_and_auth_guards():
    headers = create_user("smoke@example.com")
    seed_history(headers)

    analyze_response = client.post(
        "/analysis/analyze",
        headers=headers,
        json={
            "description": "Feeling dizzy, pale, tired with heavy bleeding and cravings",
            "fatigue_level": 9,
            "sleep_quality": 4,
            "mood": "tired",
        },
    )
    assert analyze_response.status_code == 200

    analysis_history = client.get("/analysis/history", headers=headers)
    assert analysis_history.status_code == 200
    assert len(analysis_history.json()) >= 1

    unauthorized = client.get("/analysis/history")
    assert unauthorized.status_code == 401


def test_phase2_auth_smoke_register_login_me():
    email = f"phase2_{uuid4().hex[:8]}@example.com"

    register = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "name": "Phase2 Tester",
            "age": 27,
            "state": "Karnataka",
        },
    )
    assert register.status_code == 200

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_phase2_periods_smoke_create_list_calendar_and_invalid_dates():
    headers = create_user("phase2_periods@example.com")

    first = client.post(
        "/periods/",
        headers=headers,
        json={
            "start_date": "2026-03-01T00:00:00",
            "end_date": "2026-03-05T00:00:00",
            "flow_level": "medium",
            "symptoms": "mild cramps",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/periods/",
        headers=headers,
        json={
            "start_date": "2026-02-01T00:00:00",
            "end_date": "2026-02-05T00:00:00",
            "flow_level": "heavy",
            "symptoms": "fatigue",
        },
    )
    assert second.status_code == 200

    listed = client.get("/periods/", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 2

    calendar = client.get("/periods/calendar", headers=headers)
    assert calendar.status_code == 200
    assert "periods" in calendar.json()
    assert "prediction" in calendar.json()
    assert calendar.json()["prediction"] is not None

    invalid = client.post(
        "/periods/",
        headers=headers,
        json={
            "start_date": "2026-03-10T00:00:00",
            "end_date": "2026-03-01T00:00:00",
            "flow_level": "light",
            "symptoms": "invalid range",
        },
    )
    assert invalid.status_code == 422


def test_phase2_symptoms_smoke_list_limit_and_auth_guard():
    headers = create_user("phase2_symptoms@example.com")

    created = client.post(
        "/symptoms/",
        headers=headers,
        json={
            "description": "Feeling tired and sleepy today",
            "fatigue_level": 7,
            "sleep_quality": 4,
            "mood": "anxious",
        },
    )
    assert created.status_code == 200

    listed = client.get("/symptoms/?limit=5", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    unauthorized = client.get("/symptoms/")
    assert unauthorized.status_code == 401


def test_phase2_auth_missing_token_and_bad_payload():
    missing_token = client.get("/auth/me")
    assert missing_token.status_code == 401

    bad_login = client.post(
        "/auth/login",
        json={"email": "bad@example.com", "password": "wrongpass"},
    )
    assert bad_login.status_code == 401


def test_import_backend_app_main():
    import importlib
    mod = importlib.import_module("backend.app.main")
    assert hasattr(mod, "app"), "backend.app.main must expose 'app'"


def test_import_backend_main_shim():
    import importlib
    mod = importlib.import_module("backend.main")
    assert hasattr(mod, "app"), "backend.main shim must re-export 'app'"
