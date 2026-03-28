# Recruitment Fraud Detection in Online Job Portals

Recruitment Fraud Detection in Online Job Portals is a graduation-level machine learning project that classifies job advertisements as either fraudulent or legitimate. The system combines NLP preprocessing, TF-IDF feature engineering, multiple supervised learning models, and a Flask web application with a professional dashboard for monitoring predictions.

## Project Objectives

- Detect suspicious job postings automatically from free-text descriptions.
- Compare several machine learning models and keep the best one based on F1-score.
- Provide a polished web interface for end users and administrators.
- Store prediction history for analytics and presentation during demonstrations.
- Keep the codebase modular, documented, and easy to extend for academic evaluation.

## System Architecture

The project is divided into four layers:

1. Data preprocessing in [src/data_preprocessing.py](/c:/Users/pc/Desktop/UNI-PROJECTS/job/src/data_preprocessing.py) for text cleaning and dataset column resolution.
2. Model training in [src/train_model.py](/c:/Users/pc/Desktop/UNI-PROJECTS/job/src/train_model.py) using TF-IDF plus Logistic Regression, Naive Bayes, SVM, and Random Forest.
3. Prediction and persistence in [src/predictor.py](/c:/Users/pc/Desktop/UNI-PROJECTS/job/src/predictor.py) and [src/database.py](/c:/Users/pc/Desktop/UNI-PROJECTS/job/src/database.py).
4. Presentation layer in [app.py](/c:/Users/pc/Desktop/UNI-PROJECTS/job/app.py) and the templates inside [templates/](/c:/Users/pc/Desktop/UNI-PROJECTS/job/templates).

## Technologies Used

- Python 3.x
- Flask
- scikit-learn
- pandas
- numpy
- SQLite
- Tailwind CSS
- Chart.js

## Project Structure

```text
project/
├── app.py
├── requirements.txt
├── README.md
├── AGENT.md
├── data/
│   └── sample_jobs.csv
├── models/
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── predictor.py
│   └── database.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── app.js
```

## Dataset Format

The dataset should be a CSV file containing:

- A text column such as `description`, `job_description`, `text`, or `job_text`
- A target column such as `fraudulent`, `label`, `target`, `is_fraud`, or `class`

Labels can be expressed as `0/1`, `true/false`, `yes/no`, `fraudulent/legitimate`, or similar equivalents. A small demo dataset is included at [data/sample_jobs.csv](/c:/Users/pc/Desktop/UNI-PROJECTS/job/data/sample_jobs.csv) so the training workflow can run immediately.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: define a custom Flask secret key for deployment:

```bash
set FLASK_SECRET_KEY=your-secret-key
```

## How to Train the Model

Run the training pipeline with the included sample dataset:

```bash
python -m src.train_model --data data/sample_jobs.csv
```

Optional arguments:

- `--text-column` to force the text column name
- `--target-column` to force the target column name
- `--test-size` to control the validation split
- `--random-state` to keep experiments reproducible

The training step saves:

- `models/best_model.joblib`
- `models/tfidf_vectorizer.joblib`
- `models/model_metadata.json`

## How to Run the System

After training the model:

```bash
python app.py
```

Open `http://127.0.0.1:5000` for the prediction page and `http://127.0.0.1:5000/dashboard` for the analytics dashboard.

## Application Features

- Job posting fraud prediction with confidence score
- Input validation and clear error feedback
- SQLite logging for every analyzed job
- Admin dashboard with fraud metrics and recent predictions
- Responsive interface suitable for desktop and mobile demonstrations

## Model Evaluation

The training script evaluates the following algorithms:

- Logistic Regression
- Multinomial Naive Bayes
- Support Vector Machine
- Random Forest

Metrics generated for each model:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

The best model is selected automatically according to F1-score, which is the primary metric for fraud detection because it balances false positives and false negatives.

## Screenshots

- Home page screenshot: add a capture of the prediction interface here.
- Dashboard screenshot: add a capture of the analytics page here.
- Training output screenshot: add terminal metrics here.

## Demonstration Flow

1. Train the model with the provided dataset or your own CSV file.
2. Start the Flask application.
3. Submit a realistic job description in the UI.
4. Show the prediction result and confidence score.
5. Open the dashboard to review stored predictions and fraud statistics.

