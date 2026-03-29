from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

    def _extract_supporting_terms(self, transformed_text) -> list[str]:
        feature_names = self.vectorizer.get_feature_names_out()

        if hasattr(self.model, "coef_"):
            scores = transformed_text.multiply(self.model.coef_[0]).toarray()[0]
        elif hasattr(self.model, "feature_importances_"):
            scores = transformed_text.multiply(self.model.feature_importances_).toarray()[0]
        else:
            return []

        ranked_indices = np.argsort(scores)[::-1]
        terms: list[str] = []
        for index in ranked_indices:
            if scores[index] <= 0:
                continue
            term = str(feature_names[index])
            if term not in terms:
                terms.append(term)
            if len(terms) == 5:
                break
        return terms

    def _build_risk_summary(self, label: str, supporting_terms: list[str]) -> list[str]:
        if label == "Fraudulent":
            summary = [
                "The text contains language patterns frequently associated with scam recruitment posts.",
                "High-confidence fraud predictions usually correlate with urgency, payment requests, or unrealistic earnings claims.",
            ]
        else:
            summary = [
                "The text aligns more closely with structured job descriptions seen in legitimate recruitment posts.",
                "Legitimate predictions usually include responsibilities, skills, and a standard hiring process.",
            ]

        if supporting_terms:
            summary.append(f"Top contributing terms: {', '.join(supporting_terms)}.")
        return summary

    def predict(self, text: str) -> dict[str, Any]:
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

        label = "Fraudulent" if predicted_class == 1 else "Legitimate"
        supporting_terms = self._extract_supporting_terms(transformed_text)

        return {
            "label": label,
            "confidence": round(confidence * 100, 2),
            "model_name": self.metadata.get("best_model", "Unknown"),
            "cleaned_text": cleaned_text,
            "supporting_terms": supporting_terms,
            "risk_summary": self._build_risk_summary(label, supporting_terms),
        }
