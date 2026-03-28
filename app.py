from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, flash, jsonify, render_template, request

from src.database import (
    get_dashboard_metrics,
    get_label_counts,
    get_recent_predictions,
    initialize_database,
    insert_prediction,
)
from src.predictor import ModelArtifactsMissingError, PredictionService


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "recruitment-fraud-detection-secret")
    app.config["DATABASE_PATH"] = str(BASE_DIR / "data" / "predictions.db")

    initialize_database(app.config["DATABASE_PATH"])

    try:
        predictor = PredictionService(model_dir=BASE_DIR / "models")
    except ModelArtifactsMissingError:
        predictor = None

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
                )

        return render_template(
            "index.html",
            prediction=prediction_result,
            submitted_text=submitted_text,
            model_ready=predictor is not None,
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
        )
        return jsonify(prediction_result)

    @app.route("/dashboard")
    def dashboard() -> str:
        return render_template(
            "dashboard.html",
            metrics=get_dashboard_metrics(app.config["DATABASE_PATH"]),
            recent_predictions=get_recent_predictions(app.config["DATABASE_PATH"], limit=10),
            chart_data=get_label_counts(app.config["DATABASE_PATH"]),
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
