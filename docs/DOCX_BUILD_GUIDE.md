# DOCX Build Guide

1. Install dependencies:
   `python -m pip install -r requirements.txt python-docx pillow playwright`
2. Train the model:
   `python -m src.train_model --data data/sample_job_postings.csv --model-dir models`
3. Capture screenshots with the app running:
   `env PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright python scripts/capture_screenshots.py`
4. Build the diagrams, markdown docs, and final report:
   `python scripts/build_submission_assets.py`

Output:

- `submission/Project_Report.docx`
- `docs/*.md`
- `docs/diagrams/*.png`
- `docs/diagrams/sources/*.mmd`
