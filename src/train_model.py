from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from src.data_preprocessing import DatasetBundle, load_training_data


RANDOM_STATE = 42


def build_models() -> dict[str, object]:
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Naive Bayes": MultinomialNB(),
        "Support Vector Machine": SVC(
            kernel="linear",
            probability=True,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
    }


def evaluate_model(model: object, x_train, x_test, y_train, y_test) -> dict:
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }


def train_and_select_model(dataset: DatasetBundle, model_dir: Path) -> dict:
    x_train, x_test, y_train, y_test = train_test_split(
        dataset.texts,
        dataset.labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=dataset.labels,
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=7000)
    x_train_vectorized = vectorizer.fit_transform(x_train)
    x_test_vectorized = vectorizer.transform(x_test)

    trained_models: dict[str, object] = {}
    metrics_by_model: dict[str, dict] = {}

    for model_name, model in build_models().items():
        metrics_by_model[model_name] = evaluate_model(
            model=model,
            x_train=x_train_vectorized,
            x_test=x_test_vectorized,
            y_train=y_train,
            y_test=y_test,
        )
        trained_models[model_name] = model

    best_model_name = max(metrics_by_model, key=lambda name: metrics_by_model[name]["f1_score"])
    best_model = trained_models[best_model_name]

    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, model_dir / "fraud_detector.joblib")
    joblib.dump(vectorizer, model_dir / "tfidf_vectorizer.joblib")

    metadata = {
        "best_model": best_model_name,
        "random_state": RANDOM_STATE,
        "text_column": dataset.text_column,
        "target_column": dataset.target_column,
        "train_size": int(len(x_train)),
        "test_size": int(len(x_test)),
        "class_distribution": {
            "legitimate": int(np.sum(dataset.labels == 0)),
            "fraudulent": int(np.sum(dataset.labels == 1)),
        },
    }

    with open(model_dir / "model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics_by_model, file, indent=2)
    with open(model_dir / "model_metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    return {
        "best_model_name": best_model_name,
        "metrics": metrics_by_model,
        "metadata": metadata,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the recruitment fraud detection model.")
    parser.add_argument("--data", required=True, help="Path to the CSV dataset.")
    parser.add_argument("--model-dir", default="models", help="Directory to store trained artifacts.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = load_training_data(args.data)
    result = train_and_select_model(dataset, Path(args.model_dir))
    print(f"Best model: {result['best_model_name']}")
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
