# Screenshot Guide

Screenshots are captured from the running Flask application with Playwright and stored in `docs/screenshots/`.

Target pages:

- `01_signin.png`
- `02_overview.png`
- `03_predict_result.png`
- `04_signals.png`
- `05_dashboard.png`

Capture rules:

- Fixed desktop viewport for consistency
- Real authenticated flows using the repository demo accounts
- No mockups or manually composed UI images
- Dashboard captured only after a real prediction is stored
