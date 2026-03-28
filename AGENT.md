# AGENT.md

## Purpose

This repository contains a graduation-level Flask and machine learning project for detecting fraudulent job advertisements in online job portals.

## Working Guidelines

- Keep the application modular and presentation-ready.
- Preserve the existing project structure.
- Store trained models in `models/`.
- Store persistent application data in `data/`.
- Keep the UI modern, responsive, and easy to demonstrate.

## Main Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Train the model:

```bash
python -m src.train_model --data data/sample_job_postings.csv
```

Run the web app:

```bash
python app.py
```

## Notes

- The app gracefully handles the case where model artifacts are not trained yet.
- Prediction history is stored in SQLite at `data/predictions.db`.
- The best model is selected automatically based on validation F1-score.
