from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

from src.data_preprocessing import clean_text


class ModelArtifactsMissingError(FileNotFoundError):
    """Raised when trained model files are not available."""


class PredictionService:
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "fraud_detector.joblib"
        self.vectorizer_path = self.model_dir / "tfidf_vectorizer.joblib"
        self.metadata_path = self.model_dir / "model_metadata.json"

        if not self.model_path.exists() or not self.vectorizer_path.exists():
            raise ModelArtifactsMissingError("Missing model artifacts.")

        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def predict(self, text: str) -> dict:
        cleaned_text = clean_text(text)
        transformed_text = self.vectorizer.transform([cleaned_text])
        predicted_class = int(self.model.predict(transformed_text)[0])

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(transformed_text)[0]
            confidence = float(np.max(probabilities))
        elif hasattr(self.model, "decision_function"):
            score = float(self.model.decision_function(transformed_text)[0])
            confidence = float(1 / (1 + np.exp(-abs(score))))
        else:
            confidence = 0.5

        return {
            "label": "Fraudulent" if predicted_class == 1 else "Legitimate",
            "confidence": round(confidence * 100, 2),
            "model_name": self.metadata.get("best_model", "Unknown"),
            "cleaned_text": cleaned_text,
        }
