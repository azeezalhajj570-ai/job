from __future__ import annotations

import re
import string
from dataclasses import dataclass
from typing import Iterable

import pandas as pd


TEXT_COLUMN_CANDIDATES = [
    "description",
    "job_description",
    "job_text",
    "text",
    "content",
]

TARGET_COLUMN_CANDIDATES = [
    "fraudulent",
    "is_fraud",
    "label",
    "target",
    "class",
]


@dataclass
class DatasetBundle:
    texts: pd.Series
    labels: pd.Series
    text_column: str
    target_column: str


def clean_text(text: str) -> str:
    """Lowercase, remove punctuation/numbers, and normalize whitespace."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)

    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_labels(labels: Iterable) -> pd.Series:
    normalized = []
    for value in labels:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "fraud", "fraudulent", "yes", "spam"}:
                normalized.append(1)
            elif lowered in {"0", "false", "legitimate", "real", "no", "ham"}:
                normalized.append(0)
            else:
                raise ValueError(f"Unsupported target label value: {value}")
        else:
            normalized.append(int(value))
    return pd.Series(normalized, dtype="int64")


def detect_column(columns: Iterable[str], candidates: list[str], column_kind: str) -> str:
    lowered_map = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in lowered_map:
            return lowered_map[candidate]
    raise ValueError(
        f"Unable to detect the {column_kind} column. Expected one of: {', '.join(candidates)}"
    )


def load_training_data(csv_path: str) -> DatasetBundle:
    dataframe = pd.read_csv(csv_path)
    if dataframe.empty:
        raise ValueError("The dataset is empty.")

    text_column = detect_column(dataframe.columns, TEXT_COLUMN_CANDIDATES, "text")
    target_column = detect_column(dataframe.columns, TARGET_COLUMN_CANDIDATES, "target")

    working_df = dataframe[[text_column, target_column]].dropna().copy()
    if working_df.empty:
        raise ValueError("No usable rows remained after dropping missing values.")

    working_df[text_column] = working_df[text_column].astype(str).map(clean_text)
    working_df[target_column] = normalize_labels(working_df[target_column])

    return DatasetBundle(
        texts=working_df[text_column],
        labels=working_df[target_column],
        text_column=text_column,
        target_column=target_column,
    )
