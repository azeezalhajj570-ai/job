# Recruitment Fraud Detection in Online Job Portals

This repository implements a graduation-level applied project that detects fraudulent recruitment posts from text input. The system combines a Flask web application, an SQLite persistence layer, and a scikit-learn text-classification pipeline built around TF-IDF features.

## What is implemented

- Shared sign-in and sign-up flows for normal users and administrators
- Role-protected routes for prediction and dashboard access
- Text preprocessing with lowercasing, punctuation removal, number removal, stop-word filtering, and whitespace normalization
- Model comparison across Logistic Regression, Naive Bayes, Support Vector Machine, and Random Forest
- Automatic best-model selection with saved metrics and metadata
- Web pages for overview, prediction, detection signals, and the administrator dashboard
- SQLite logging of prediction results
- Automated tests for preprocessing, database logic, predictor behavior, and Flask routes
- Submission assets for diagrams, screenshots, audit notes, and the editable final DOCX report

## Repository structure

```text
job/
├── app.py
├── requirements.txt
├── data/
├── docs/
├── models/
├── scripts/
├── src/
├── static/
├── submission/
├── templates/
└── tests/
```

## Core files

- `app.py`: Flask app factory, routes, authentication, and page rendering
- `src/data_preprocessing.py`: dataset loading, text cleaning, and label normalization
- `src/train_model.py`: model training, evaluation, and artifact persistence
- `src/predictor.py`: runtime inference service
- `src/database.py`: SQLite schema and dashboard queries
- `scripts/capture_screenshots.py`: Playwright-based screenshot capture
- `scripts/build_submission_assets.py`: generates UML assets, markdown docs, and `submission/Project_Report.docx`

## Dataset expectations

The training script expects:

- A text column such as `description`, `job_description`, `job_text`, `text`, or `content`
- A target column such as `fraudulent`, `is_fraud`, `label`, `target`, or `class`

Optional context columns such as `title`, `company`, `location`, `requirements`, and `benefits` are merged into the training text when they are present.

## Setup

```bash
python -m pip install -r requirements.txt python-docx playwright
```

If you need browser-based screenshot capture, install Chromium for Playwright in a writable location:

```bash
env PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright python -m playwright install chromium
```

## Train the model

```bash
python -m src.train_model --data data/sample_job_postings.csv --model-dir models
```

Artifacts written by training:

- `models/fraud_detector.joblib`
- `models/tfidf_vectorizer.joblib`
- `models/model_metrics.json`
- `models/model_metadata.json`

## Run the application

```bash
python app.py
```

The default local URL is `http://127.0.0.1:5003`.

Key routes:

- `/signin`
- `/signup`
- `/overview`
- `/predict`
- `/signals`
- `/dashboard`
- `/api/predict`

Demo accounts created automatically:

- User: `user` / `user`
- Admin: `admin` / `admin`

## Run tests

```bash
pytest -q
```

## Build the report deliverables

1. Train the model.
2. Start the Flask application.
3. Capture screenshots:

   ```bash
   env PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright python scripts/capture_screenshots.py
   ```

4. Generate diagrams, markdown documentation, and the final editable report:

   ```bash
   python scripts/build_submission_assets.py
   ```

Main outputs:

- `submission/Project_Report.docx`
- `docs/00_project_audit.md`
- `docs/01_missing_documentation_gaps.md`
- `docs/PROJECT_SUBMISSION_CHECKLIST.md`
- `docs/diagrams/*.png`
- `docs/diagrams/sources/*.mmd`
- `docs/screenshots/*.png`

## Current model note

The bundled demonstration dataset is very small. The persisted metrics are useful for verifying the pipeline and explaining the workflow, but they should not be presented as strong evidence of production-level performance.

## Current limitations

- No live recruitment-platform API integration
- No multilingual processing
- No deep-learning or transformer-based classifier
- No image, link, or attachment analysis
- No user-to-prediction ownership link in the current SQLite schema
