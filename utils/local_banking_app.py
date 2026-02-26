"""
Local XYZ Banking app: prepare, serve, and health-check.

Inspired by Playwright's webServer flow: one place that ensures the app is
built/prepared, brings it up, and waits until it is healthy before tests run.
Used by run_tests.py for both pytest and playwright-ui when --local is set.
"""
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path


LOCAL_PORT = 8081
LOCAL_BASE_URL = f"http://127.0.0.1:{LOCAL_PORT}"
LOCAL_LOGIN_URL = f"{LOCAL_BASE_URL}/#/login"

# Minimal content that indicates the Angular app is served (not just 200 empty)
HEALTHY_INDICATORS = ("XYZ Bank", "ng-app", "Customer Login", "angular")


def ensure_app_present(repo_root: Path) -> Path:
    """
    Ensure banking-app dir exists with index.html and key templates.
    Exits with a clear message if not (user must run download_app.py first).
    """
    app_dir = repo_root / "banking-app"
    if not (app_dir / "index.html").exists():
        print("WARNING: banking-app/index.html not found. Run: python download_app.py")
        sys.exit(1)
    if not (app_dir / "customerView.html").exists():
        print("WARNING: Angular templates missing. Run: python download_app.py")
        sys.exit(1)
    return app_dir


def _serve(app_dir: Path, port: int) -> None:
    """Run http.server in process (for use in daemon thread)."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    proc.wait()


def start_local_server(app_dir: Path, port: int = LOCAL_PORT) -> threading.Thread:
    """Start static server in a daemon thread. Returns the thread (already started)."""
    thread = threading.Thread(target=_serve, args=(app_dir, port), daemon=True)
    thread.start()
    return thread


def wait_until_healthy(
    base_url: str = LOCAL_BASE_URL,
    timeout_seconds: float = 30.0,
    poll_interval: float = 0.5,
) -> None:
    """
    Poll base_url until response is 200 and body contains a healthy indicator.
    Raises TimeoutError if not healthy within timeout_seconds.
    """
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status != 200:
                    last_error = RuntimeError(f"HTTP {resp.status}")
                    time.sleep(poll_interval)
                    continue
                body = resp.read().decode("utf-8", errors="replace")
                if any(indicator in body for indicator in HEALTHY_INDICATORS):
                    return
                last_error = RuntimeError("Response did not contain app content")
        except Exception as e:
            last_error = e
        time.sleep(poll_interval)
    raise TimeoutError(
        f"Local app at {base_url} did not become healthy within {timeout_seconds}s"
    ) from last_error


def prepare_and_serve_local(
    repo_root: Path,
    port: int = LOCAL_PORT,
    healthy_timeout: float = 30.0,
) -> str:
    """
    Ensure banking-app is present, start server, wait until healthy.
    Returns base URL for tests (e.g. http://127.0.0.1:8081).
    Exits if app is not present; raises TimeoutError if not healthy in time.
    """
    app_dir = ensure_app_present(repo_root)
    base_url = f"http://127.0.0.1:{port}"
    start_local_server(app_dir, port=port)
    wait_until_healthy(base_url=base_url, timeout_seconds=healthy_timeout)
    return base_url
