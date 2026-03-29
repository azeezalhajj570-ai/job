from __future__ import annotations

import json
from pathlib import Path

import joblib
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

from src.predictor import ModelArtifactsMissingError, PredictionService


def _build_artifacts(model_dir: Path) -> None:
    texts = [
        "urgent hiring work from home",
        "we are seeking a data analyst for our office",
    ]
    labels = [1, 0]

    vectorizer = TfidfVectorizer()
    transformed = vectorizer.fit_transform(texts)

    model = DummyClassifier(strategy="constant", constant=1, random_state=42)
    model.fit(transformed, labels)

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_dir / "fraud_detector.joblib")
    joblib.dump(vectorizer, model_dir / "tfidf_vectorizer.joblib")
    (model_dir / "model_metadata.json").write_text(
        json.dumps({"best_model": "DummyClassifier"}),
        encoding="utf-8",
    )


def test_prediction_service_loads_artifacts_and_predicts(tmp_path) -> None:
    model_dir = tmp_path / "models"
    _build_artifacts(model_dir)

    service = PredictionService(model_dir)
    result = service.predict("Earn money fast with no interview required")

    assert result["label"] == "Fraudulent"
    assert result["confidence"] == 100.0
    assert result["model_name"] == "DummyClassifier"
    assert result["cleaned_text"] == "earn money fast no interview required"


def test_prediction_service_requires_artifacts(tmp_path) -> None:
    with pytest.raises(ModelArtifactsMissingError):
        PredictionService(tmp_path / "missing-models")