## Academic Notes

- The code is modular to support discussion of preprocessing, feature extraction, model training, and deployment.
- The design system uses consistent colors, spacing, cards, and tables for a professional presentation.
- The repository documentation should be updated whenever the project scope or implementation changes.
# Recruitment Fraud Detection in Online Job Portals

An end-to-end graduation project that detects fraudulent online job postings using Natural Language Processing (NLP), Machine Learning (ML), and a Flask web application with a modern dashboard.

## Project Overview

Online job portals are vulnerable to scams that imitate legitimate vacancies. This project classifies job descriptions as **Fraudulent** or **Legitimate** using a reproducible NLP pipeline and exposes the prediction workflow through a professional web application for users and administrators.

## Objectives

- Build an NLP-powered classification pipeline for job post fraud detection.
- Compare multiple ML models and automatically select the best one using **F1-score**.
- Provide a responsive web interface for inference and an admin dashboard for monitoring.
- Persist prediction history and analytics in SQLite.
- Keep the code modular, readable, and easy to demonstrate during a graduation presentation.

## System Architecture

1. **Input Layer**
   - User enters a job description in the Flask web application.
2. **Preprocessing Layer**
   - Lowercasing
   - Punctuation removal
   - Number removal
   - Whitespace normalization
3. **Feature Engineering**
   - TF-IDF vectorization with unigram and bigram features.
4. **Model Selection**
   - Logistic Regression
   - Multinomial Naive Bayes
   - Support Vector Machine
   - Random Forest
5. **Inference & Storage**
   - Best model predicts label and confidence.
   - Prediction is stored in SQLite.
6. **Dashboard**
   - Displays totals, fraud rate, recent predictions, and chart data.

## Technologies Used

- **Backend:** Python, Flask
- **Machine Learning:** scikit-learn, pandas, numpy, joblib
- **Database:** SQLite
- **Frontend:** HTML, Tailwind CSS, JavaScript, Chart.js

## Project Structure

```text
project/
├── app.py
├── requirements.txt
├── README.md
├── AGENT.md
├── data/
├── models/
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── predictor.py
│   └── database.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── app.js
```

## Dataset Format

Place your CSV dataset inside the `data/` directory. The training script supports flexible column names, but the dataset should contain:

- A text column such as `description`, `job_description`, `text`, `job_text`, or `content`
- A target column such as `fraudulent`, `is_fraud`, `label`, `target`, or `class`

Example:

```csv
description,fraudulent
"Earn money quickly from home with no experience required",1
"We are hiring a software engineer with Python and SQL skills",0
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Train the Model

Run the training pipeline with your dataset:

```bash
python -m src.train_model --data data/sample_job_postings.csv
```

Generated artifacts:

- `models/fraud_detector.joblib`
- `models/tfidf_vectorizer.joblib`
- `models/model_metrics.json`
- `models/model_metadata.json`

The script evaluates all configured models and automatically saves the best-performing one based on **F1-score**.

## How to Run the Web Application

After training, start the Flask app:

```bash
python app.py
```

Then open:

- User Interface: `http://127.0.0.1:5000/`
- Admin Dashboard: `http://127.0.0.1:5000/dashboard`

## Features Included

- Fraud prediction from raw job description text
- Confidence score display
- Loading state in the user interface
- SQLite logging of all predictions
- Dashboard cards for totals and fraud rate
- Recent predictions table
- Doughnut chart for fraud vs legitimate predictions
- Clean modern design system with responsive layouts

## Evaluation Metrics

Each model is evaluated using:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

The **F1-score** is used as the primary selection metric because fraud detection is sensitive to class imbalance.

## Presentation Notes

For demonstration to examiners:

- Prepare a trained model artifact before the presentation.
- Show both a legitimate and a fraudulent sample prediction.
- Open the dashboard to explain live analytics and logging.
- Use the metrics JSON file to discuss model comparison and selection.

## Screenshots

- Home Page: add screenshot here
- Prediction Result: add screenshot here
- Dashboard: add screenshot here

## Future Improvements

- Add user authentication for the admin dashboard
- Support batch CSV prediction uploads
- Add explainability using SHAP or feature importance reports
- Deploy using Gunicorn and Nginx

## License

This project is intended for educational and academic use.
