"""Verify readiness probes without external network calls or submission side effects."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_readiness", ROOT / "scripts/check_readiness.py")
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class Handler(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        self.requests.append((self.command, self.path))
        status = int(self.path[1:]) if self.path[1:].isdigit() else 200
        body = b"<title>Just a moment</title>" if self.path == "/challenge" else b"x" * (readiness.READ_LIMIT + 100)
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_success_is_http_only_and_reads_at_most_64kb(self):
        result = readiness.probe_url("sample", self.base + "/200", 1)
        self.assertEqual(result["status"], "http_reachable")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["bytes_read"], readiness.READ_LIMIT)
        self.assertEqual(Handler.requests[-1], ("GET", "/200"))

    def test_restrictions_errors_and_challenges_are_not_success(self):
        for path, expected in [("403", "restricted"), ("418", "restricted"),
                               ("429", "restricted"), ("404", "http_error"),
                               ("503", "http_error"), ("challenge", "restricted")]:
            with self.subTest(path=path):
                self.assertEqual(readiness.probe_url("sample", self.base + "/" + path, 1)["status"], expected)

    def test_offline_report_never_networks_or_infers_manual_checks(self):
        with patch.object(readiness, "probe_url", side_effect=AssertionError("must not access network")):
            report = readiness.build_report(skip_network=True)
        self.assertEqual(len(report["network"]["literature_sites"]), 4)
        self.assertTrue(all(site["status"] == "skipped" for site in report["network"]["literature_sites"]))
        for item in [report["browser"], report["word"], *report["file_transfer"].values()]:
            self.assertEqual(item["status"], "pending_manual")
        self.assertEqual(report["network"]["official_website"]["status"], "pending_manual")
        self.assertEqual(report["overall_status"], "needs_attention")

    def test_online_report_checks_official_and_keeps_browser_unverified(self):
        with patch.object(readiness, "LITERATURE_SITES", (("local", self.base + "/200"),)):
            report = readiness.build_report(official_url=self.base + "/403", timeout=1)
        self.assertEqual(report["network"]["official_website"]["status"], "restricted")
        self.assertEqual(report["network"]["literature_sites"][0]["status"], "http_reachable")
        self.assertEqual(report["browser"]["status"], "pending_manual")

    def test_report_is_written_under_workspace_without_decision_log(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp) / "contest"
            path, report = readiness.check_readiness(workspace, skip_network=True)
            self.assertEqual(path, workspace.resolve() / "state/readiness/latest.json")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), report)
            self.assertFalse((workspace / "state/decision_log.json").exists())
            self.assertEqual(list(path.parent.glob(".readiness-*.tmp")), [])

    def test_repository_relations_and_invalid_inputs_are_rejected_before_probe(self):
        with patch.object(readiness, "build_report", side_effect=AssertionError("must reject before probing")):
            for workspace in [ROOT, ROOT / "contest", ROOT.parent]:
                with self.subTest(workspace=workspace), self.assertRaises(ValueError):
                    readiness.check_readiness(workspace)
        for url in ["file:///tmp/example", "https://user:secret@example.com", "https://bad site"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                readiness.build_report(official_url=url, skip_network=True)
        for timeout in [0, 16, float("nan"), float("inf")]:
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                readiness.build_report(timeout=timeout, skip_network=True)

    def test_cli_exit_zero_means_report_written_not_all_checks_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/check_readiness.py"),
                                   "--workspace", str(Path(temp) / "contest"), "--skip-network"],
                                  capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            output = json.loads(proc.stdout)
            self.assertEqual(output["overall_status"], "needs_attention")
            self.assertTrue(Path(output["report"]).is_file())


if __name__ == "__main__":
    unittest.main()
