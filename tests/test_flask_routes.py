from __future__ import annotations

import importlib

import pytest

import src.database as database_module
from src.database import initialize_database as real_initialize_database


class DummyPredictionService:
    def __init__(self, model_dir):
        self.model_dir = model_dir

    def predict(self, text: str) -> dict:
        label = "Fraudulent" if "urgent" in text.lower() or "payment" in text.lower() else "Legitimate"
        confidence = 96.4 if label == "Fraudulent" else 88.1
        return {
            "label": label,
            "confidence": confidence,
            "model_name": "DummyRouteModel",
            "cleaned_text": text.lower(),
            "risk_summary": [],
            "supporting_terms": [],
        }


@pytest.fixture()
def app_module(monkeypatch, tmp_path):
    monkeypatch.setattr(database_module, "initialize_database", lambda *_args, **_kwargs: None)
    module = importlib.import_module("app")
    monkeypatch.setattr(module, "BASE_DIR", tmp_path)
    monkeypatch.setattr(module, "initialize_database", real_initialize_database)
    monkeypatch.setattr(module, "PredictionService", DummyPredictionService)
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    return module


def create_user_account(client, path: str, **extra_fields) -> None:
    payload = {
        "full_name": "Student User",
        "email": "student@example.com",
        "password": "password123",
    }
    payload.update(extra_fields)
    response = client.post(path, data=payload, follow_redirects=True)
    assert response.status_code == 200


def test_user_routes_require_authentication(app_module):
    flask_app = app_module.create_app({"ADMIN_SIGNUP_CODE": "secret-admin"})
    client = flask_app.test_client()

    home_response = client.get("/", follow_redirects=False)
    predict_response = client.get("/predict", follow_redirects=False)
    api_response = client.post("/api/predict", json={"job_text": "test"}, follow_redirects=False)

    assert home_response.status_code == 302
    assert "/signin" in home_response.headers["Location"]
    assert predict_response.status_code == 302
    assert "/signin" in predict_response.headers["Location"]
    assert api_response.status_code == 302


def test_user_signup_signin_and_prediction_flow(app_module):
    flask_app = app_module.create_app({"ADMIN_SIGNUP_CODE": "secret-admin"})
    client = flask_app.test_client()

    create_user_account(client, "/signup")
    prediction_response = client.post(
        "/predict",
        data={"job_text": "Urgent work from home role. Payment required to start."},
        follow_redirects=True,
    )
    dashboard_response = client.get("/dashboard", follow_redirects=True)

    assert prediction_response.status_code == 200
    assert b"Fraudulent" in prediction_response.data
    assert b"DummyRouteModel" in prediction_response.data
    assert dashboard_response.status_code == 200
    assert b"Admin access is required for this page." in dashboard_response.data


def test_admin_signup_signin_and_dashboard_access(app_module):
    flask_app = app_module.create_app({"ADMIN_SIGNUP_CODE": "secret-admin"})
    client = flask_app.test_client()

    response = client.post(
        "/admin/signup",
        data={
            "full_name": "System Admin",
            "email": "admin@example.com",
            "password": "adminpass123",
            "admin_code": "secret-admin",
        },
        follow_redirects=True,
    )
    dashboard_response = client.get("/dashboard", follow_redirects=True)

    assert response.status_code == 200
    assert b"Prediction activity and fraud monitoring" in response.data
    assert dashboard_response.status_code == 200
    assert b"Recent Predictions" in dashboard_response.data
