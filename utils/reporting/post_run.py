"""
Post-run script responsibilities:

1. Locate the most recent HTML report on disk.
2. Optionally open it in the default browser when --open is passed
   or PW_REPORT_AUTO_OPEN=true is set.
3. Find trace.zip files for Playwright Trace Viewer (failed or all).

Failures here are intentionally non-fatal (caller swallows errors).
"""
import html
import json
import re
import socket
import subprocess
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread

from .report_config import AUTO_OPEN, REPORTS_ROOT


def find_latest_report() -> str | None:
    """
    Scan the reports root for the newest directory containing report.html.
    Directories are sorted lexicographically (newest first, names encode timestamps).
    """
    if not REPORTS_ROOT.exists():
        return None
    dirs = sorted(
        [d.name for d in REPORTS_ROOT.iterdir() if d.is_dir()],
        reverse=True,
    )
    for name in dirs:
        html_path = REPORTS_ROOT / name / "report.html"
        if html_path.exists():
            return str(html_path.resolve())
    return None


def open_in_browser(file_path: str) -> None:
    """Open a file in the platform's default browser."""
    try:
        webbrowser.open(Path(file_path).as_uri())
    except Exception:
        print(f"Could not auto-open browser. Open manually:\n  {file_path}")


def _display_path(path: Path) -> str:
    """
    Return a portable path for display (relative to repo, forward slashes).
    Avoids leaking platform-specific absolute paths when sharing output.
    """
    try:
        rel = path.resolve().relative_to(REPORTS_ROOT.parent)
        return rel.as_posix()
    except ValueError:
        return str(path)


def _find_latest_run_dir() -> Path | None:
    """Return the most recent report run directory (newest timestamp)."""
    report_path = find_latest_report()
    if not report_path:
        return None
    return Path(report_path).parent


def _test_id_to_artifact_slug(test_id: str) -> str:
    """
    Normalize pytest test ID to match artifact folder naming.
    e.g. src/banking/specs/test_x.py::test_y[param] -> src-banking-specs-test-x-py-test-y
    """
    # Remove [param] for matching; param order can vary (chromium-bank_user0 vs bank_user0-chromium)
    base = re.sub(r"\[.*\]", "", test_id)
    base = base.replace("/", "-").replace("::", "-").replace("_", "-").replace(".py", "-py")
    return base.lower()


def _artifact_folder_matches_test(artifact_name: str, test_id: str) -> bool:
    """Check if an artifact folder name corresponds to a test ID."""
    slug = _test_id_to_artifact_slug(test_id)
    # Artifact: src-banking-specs-test-failing-deposit-py-test-this-test-will-fail-chromium-bank-user0
    # Slug:    src-banking-specs-test-failing-deposit-py-test-this-test-will-fail
    an = artifact_name.lower()
    return slug in an or an.startswith(slug.rstrip("-"))


def _get_failed_test_ids(report_html_path: Path) -> list[str]:
    """Parse pytest-html report and return test IDs that failed."""
    try:
        text = report_html_path.read_text(encoding="utf-8")
        match = re.search(r'data-jsonblob="([^"]+)"', text)
        if not match:
            return []
        blob = html.unescape(match.group(1))
        data = json.loads(blob)
        failed = []
        for test_id, runs in data.get("tests", {}).items():
            for run in runs if isinstance(runs, list) else [runs]:
                if run.get("result") in ("Failed", "Error"):
                    failed.append(test_id)
                    break
        return failed
    except Exception:
        return []


def find_latest_trace() -> Path | None:
    """
    Find the most recently modified trace.zip under test-reports.
    Returns None if no trace found.
    """
    if not REPORTS_ROOT.exists():
        return None
    traces = list(REPORTS_ROOT.rglob("trace.zip"))
    if not traces:
        return None
    return max(traces, key=lambda p: p.stat().st_mtime)


def find_all_traces(run_dir: Path | None = None) -> list[Path]:
    """Return all trace.zip paths from the given or latest run."""
    rdir = run_dir or _find_latest_run_dir()
    if not rdir or not rdir.exists():
        return []
    traces = list(rdir.rglob("trace.zip"))
    return sorted(traces, key=lambda p: p.stat().st_mtime, reverse=True)


def find_failed_traces(run_dir: Path | None = None, report_path: str | Path | None = None) -> list[Path]:
    """Return trace.zip paths for tests that failed in the report."""
    rdir = run_dir or _find_latest_run_dir()
    if not rdir or not rdir.exists():
        return []
    report = report_path or (rdir / "report.html")
    if not Path(report).exists():
        return []
    failed_ids = _get_failed_test_ids(Path(report))
    if not failed_ids:
        return []
    all_traces = find_all_traces(rdir)
    result = []
    for trace in all_traces:
        # Trace path: run_dir/artifacts/artifact_folder/trace.zip
        artifact_folder = trace.parent.name
        for tid in failed_ids:
            if _artifact_folder_matches_test(artifact_folder, tid):
                result.append(trace)
                break
    return result


