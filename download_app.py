#!/usr/bin/env python3
"""Optional: Download the XYZ Banking app from live site to banking-app/ for local testing."""
import re
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BANKING_APP_DIR = REPO_ROOT / "banking-app"
SOURCE_URL = "https://www.globalsqa.com/angularJs-protractor/BankingProject/"
BASE = SOURCE_URL.rstrip("/") + "/"

# Angular templateUrl files - needed for --local (templates resolve to page origin)
TEMPLATES = [
    "main.html",
    "options.html",
    "managerView.html",
    "newCustomer.html",
    "openAccount.html",
    "customerList.html",
    "customerView.html",
    "account.html",
    "depositTx.html",
    "withdrawlTx.html",
    "listTx.html",
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def main():
    BANKING_APP_DIR.mkdir(parents=True, exist_ok=True)

    # If templates are present, only refresh index.html (optional full refresh)
    has_templates = (BANKING_APP_DIR / "customerView.html").exists()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return

    print("Fetching app from", SOURCE_URL, "...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(SOURCE_URL, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()

    def absol(src: str) -> str:
        if src.startswith(("http", "//", "data:", "blob:")):
            return src
        return BASE + src.lstrip("/")

    html = re.sub(r'src="([^"]+)"', lambda m: f'src="{absol(m.group(1))}"', html)
    html = re.sub(
        r'href="([^"]+)"',
        lambda m: m.group(0)
        if m.group(1).startswith("#") or m.group(1).startswith(("http", "//", "data:"))
        else f'href="{absol(m.group(1))}"',
        html,
    )
    (BANKING_APP_DIR / "index.html").write_text(html, encoding="utf-8")
    print("Saved index.html")

    if has_templates:
        print("Templates already present. Delete customerView.html to re-download.")
    else:
        print("Fetching Angular templates...")
        for name in TEMPLATES:
            try:
                content = fetch(BASE + name)
                (BANKING_APP_DIR / name).write_text(content, encoding="utf-8")
                print(f"  {name}")
            except Exception as e:
                print(f"  {name} FAILED: {e}")

    print("Done. Run: python run_tests.py --local")


if __name__ == "__main__":
    main()
