"""Report generation, retention, and post-run hooks (mirrors TS e2e-tests/utils/reporting)."""
from .report_config import (
    AUTO_OPEN,
    KEEP_COUNT,
    REPORTS_ROOT,
    build_run_id,
    report_dir,
    report_html_path,
)
from .retention import prune_reports
from .post_run import find_latest_report, find_latest_trace, open_trace, run as post_run

__all__ = [
    "AUTO_OPEN",
    "KEEP_COUNT",
    "REPORTS_ROOT",
    "build_run_id",
    "report_dir",
    "report_html_path",
    "prune_reports",
    "find_latest_report",
    "find_latest_trace",
    "open_trace",
    "post_run",
]
