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
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def insert_prediction(database_path: str, job_text: str, predicted_label: str, confidence: float) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO predictions (job_text, predicted_label, confidence)
            VALUES (?, ?, ?)
            """,
            (job_text, predicted_label, confidence),
        )
        connection.commit()


def get_dashboard_metrics(database_path: str) -> dict[str, Any]:
    with get_connection(database_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_jobs,
                SUM(CASE WHEN predicted_label = 'Fraudulent' THEN 1 ELSE 0 END) AS fraud_count,
                SUM(CASE WHEN predicted_label = 'Legitimate' THEN 1 ELSE 0 END) AS legitimate_count
            FROM predictions
            """
        ).fetchone()

    total_jobs = int(row["total_jobs"] or 0)
    fraud_count = int(row["fraud_count"] or 0)
    legitimate_count = int(row["legitimate_count"] or 0)
    fraud_rate = round((fraud_count / total_jobs) * 100, 2) if total_jobs else 0.0

    return {
        "total_jobs": total_jobs,
        "fraud_count": fraud_count,
        "legitimate_count": legitimate_count,
        "fraud_rate": fraud_rate,
    }


def get_recent_predictions(database_path: str, limit: int = 10) -> list[dict[str, Any]]:
    with get_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, job_text, predicted_label, confidence, created_at
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
