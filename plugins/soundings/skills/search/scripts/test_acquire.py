"""Acquisition boundaries, actual HTTP responses, and capture integration."""

from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest.mock import patch
from urllib.request import Request

import acquire
import evidence
import workspace
from evidence import EvidenceError


HTML = '<html><head><title>条件与结论</title><style>.x{color:red}</style></head><body><svg><title>图例</title></svg><h1>条件</h1><p>只在离线时成立。<sup>1</sup></p><table><tr><th>版本</th><th>限制</th></tr><tr><td>2</td><td>十条</td></tr></table><p id="note">1：包括例外。</p><script>ignore()</script></body></html>'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/html")
            self.end_headers()
            return
        self.send_response(200)
        mime, body = {
            "/html": ("text/html; charset=utf-8", HTML.encode()),
            "/text": ("text/plain; charset=utf-8", "短\n\n限定\r\n".encode()),
            "/latin": ("text/plain; charset=iso-8859-1", b"caf\xe9"),
            "/binary": ("application/pdf", b"%PDF-1.7"),
            "/invalid": ("text/plain; charset=utf-8", b"\xff"),
            "/empty": ("text/plain", b""),
            "/encoded": ("text/plain", b"fake gzip"),
        }.get(self.path, ("text/plain", b"not found"))
        self.send_header("Content-Type", mime)
        if self.path == "/encoded":
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        self.wfile.write(body)


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def fetch(self, path, **options):
        return acquire.fetch_text(self.url + path, allow_http=True,
                                  allow_private_network=True, **options)

    def test_html_keeps_raw_conditions_tables_and_declared_omissions(self):
        result = self.fetch("/html")
        self.assertEqual(result.raw_text, HTML)
        self.assertEqual(result.title, "条件与结论")
        self.assertIn("只在离线时成立。1", result.text)
        self.assertIn("版本\t限制", result.text)
        self.assertIn("1：包括例外。", result.text)
        self.assertNotIn("ignore()", result.text)
        self.assertEqual(result.omissions, ("script", "style"))

    def test_exact_decoded_text_and_redirect(self):
        self.assertEqual(self.fetch("/text").text, "短\n\n限定\r\n")
        self.assertEqual(self.fetch("/latin").text, "café")
        self.assertEqual(self.fetch("/redirect").url, self.url + "/html")

    def test_limits_invalid_encoding_empty_binary_and_encoded_are_errors(self):
        for path in ["/binary", "/invalid", "/empty", "/encoded"]:
            with self.subTest(path=path), self.assertRaises(EvidenceError):
                self.fetch(path)
        with self.assertRaisesRegex(EvidenceError, "exceeds"):
            self.fetch("/html", max_source_bytes=8)

    def test_no_implicit_private_or_insecure_destination(self):
        with self.assertRaisesRegex(EvidenceError, "HTTPS"):
            acquire.fetch_text(self.url + "/html")
        with self.assertRaisesRegex(EvidenceError, "non-public"):
            acquire.fetch_text(self.url + "/html", allow_http=True)
        for url in ["file:///etc/passwd", "https://user:password@example.com/a",
                    "https://example.com/a\nsecret", "https://example.com\\@localhost/"]:
            with self.subTest(url=url), self.assertRaises(EvidenceError):
                acquire.validate_url(url)
        for timeout in [0, -1, float("inf"), float("nan")]:
            with self.subTest(timeout=timeout), self.assertRaises(EvidenceError):
                acquire.fetch_text("https://example.com", timeout=timeout)

    def test_redirect_rechecks_destination(self):
        handler = acquire.CheckedRedirect()
        with self.assertRaisesRegex(EvidenceError, "non-public"):
            handler.redirect_request(Request("https://example.com"), None, 302, "Found", Message(),
                                     "https://127.0.0.1/secret")

    def test_bounded_receipt_before_capture_and_raw_extracted_link(self):
        captured = []

        def capture(root, path, source, title, representation, **kwargs):
            captured.append((path.read_bytes(), representation, kwargs))
            return {"ref": "s-" + str(len(captured)) * 32}

        stub = types.SimpleNamespace(load_state=lambda _: {}, capture_source=capture)
        with patch.dict("sys.modules", workspace=stub), patch.object(acquire, "fetch_text", return_value=self.fetch("/html")):
            with self.assertRaises(EvidenceError):
                acquire.acquire(Path("unused"), self.url, max_bytes=1)
            self.assertEqual(captured, [])
            result = acquire.acquire(Path("unused"), self.url, lead_id="l-test")
        self.assertEqual(captured[0][0], HTML.encode())
        self.assertEqual(captured[0][1], "verbatim")
        self.assertEqual(captured[1][1], "extracted")
        self.assertEqual(captured[1][2]["derived_from"], result["raw_ref"])
        self.assertEqual(captured[1][2]["lead_id"], "l-test")
        self.assertNotEqual(result["raw_ref"], result["ref"])

    def test_failed_second_capture_identifies_retained_raw_basis(self):
        calls = []

        def capture(*args, **kwargs):
            calls.append(1)
            if len(calls) == 2:
                raise EvidenceError("locked")
            return {"ref": "s-" + "a" * 32}

        stub = types.SimpleNamespace(load_state=lambda _: {}, capture_source=capture)
        with patch.dict("sys.modules", workspace=stub), patch.object(acquire, "fetch_text", return_value=self.fetch("/html")):
            with self.assertRaisesRegex(EvidenceError, "raw source retained as s-aaaa"):
                acquire.acquire(Path("unused"), self.url)

    def test_real_workspace_retains_raw_and_extracted_without_read_credit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "inquiry"
            workspace.init(root, "explanation", "which conditions?", "inspect source")
            lead = workspace.lead(root, locator=self.url + "/html", title="Conditions", why="decides result")["id"]
            result = acquire.acquire(root, self.url + "/html", lead_id=lead,
                                     allow_http=True, allow_private_network=True)
            raw = evidence.load(root / "evidence", result["raw_ref"])
            extracted = evidence.load(root / "evidence", result["ref"])
            self.assertEqual(raw["content"], HTML)
            self.assertEqual(raw["representation"], "verbatim")
            self.assertEqual(extracted["representation"], "extracted")
            state = workspace.load_state(root)
            self.assertEqual(state["sources"][result["ref"]]["derived_from"], result["raw_ref"])
            self.assertEqual(state["leads"][lead]["status"], "unread")
            self.assertTrue(all(not source["delivered"] for source in state["sources"].values()))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            with self.assertRaises(EvidenceError):
                acquire.acquire(root, self.url + "/html", max_bytes=1,
                                allow_http=True, allow_private_network=True)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