def _find_free_port() -> int:
    """Bind to port 0 to get an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve_traces_and_open_urls(
    trace_paths: list[Path], run_dir: Path
) -> bool:
    """
    Serve trace.zip files from run_dir via local HTTP server and open each
    in trace.playwright.dev/?trace=... in new tabs.
    trace_paths must be under run_dir (e.g. run_dir/artifacts/<artifact-dir>/trace.zip).
    """
    if not trace_paths:
        return False
    for p in trace_paths:
        if not p.resolve().exists():
            return False
    run_dir = run_dir.resolve()

    class TraceHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(run_dir), **kwargs)

        def do_OPTIONS(self):
            self.send_response(204)
            self.end_headers()

        def _send_cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Max-Age", "86400")

        def end_headers(self):
            self._send_cors_headers()
            super().end_headers()

    port = _find_free_port()
    server = HTTPServer(("127.0.0.1", port), TraceHandler)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)  # Allow server to be ready before browser fetches

    base = f"http://127.0.0.1:{port}"
    for trace in trace_paths:
        try:
            rel = trace.resolve().relative_to(run_dir)
            trace_url = f"{base}/{rel.as_posix()}"
            viewer_url = f"https://trace.playwright.dev/?trace={trace_url}"
            webbrowser.open(viewer_url)
        except ValueError:
            continue
    print(
        f"Opened {len(trace_paths)} trace(s) in trace.playwright.dev (served via local HTTP)."
    )
    try:
        input("Press Enter to close... ")
    except EOFError:
        pass
    server.shutdown()
    return True


def open_trace(
    scope: str = "failed",
    local_viewer: bool = True,
    online_viewer: bool = True,
    auto_upload: bool = True,
) -> None:
    """
    Open trace.zip file(s) in Playwright Trace Viewer.

    scope: "failed" | "all"
        - failed: traces from tests that failed (requires report.html)
        - all: all traces from the latest run
    When auto_upload=True, serves traces via a local HTTP server and opens
    each in trace.playwright.dev/?trace=... in new tabs.
    Optionally runs `playwright show-trace` for the local viewer (first trace only).
    """
    run_dir = _find_latest_run_dir()
    if not run_dir:
        print("No report directory found. Run tests first.")
        return

    if scope == "failed":
        traces = find_failed_traces(run_dir=run_dir)
        if not traces:
            print("No failed traces found. (Use --open-trace-all to capture all traces.)")
            return
    else:  # all
        traces = find_all_traces(run_dir=run_dir)
        if not traces:
            print("No trace.zip found. Run tests with --open-trace-all to capture traces.")
            return

    label = {"failed": "Failed trace(s)", "all": "All traces"}.get(scope, scope)
    print(f"{label}:")
    for t in traces:
        try:
            rel = t.resolve().relative_to(REPORTS_ROOT.parent)
            print(f"  {rel.as_posix()}")
        except ValueError:
            print(f"  {t}")

    if online_viewer:
        if auto_upload and _serve_traces_and_open_urls(traces, run_dir):
            pass  # Browser launched with trace(s) loaded via ?trace= URL
        else:
            webbrowser.open("https://trace.playwright.dev/")
            print("Opened trace.playwright.dev — drag trace.zip files onto the page to view.")

    if local_viewer and traces:
        first = traces[0].resolve()
        try:
            subprocess.run(
                ["playwright", "show-trace", str(first)],
                check=False,
                timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            try:
                display = first.relative_to(REPORTS_ROOT.parent).as_posix()
            except ValueError:
                display = str(first)
            print(f"Local viewer failed. Use: playwright show-trace {display}")


def run(should_open: bool = False) -> None:
    """
    Locate the latest report and optionally open it.
    should_open: True if --open was passed or PW_REPORT_AUTO_OPEN=true
    """
    latest = find_latest_report()
    if not latest:
        print("No HTML report found.")
        return

    path = Path(latest).resolve()
    display = _display_path(path)
    open_now = should_open or AUTO_OPEN

    if open_now:
        print(f"Opening report in browser: {display}")
        open_in_browser(latest)
    else:
        print(
            f"HTML report ready:\n  {display}\n\n"
            "To open automatically after each run, set PW_REPORT_AUTO_OPEN=true\n"
            "or use: python run_tests.py --open"
        )
