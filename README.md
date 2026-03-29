# Recruitment Fraud Detection in Online Job Portals

This project implements the proposal as a complete Flask application backed by an NLP and machine-learning pipeline for classifying online job posts as `Fraudulent` or `Legitimate`.

## What the project includes

- Text preprocessing with lowercasing, punctuation and number removal, stop-word filtering, and whitespace normalization
- TF-IDF feature extraction with unigram and bigram support
- Model comparison across Logistic Regression, Naive Bayes, SVM, and Random Forest
- Automatic best-model selection using F1 score, cross-validation support, and stored evaluation metrics
- Flask prediction interface for end users
- Monitoring dashboard for administrators with fraud rate, confidence averages, model usage, and recent activity
- SQLite logging of every analyzed posting
- Automated tests for preprocessing, persistence, prediction, and Flask routes

## Project structure

```text
job/
├── app.py
├── requirements.txt
├── data/
│   ├── sample_job_postings.csv
│   └── sample_jobs.csv
├── src/
│   ├── data_preprocessing.py
│   ├── database.py
│   ├── predictor.py
│   └── train_model.py
├── templates/
├── static/
└── tests/
```

## Dataset expectations

The training CSV should contain:

- A text column such as `description`, `job_description`, `job_text`, `text`, or `content`
- A target column such as `fraudulent`, `is_fraud`, `label`, `target`, or `class`

Optional columns such as `title`, `company`, `location`, `requirements`, and `benefits` are merged into the training text when present.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Train the model

```bash
python -m src.train_model --data data/sample_job_postings.csv --model-dir models
```

Training generates:

- `models/fraud_detector.joblib`
- `models/tfidf_vectorizer.joblib`
- `models/model_metrics.json`
- `models/model_metadata.json`

## Run the app

```bash
python app.py
```

Open:

- `http://127.0.0.1:5000/` for prediction
- `http://127.0.0.1:5000/dashboard` for monitoring

## Run tests

```bash
pytest
```

## Proposal alignment

The implementation maps directly to the proposal:

- Intelligent job post analysis: NLP preprocessing, TF-IDF, and multiple ML classifiers
- Web-based prediction platform: Flask UI for manual prediction and JSON API support
- Fraud detection monitoring dashboard: summary metrics, chart data, model usage, and recent predictions
- Quality assurance: automated tests plus cross-validation metrics in the training workflow

## Future extensions

- Integrate live job portal APIs
- Add multilingual processing
- Evaluate transformer-based classifiers
- Add analyst review workflows and exportable reports
