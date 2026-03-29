from __future__ import annotations

import sqlite3
from typing import Any


def get_connection(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: str) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_text TEXT NOT NULL,
                predicted_label TEXT NOT NULL,
                model_name TEXT NOT NULL DEFAULT 'Unknown',
                confidence REAL NOT NULL,
                input_length INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(predictions)").fetchall()
        }
        if "model_name" not in existing_columns:
            connection.execute(
                "ALTER TABLE predictions ADD COLUMN model_name TEXT NOT NULL DEFAULT 'Unknown'"
            )
        if "input_length" not in existing_columns:
            connection.execute(
                "ALTER TABLE predictions ADD COLUMN input_length INTEGER NOT NULL DEFAULT 0"
            )
        connection.commit()


def insert_prediction(
    database_path: str,
    job_text: str,
    predicted_label: str,
    confidence: float,
    model_name: str,
) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO predictions (job_text, predicted_label, model_name, confidence, input_length)
            VALUES (?, ?, ?, ?, ?)
            """,
            (job_text, predicted_label, model_name, confidence, len(job_text)),
        )
        connection.commit()


def get_dashboard_metrics(database_path: str) -> dict[str, Any]:
    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_jobs,
                SUM(CASE WHEN predicted_label = 'Fraudulent' THEN 1 ELSE 0 END) AS fraud_count,
                SUM(CASE WHEN predicted_label = 'Legitimate' THEN 1 ELSE 0 END) AS legitimate_count,
                AVG(confidence) AS avg_confidence,
                AVG(input_length) AS avg_input_length
            FROM predictions
            """
        ).fetchone()

    total_jobs = int(row["total_jobs"] or 0)
    fraud_count = int(row["fraud_count"] or 0)
    legitimate_count = int(row["legitimate_count"] or 0)
    avg_confidence = round(float(row["avg_confidence"] or 0.0), 2)
    avg_input_length = round(float(row["avg_input_length"] or 0.0), 1)
    fraud_rate = round((fraud_count / total_jobs) * 100, 2) if total_jobs else 0.0

    return {
        "total_jobs": total_jobs,
        "fraud_count": fraud_count,
        "legitimate_count": legitimate_count,
        "fraud_rate": fraud_rate,
        "avg_confidence": avg_confidence,
        "avg_input_length": avg_input_length,
    }


def get_recent_predictions(database_path: str, limit: int = 10) -> list[dict[str, Any]]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, job_text, predicted_label, model_name, confidence, input_length, created_at
            FROM predictions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_label_counts(database_path: str) -> dict[str, int]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT predicted_label, COUNT(*) AS count
            FROM predictions
            GROUP BY predicted_label
            """
        ).fetchall()

    counts = {"Fraudulent": 0, "Legitimate": 0}
    for row in rows:
        counts[row["predicted_label"]] = int(row["count"])
    return counts


def get_model_usage(database_path: str) -> list[dict[str, Any]]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT model_name, COUNT(*) AS count
            FROM predictions
            GROUP BY model_name
            ORDER BY count DESC, model_name ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]
