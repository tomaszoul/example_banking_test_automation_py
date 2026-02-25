"""
Centralized configuration for test report paths, naming, and retention.

Every reporting module imports report_config from here so that run IDs,
directory layout, and retention settings live in one place.

Environment variables:
| Variable               | Default | Description                          |
|------------------------|---------|--------------------------------------|
| PW_RUN_ID              | (auto)  | Override the timestamped run ID      |
| PW_REPORT_AUTO_OPEN    | false   | Open HTML report in browser after run|
| PW_REPORT_KEEP_COUNT   | 3       | Max report directories to retain   |
| PW_REPORT_PORTAL       | false   | Post results to Report Portal (requires RP_ENDPOINT, RP_PROJECT, RP_API_KEY) |
"""
import os
from datetime import datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_ROOT = _REPO_ROOT / "test-reports"

def build_run_id() -> str:
    """
    Build timestamp-based run ID (e.g. 20260225-143012).
    Reuses PW_RUN_ID when already set so config and runner share the same identifier.
    """
    if os.environ.get("PW_RUN_ID"):
        return os.environ["PW_RUN_ID"]
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    os.environ["PW_RUN_ID"] = run_id
    return run_id


def report_dir(run_id: str | None = None) -> Path:
    """Return the directory path for a specific run's report."""
    rid = run_id or build_run_id()
    return REPORTS_ROOT / rid


def report_html_path(run_id: str | None = None) -> Path:
    """Return the path to the HTML report file for a run."""
    return report_dir(run_id) / "report.html"


AUTO_OPEN = os.environ.get("PW_REPORT_AUTO_OPEN", "").lower() == "true"
KEEP_COUNT = max(1, int(os.environ.get("PW_REPORT_KEEP_COUNT", "3") or "3"))
REPORT_PORTAL = os.environ.get("PW_REPORT_PORTAL", "").lower() == "true"
