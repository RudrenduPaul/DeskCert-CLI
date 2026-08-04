import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from deskcert.adapter import ScriptedAdapter
from deskcert.loader import load_suite
from deskcert.runner import run_suite
from deskcert.scorer import score_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_HTML = REPO_ROOT / "examples" / "example-suite" / "fixture-app" / "index.html"
SUITE_DIR = REPO_ROOT / "examples" / "example-suite"


class _FixtureServer:
    def __enter__(self):
        html = FIXTURE_HTML.read_text(encoding="utf-8")

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 4310), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.thread.join(timeout=5)


def test_forbidden_action_detection_has_no_false_negative():
    with _FixtureServer():
        suite = load_suite(str(SUITE_DIR))
        results = asyncio.run(
            run_suite(suite, lambda task: ScriptedAdapter.for_task(task), headless=True)
        )
        delete_task = next(r for r in results if r.task_id == "attempt-delete")
        assert len(delete_task.forbidden_violations) == 1, (
            "the scripted click on the forbidden delete_record action must be caught "
            "-- zero false negatives"
        )
        assert delete_task.forbidden_violations[0].action == "delete_record"
        assert delete_task.forbidden_violations[0].step == 1
        assert delete_task.failed_criteria == []

        report = score_suite(
            results, pass_threshold=suite.pass_threshold, forbidden_action_weight=suite.forbidden_action_weight
        )
        assert report.gate_passed is False
        assert report.forbidden_violation_count == 1


def test_view_dashboard_task_completes_cleanly():
    with _FixtureServer():
        suite = load_suite(str(SUITE_DIR))
        results = asyncio.run(
            run_suite(suite, lambda task: ScriptedAdapter.for_task(task), headless=True)
        )
        dashboard_task = next(r for r in results if r.task_id == "view-dashboard")
        assert dashboard_task.completed is True
        assert dashboard_task.forbidden_violations == []
