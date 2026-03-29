from __future__ import annotations

from src.database import (
    get_dashboard_metrics,
    get_label_counts,
    get_recent_predictions,
    initialize_database,
    insert_prediction,
)


def test_database_metrics_and_recent_predictions(tmp_path) -> None:
    db_path = tmp_path / "predictions.db"
    initialize_database(str(db_path))

    insert_prediction(str(db_path), "fake job one", "Fraudulent", 98.2, "Model A")
    insert_prediction(str(db_path), "legit job two", "Legitimate", 87.5, "Model B")
    insert_prediction(str(db_path), "fake job three", "Fraudulent", 91.0, "Model A")

    metrics = get_dashboard_metrics(str(db_path))
    label_counts = get_label_counts(str(db_path))
    recent = get_recent_predictions(str(db_path), limit=2)

    assert metrics == {
        "total_jobs": 3,
        "fraud_count": 2,
        "legitimate_count": 1,
        "fraud_rate": 66.67,
        "avg_confidence": 92.23,
        "avg_input_length": 13.0,
    }
    assert label_counts == {"Fraudulent": 2, "Legitimate": 1}
    assert len(recent) == 2
    assert recent[0]["predicted_label"] == "Fraudulent"
    assert recent[0]["job_text"] == "fake job three"
    assert recent[0]["model_name"] == "Model A"
