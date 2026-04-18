# Project Audit

## Repository summary

- Project title: `Recruitment Fraud Detection in Online Job Portals`
- Main entry point: `app.py`
- Core stack: Flask, SQLite, pandas, scikit-learn, joblib, Tailwind CSS, Chart.js
- ML task: binary text classification of job posts into `Fraudulent` or `Legitimate`
- Current trained model: `Logistic Regression`
- Current feature space size: `169`
- Metrics file generated at: `2026-04-10T17:24:27.058084+00:00`

## Evidence-based module inventory

| Area | Evidence | Assessment |
| --- | --- | --- |
| Web app | `app.py`, `templates/*.html`, `static/css/styles.css`, `static/js/app.js` | Implemented and demonstrable |
| Authentication | Shared sign-in and sign-up flows in `app.py`, hashed passwords via `werkzeug.security`, role checks in `login_required` and `admin_required` | Implemented |
| Prediction service | `src/predictor.py` loads a saved joblib model and vectorizer, returns label, confidence, terms, and risk summary | Implemented |
| Training pipeline | `src/train_model.py` trains four classical ML models and persists the best one with metadata and metrics | Implemented |
| Data preprocessing | `src/data_preprocessing.py` handles text cleaning, label normalization, and column detection | Implemented |
| Persistence | `src/database.py` initializes SQLite tables for users and predictions and exposes dashboard queries | Implemented |
| UI pages | `/signin`, `/signup`, `/overview`, `/predict`, `/signals`, `/dashboard` plus `/api/predict` | Implemented |
| Automated testing | `tests/` covers preprocessing, database, predictor, and Flask routes | Present, with one route-import issue fixed in this pass |

## Existing documentation classification

| File | Classification | Notes |
| --- | --- | --- |
| `README.md` | Partially accurate | Good high-level summary, but it did not fully support submission deliverables or documentation workflow |
| `docs/Recruitment_Fraud_Detection_Graduation_Report.docx` | Reusable with restructuring | Strong starting structure, but needed tighter sample alignment and more explicit evidence from code |
| `docs/diagrams/*.png` | Partially accurate | Useful conceptually, but no editable source files and inconsistent academic packaging |
| `scripts/generate_graduation_report.py` | Reusable idea, outdated output shape | Generated a DOCX, but not in the exact final deliverable path and not tied to screenshot capture |

## Route inventory

| Route | Methods | Purpose | Access |
| --- | --- | --- | --- |
| `/` | GET | Redirect authenticated users to the overview page | Authenticated |
| `/overview` | GET | Present model readiness, metrics, and workflow summary | Authenticated |
| `/predict` | GET, POST | Run text classification from the web form | Authenticated |
| `/signals` | GET | Explain common fraud and legitimate language patterns | Authenticated |
| `/api/predict` | POST | Return JSON prediction results | Authenticated |
| `/dashboard` | GET | Show aggregate metrics and recent predictions | Admin |
| `/signup` | GET, POST | Register a normal user | Public |
| `/signin` | GET, POST | Sign in for both roles | Public |
| `/admin/signup` | GET, POST | Register an admin with signup code | Public |
| `/logout` | GET | Clear the session | Authenticated |

## Dataset observations

- `data/sample_job_postings.csv` contains 10 labeled records with a balanced split of 5 fraudulent and 5 legitimate samples.
- `data/sample_jobs.csv` contains 16 labeled records with a balanced split of 8 fraudulent and 8 legitimate samples.
- The bundled datasets are sufficient for demonstration and code validation, but not for claiming production-grade accuracy.

## Model observations

- The training script evaluates Logistic Regression, Naive Bayes, Support Vector Machine, and Random Forest.
- On the current 10-row bundled sample dataset, Logistic Regression is selected as the best model.
- The hold-out test split reports perfect scores because the test set contains only 2 records; the cross-validation mean F1 score of `0.1667` shows that the tiny dataset makes those perfect scores unstable.
