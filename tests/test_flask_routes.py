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


def test_flask_routes_support_prediction_api_and_dashboard(app_module):
    flask_app = app_module.create_app()
    client = flask_app.test_client()

    index_response = client.post(
        "/",
        data={"job_text": "Urgent work from home role. Payment required to start."},
    )
    api_response = client.post(
        "/api/predict",
        json={"job_text": "We are hiring a Python developer for our office."},
    )
    dashboard_response = client.get("/dashboard")

    assert index_response.status_code == 200
    assert b"Fraudulent" in index_response.data
    assert b"DummyRouteModel" in index_response.data
    assert api_response.status_code == 200
    assert api_response.get_json()["label"] == "Legitimate"
    assert dashboard_response.status_code == 200
    assert b"Prediction Distribution" in dashboard_response.data
    assert b"Recent Predictions" in dashboard_response.data
