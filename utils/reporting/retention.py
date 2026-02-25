"""
Report retention policy — prevents unbounded disk growth from HTML reports.

Each test run produces a timestamped directory under test-reports/.
prune_reports removes the oldest directories so that at most keep_count remain.
"""
import shutil
from pathlib import Path

from .report_config import REPORTS_ROOT, KEEP_COUNT


def prune_reports(keep_count: int = KEEP_COUNT) -> list[str]:
    """
    Remove oldest report directories so that at most keep_count remain.
    Directories are sorted by name (which encodes date-time), newest first.

    Returns:
        Names of the directories that were removed.
    """
    if not REPORTS_ROOT.exists():
        return []

    dirs = sorted(
        [d.name for d in REPORTS_ROOT.iterdir() if d.is_dir()],
        reverse=True,
    )
    removed: list[str] = []
    for name in dirs[keep_count:]:
        path = REPORTS_ROOT / name
        try:
            shutil.rmtree(path, ignore_errors=True)
            removed.append(name)
        except OSError:
            pass
    return removed
