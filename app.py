from __future__ import annotations

import json
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from src.database import (
    create_user,
    ensure_demo_user,
    get_dashboard_metrics,
    get_label_counts,
    get_model_usage,
    get_recent_predictions,
    get_user_by_email,
    get_user_by_id,
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


def login_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.current_user is None:
            flash("Please sign in first.", "error")
            return redirect(url_for("user_signin"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.current_user is None:
            flash("Please sign in as admin first.", "error")
            return redirect(url_for("admin_signin"))
        if g.current_user["role"] != "admin":
            flash("Admin access is required for this page.", "error")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped_view


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "recruitment-fraud-detection-secret")
    app.config["DATABASE_PATH"] = str(BASE_DIR / "data" / "predictions.db")
    app.config["MODEL_DIR"] = str(BASE_DIR / "models")
    app.config["DEMO_EXAMPLES"] = DEFAULT_EXAMPLES
    app.config["ADMIN_SIGNUP_CODE"] = os.getenv("ADMIN_SIGNUP_CODE", "admin123")

    if test_config:
        app.config.update(test_config)

    initialize_database(app.config["DATABASE_PATH"])
    ensure_demo_user(
        app.config["DATABASE_PATH"],
        full_name="Demo User",
        email="user",
        password_hash=generate_password_hash("user"),
        role="user",
    )
    ensure_demo_user(
        app.config["DATABASE_PATH"],
        full_name="Demo Admin",
        email="admin",
        password_hash=generate_password_hash("admin"),
        role="admin",
    )

    try:
        predictor = PredictionService(model_dir=Path(app.config["MODEL_DIR"]))
    except ModelArtifactsMissingError:
        predictor = None

    model_report = load_model_metrics(Path(app.config["MODEL_DIR"]))

    @app.before_request
    def load_current_user() -> None:
        user_id = session.get("user_id")
        g.current_user = None
        if user_id is not None:
            g.current_user = get_user_by_id(app.config["DATABASE_PATH"], int(user_id))

    @app.context_processor
    def inject_auth_state() -> dict[str, Any]:
        return {"current_user": g.get("current_user")}

    def handle_signup(role: str) -> str:
        if g.current_user is not None:
            return redirect(url_for("index"))

        if request.method == "POST":
            full_name = (request.form.get("full_name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            admin_code = request.form.get("admin_code") or ""

            if not full_name or not email or not password:
                flash("All fields are required.", "error")
            elif get_user_by_email(app.config["DATABASE_PATH"], email):
                flash("An account with this email already exists.", "error")
            elif role == "admin" and admin_code != app.config["ADMIN_SIGNUP_CODE"]:
                flash("Invalid admin signup code.", "error")
            else:
                user_id = create_user(
                    app.config["DATABASE_PATH"],
                    full_name=full_name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                )
                session.clear()
                session["user_id"] = user_id
                flash("Account created successfully.", "success")
                return redirect(url_for("dashboard" if role == "admin" else "index"))

        return render_template(
            "auth.html",
            page_mode="signup",
            role=role,
            title=f"{role.title()} Sign Up",
        )

    def handle_signin(role: str) -> str:
        if g.current_user is not None and g.current_user["role"] == role:
            return redirect(url_for("dashboard" if role == "admin" else "index"))

        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            user = get_user_by_email(app.config["DATABASE_PATH"], email)

            if user is None or user["role"] != role or not check_password_hash(
                user["password_hash"], password
            ):
                flash("Invalid credentials.", "error")
            else:
                session.clear()
                session["user_id"] = user["id"]
                flash("Signed in successfully.", "success")
                return redirect(url_for("dashboard" if role == "admin" else "index"))

        return render_template(
            "auth.html",
            page_mode="signin",
            role=role,
            title=f"{role.title()} Sign In",
        )

    @app.route("/")
    @login_required
    def home_redirect() -> str:
        return redirect(url_for("index"))

    @app.route("/predict", methods=["GET", "POST"])
    @login_required
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
    @login_required
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
    @admin_required
    def dashboard() -> str:
        return render_template(
            "dashboard.html",
            metrics=get_dashboard_metrics(app.config["DATABASE_PATH"]),
            recent_predictions=get_recent_predictions(app.config["DATABASE_PATH"], limit=10),
            chart_data=get_label_counts(app.config["DATABASE_PATH"]),
            model_usage=get_model_usage(app.config["DATABASE_PATH"]),
            model_report=model_report,
        )

    @app.route("/signup", methods=["GET", "POST"])
    def user_signup() -> str:
        return handle_signup("user")

    @app.route("/signin", methods=["GET", "POST"])
    def user_signin() -> str:
        return handle_signin("user")

    @app.route("/admin/signup", methods=["GET", "POST"])
    def admin_signup() -> str:
        return handle_signup("admin")

    @app.route("/admin/signin", methods=["GET", "POST"])
    def admin_signin() -> str:
        return handle_signin("admin")

    @app.route("/logout")
    def logout() -> str:
        session.clear()
        flash("You have been signed out.", "success")
        return redirect(url_for("user_signin"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
