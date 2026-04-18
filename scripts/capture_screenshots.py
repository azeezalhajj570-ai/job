from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT / "docs" / "screenshots"
BASE_URL = os.environ.get("SCREENSHOT_BASE_URL", "http://127.0.0.1:5003")


def ensure_dir() -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def save(page, name: str) -> None:
    page.screenshot(path=str(SCREENSHOTS_DIR / name), full_page=True)


def main() -> None:
    ensure_dir()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1600}, device_scale_factor=1)
        page = context.new_page()

        page.goto(f"{BASE_URL}/signin", wait_until="networkidle")
        save(page, "01_signin.png")

        page.fill("#email", "user")
        page.fill("#password", "user")
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/overview")
        page.wait_for_load_state("networkidle")
        save(page, "02_overview.png")

        page.goto(f"{BASE_URL}/predict", wait_until="networkidle")
        page.fill(
            "#job_text",
            "Urgent remote opportunity. Earn thousands weekly with no interview. Submit your passport copy and onboarding fee today to secure your slot.",
        )
        page.click("#submit-button")
        page.wait_for_load_state("networkidle")
        save(page, "03_predict_result.png")

        page.goto(f"{BASE_URL}/signals", wait_until="networkidle")
        save(page, "04_signals.png")

        page.goto(f"{BASE_URL}/logout", wait_until="networkidle")
        page.fill("#email", "admin")
        page.fill("#password", "admin")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
        save(page, "05_dashboard.png")

        context.close()
        browser.close()
    print(f"Wrote screenshots to {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    main()
