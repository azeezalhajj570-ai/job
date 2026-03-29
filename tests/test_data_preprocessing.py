from __future__ import annotations

import pandas as pd
import pytest

from src.data_preprocessing import clean_text, load_training_data, normalize_labels


def test_clean_text_normalizes_case_numbers_and_punctuation() -> None:
    text = "Urgent! Earn 5000 dollars/week, NOW!!"

    assert clean_text(text) == "urgent earn dollarsweek now"


def test_normalize_labels_supports_common_label_encodings() -> None:
    labels = ["Fraudulent", "legitimate", "yes", "no", 1, 0, "spam", "ham"]

    result = normalize_labels(labels)

    assert result.tolist() == [1, 0, 1, 0, 1, 0, 1, 0]


def test_load_training_data_detects_expected_columns(sample_csv_path) -> None:
    bundle = load_training_data(str(sample_csv_path))

    assert bundle.text_column == "description"
    assert bundle.target_column == "fraudulent"
    assert len(bundle.texts) == 10
    assert set(bundle.labels.unique().tolist()) <= {0, 1}
    assert bundle.texts.iloc[0] == "immediate hiring work home earn dollars weekly no interview required send bank details get started today"


def test_load_training_data_rejects_empty_dataset(tmp_path) -> None:
    csv_path = tmp_path / "empty.csv"
    pd.DataFrame(columns=["description", "fraudulent"]).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="dataset is empty"):
        load_training_data(str(csv_path))
