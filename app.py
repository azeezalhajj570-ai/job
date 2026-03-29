from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, flash, jsonify, render_template, request

from src.database import (
    get_dashboard_metrics,
    get_label_counts,
    get_model_usage,
    get_recent_predictions,
    initialize_database,
    insert_prediction,
)
from src.predictor import ModelArtifactsMissingError, PredictionService


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_EXAMPLES = [
    {
        "title": "Fraud-style example",
        "text": "Urgent remote opportunity. Earn thousands weekly with no interview. Submit your passport copy and onboarding fee today to secure your slot.",
    },
    {
        "title": "Legitimate-style example",
        "text": "We are hiring a backend engineer to build Flask APIs, write automated tests, and collaborate with product managers in a full-time hybrid role.",
    },
]


def load_model_metrics(model_dir: Path) -> dict[str, Any]:
    metrics_path = model_dir / "model_metrics.json"
    metadata_path = model_dir / "model_metadata.json"
    if not metrics_path.exists() or not metadata_path.exists():
        return {}

    with open(metrics_path, "r", encoding="utf-8") as metrics_file:
        metrics = json.load(metrics_file)
    with open(metadata_path, "r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    return {
        "metrics": metrics,
        "metadata": metadata,
    }


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "recruitment-fraud-detection-secret")
    app.config["DATABASE_PATH"] = str(BASE_DIR / "data" / "predictions.db")
    app.config["MODEL_DIR"] = str(BASE_DIR / "models")
    app.config["DEMO_EXAMPLES"] = DEFAULT_EXAMPLES

    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])

    try:
        predictor = PredictionService(model_dir=Path(app.config["MODEL_DIR"]))
    except ModelArtifactsMissingError:
        predictor = None

    model_report = load_model_metrics(Path(app.config["MODEL_DIR"]))

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        prediction_result: dict[str, Any] | None = None
        submitted_text = ""

        if request.method == "POST":
            submitted_text = (request.form.get("job_text") or "").strip()

            if not submitted_text:
                flash("Please provide a job description before submitting.", "error")
            elif predictor is None:
                flash(
                    "The ML model is not trained yet. Run `python -m src.train_model --data data/sample_job_postings.csv` first.",
                    "error",
                )
            else:
                prediction_result = predictor.predict(submitted_text)
                insert_prediction(
                    app.config["DATABASE_PATH"],
                    job_text=submitted_text,
                    predicted_label=prediction_result["label"],
                    confidence=prediction_result["confidence"],
                    model_name=prediction_result["model_name"],
                )

        return render_template(
            "index.html",
            prediction=prediction_result,
            submitted_text=submitted_text,
            model_ready=predictor is not None,
            model_report=model_report,
            demo_examples=app.config["DEMO_EXAMPLES"],
        )

    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        payload = request.get_json(silent=True) or {}
        job_text = (payload.get("job_text") or "").strip()

        if not job_text:
            return jsonify({"error": "job_text is required"}), 400

        if predictor is None:
            return jsonify({"error": "Model artifacts are missing. Train the model first."}), 503

        prediction_result = predictor.predict(job_text)
        insert_prediction(
            app.config["DATABASE_PATH"],
            job_text=job_text,
            predicted_label=prediction_result["label"],
            confidence=prediction_result["confidence"],
            model_name=prediction_result["model_name"],
        )
        return jsonify(prediction_result)

    @app.route("/dashboard")
    def dashboard() -> str:
        return render_template(
            "dashboard.html",
            metrics=get_dashboard_metrics(app.config["DATABASE_PATH"]),
            recent_predictions=get_recent_predictions(app.config["DATABASE_PATH"], limit=10),
            chart_data=get_label_counts(app.config["DATABASE_PATH"]),
            model_usage=get_model_usage(app.config["DATABASE_PATH"]),
            model_report=model_report,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
