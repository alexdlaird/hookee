__copyright__ = "Copyright (c) 2020-2026 Alex Laird"
__license__ = "MIT"

import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock

import requests

from hookee import HookeeManager
from hookee.conf import Config
from hookee.exception import HookeeError
from tests.testcase import HookeeTestCase


class UpstreamHandler(BaseHTTPRequestHandler):
    received = []

    def do_GET(self):  # noqa: N802
        self.handle_request()

    def do_POST(self):  # noqa: N802
        self.handle_request()

    def handle_request(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        UpstreamHandler.received.append({"method": self.command, "path": self.path, "headers": dict(self.headers),
                                         "body": body})

        if self.path.startswith("/redirect"):
            self.send_response(302)
            self.send_header("Location", "/elsewhere")
            self.end_headers()
        elif self.path.startswith("/stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for i in range(3):
                self.wfile.write(f"data: event {i}\n\n".encode())
                self.wfile.flush()
                time.sleep(0.5)
        elif self.path.startswith("/error"):
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"upstream failed")
        else:
            body = b"<Response><Message>From the app</Message></Response>"
            self.send_response(201)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Upstream", "yes")
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass


def raise_error(request, response):
    raise RuntimeError("Error raised by the response callback")


class TestServer(HookeeTestCase):
    def setUp(self):
        super(TestServer, self).setUp()

        self.server = None
        self.port = 8010
        self.upstream_port = 8012
        self.webhook_url = f"http://127.0.0.1:{self.port}/webhook"

    def tearDown(self):
        if self.server:
            self.server.stop()

        super(TestServer, self).tearDown()

    def given_server(self, **options):
        self.hookee_manager = HookeeManager(config=Config(click_logging=True, port=self.port, **options))
        self.server = self.hookee_manager.server
        self.server.start()

    def given_upstream(self):
        UpstreamHandler.received = []
        upstream = HTTPServer(("127.0.0.1", self.upstream_port), UpstreamHandler)
        threading.Thread(target=upstream.serve_forever, daemon=True).start()
        self.addCleanup(upstream.server_close)
        self.addCleanup(upstream.shutdown)

        return f"http://127.0.0.1:{self.upstream_port}"

    def send_raw_request(self, request_target):
        with socket.create_connection(("127.0.0.1", self.port)) as connection:
            connection.sendall(f"GET {request_target} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                               .encode())
            response = b""
            while chunk := connection.recv(4096):
                response += chunk

        return response.split(b"\r\n")[0].decode()

    def given_file(self, name, contents):
        path = os.path.join(self.config_dir, name)
        with open(path, "wb") as f:
            f.write(contents)

        return path

    def test_shutdown_route_not_exposed(self):
        # GIVEN
        self.given_server()

        # WHEN
        response = requests.post(f"http://127.0.0.1:{self.port}/shutdown")

        # THEN
        self.assertEqual(response.status_code, 404)

    def test_stop_releases_port(self):
        # GIVEN
        self.given_server()

        # WHEN
        self.server.stop()

        # THEN
        self.assertIsNone(self.server._thread)
        with self.assertRaises(requests.exceptions.ConnectionError):
            requests.get(self.webhook_url)

    def test_unhandled_error_hides_traceback(self):
        # GIVEN
        self.given_server(response_callback=raise_error)

        # WHEN
        with self.captured_output():
            response = requests.post(self.webhook_url, json={})

        # THEN
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("Traceback", response.text)

    def test_binary_body_echoed(self):
        # GIVEN
        self.given_server()
        data = bytes(range(256))

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, data=data,
                                     headers={"Content-Type": "application/octet-stream"})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, data)
        self.assertIn("Body: <256 bytes of binary data>", out.getvalue())

    def test_multipart_upload(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, files={"file": ("hello.txt", b"hello", "text/plain")})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertIn("""Files: {
    "file": {
        "filename": "hello.txt",
        "content_type": "text/plain",
        "size": 5
    }
}""", out.getvalue())

    def test_json_array_body_echoed(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output():
            response = requests.post(self.webhook_url, json=[1, 2])

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [1, 2])

    def test_repeated_form_values_kept(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output():
            response = requests.post(self.webhook_url, data=[("a", "1"), ("a", "2"), ("b", "3")])

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"a": ["1", "2"], "b": "3"})

    def test_repeated_query_params_kept(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.get(self.webhook_url, params=[("a", "1"), ("a", "2"), ("b", "3")])

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertIn("""Query Params: {
    "a": [
        "1",
        "2"
    ],
    "b": "3"
}""", out.getvalue())

    def test_xml_request_body_formatted(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, data="<Request><From>+15005550006</From></Request>",
                                     headers={"Content-Type": "text/xml"})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertIn("Body Type: XML", out.getvalue())
        self.assertIn("""<Request>
\t<From>+15005550006</From>
</Request>""", out.getvalue())

    def test_status_code_and_headers_applied_to_echo(self):
        # GIVEN
        self.given_server(status_code=202, response_headers=["X-Test: one", "X-Other:two"])

        # WHEN
        with self.captured_output():
            response = requests.post(self.webhook_url, json={"a": 1})

        # THEN
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.headers["X-Test"], "one")
        self.assertEqual(response.headers["X-Other"], "two")
        self.assertEqual(response.json(), {"a": 1})

    def test_response_file_with_guessed_content_type(self):
        # GIVEN
        twiml = b"<Response><Message>Thanks!</Message></Response>"
        self.given_server(response_file=self.given_file("twiml.xml", twiml))

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, data={"Body": "hi"})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, twiml)
        self.assertIn(response.headers["Content-Type"], ["application/xml", "text/xml"])
        self.assertIn("""<Response>
\t<Message>Thanks!</Message>
</Response>""", out.getvalue())

    def test_delay(self):
        # GIVEN
        self.given_server(delay=0.5)

        # WHEN
        start = time.monotonic()
        with self.captured_output():
            response = requests.post(self.webhook_url, data={"a": "1"})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(time.monotonic() - start, 0.5)

    def test_response_and_response_file_fails(self):
        # GIVEN
        response_file = self.given_file("response.txt", b"Ok")

        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, response="Ok", response_file=response_file))

        # THEN
        self.assertIn("`--response` and `--response-file` cannot both be given", str(cm.exception))

    def test_forward_to_with_response_fails(self):
        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, forward_to="http://127.0.0.1:1", response="Ok"))

        # THEN
        self.assertIn("`--forward-to` cannot be combined with `--response`", str(cm.exception))

    def test_invalid_response_header_fails(self):
        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, response_headers=["no-separator"]))

        # THEN
        self.assertIn("must be given as \"Name: value\"", str(cm.exception))

    def test_save_dir_writes_request_and_response(self):
        # GIVEN
        save_dir = os.path.join(self.config_dir, "requests")
        self.given_server(save_dir=save_dir)

        # WHEN
        with self.captured_output():
            requests.post(f"{self.webhook_url}?a=1&a=2", data={"Body": "hi", "To": "+15005550006"},
                          headers={"Authorization": "Basic dXNlcjpzZWNyZXQ="})

        # THEN
        saved_files = os.listdir(save_dir)
        self.assertEqual(len(saved_files), 1)
        with open(os.path.join(save_dir, saved_files[0])) as f:
            saved = json.load(f)
        self.assertEqual(saved["request"]["method"], "POST")
        self.assertEqual(saved["request"]["path"], "/webhook")
        self.assertEqual(saved["request"]["query"], {"a": ["1", "2"]})
        self.assertEqual(saved["request"]["headers"]["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(saved["request"]["headers"]["Authorization"], "Basic <masked>")
        self.assertEqual(saved["request"]["body"], "Body=hi&To=%2B15005550006")
        self.assertEqual(saved["request"]["body_encoding"], "utf-8")
        self.assertEqual(saved["response"]["status_code"], 200)
        self.assertEqual(saved["response"]["headers"]["Content-Type"], "application/json")
        self.assertEqual(json.loads(saved["response"]["body"]), {"Body": "hi", "To": "+15005550006"})

    def test_save_dir_writes_binary_body_as_base64(self):
        # GIVEN
        save_dir = os.path.join(self.config_dir, "requests")
        self.given_server(save_dir=save_dir)

        # WHEN
        with self.captured_output():
            requests.post(self.webhook_url, data=b"\xff\xfe", headers={"Content-Type": "application/octet-stream"})

        # THEN
        with open(os.path.join(save_dir, os.listdir(save_dir)[0])) as f:
            saved = json.load(f)
        self.assertEqual(saved["request"]["body"], "//4=")
        self.assertEqual(saved["request"]["body_encoding"], "base64")
        self.assertEqual(saved["response"]["body"], "//4=")
        self.assertEqual(saved["response"]["body_encoding"], "base64")

    def test_sensitive_headers_masked(self):
        # GIVEN
        self.given_server(response_headers=["Set-Cookie: session=abc123"])

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, data={"a": "1"},
                                     headers={"Authorization": "Bearer my-token", "Cookie": "session=xyz789"})

        # THEN
        self.assertEqual(response.headers["Set-Cookie"], "session=abc123")
        self.assertIn("\"Authorization\": \"Bearer <masked>\"", out.getvalue())
        self.assertIn("\"Cookie\": \"<masked>\"", out.getvalue())
        self.assertIn("\"Set-Cookie\": \"<masked>\"", out.getvalue())
        self.assertNotIn("my-token", out.getvalue())
        self.assertNotIn("xyz789", out.getvalue())
        self.assertNotIn("abc123", out.getvalue())

    def test_sensitive_headers_shown_with_show_sensitive_headers(self):
        # GIVEN
        self.given_server(show_sensitive_headers=True)

        # WHEN
        with self.captured_output() as (out, err):
            requests.post(self.webhook_url, data={"a": "1"}, headers={"Authorization": "Bearer my-token"})

        # THEN
        self.assertIn("\"Authorization\": \"Bearer my-token\"", out.getvalue())

    def test_root_route(self):
        # GIVEN
        self.given_server(default_route="/$")

        # WHEN
        with self.captured_output():
            response = requests.post(f"http://127.0.0.1:{self.port}/", json={"a": 1})

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"a": 1})

    def test_response_route_limits_response_options(self):
        # GIVEN
        self.given_server(status_code=503, delay=0.5, response_route="^GET /webhook")

        # WHEN
        with self.captured_output():
            start = time.monotonic()
            post_response = requests.post(self.webhook_url, json={"a": 1})
            post_elapsed = time.monotonic() - start
            get_response = requests.get(self.webhook_url)

        # THEN
        self.assertEqual(post_response.status_code, 200)
        self.assertLess(post_elapsed, 0.5)
        self.assertEqual(get_response.status_code, 503)

    def test_response_route_limits_response_body(self):
        # GIVEN
        self.given_server(response="Ok", response_route="^GET ")

        # WHEN
        with self.captured_output():
            get_response = requests.get(self.webhook_url)
            post_response = requests.post(self.webhook_url, json={"a": 1})

        # THEN
        self.assertEqual(get_response.text, "Ok")
        self.assertEqual(post_response.json(), {"a": 1})

    def test_invalid_response_route_fails(self):
        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, status_code=503, response_route="("))

        # THEN
        self.assertIn("`--response-route` is not a valid regex", str(cm.exception))

    def test_forward_to_relays_request_and_response(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(f"http://127.0.0.1:{self.port}/sms?x=1",
                                     data={"Body": "hi", "To": "+15005550006"},
                                     headers={"X-Twilio-Signature": "abc", "Authorization": "Bearer my-token"})

        # THEN
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["X-Upstream"], "yes")
        self.assertEqual(response.text, "<Response><Message>From the app</Message></Response>")
        self.assertIn(f"Forwarded To: {upstream_url}/sms?x=1", out.getvalue())
        self.assertIn("<Message>From the app</Message>", out.getvalue())
        self.assertNotIn("<streamed", out.getvalue())
        received = UpstreamHandler.received[0]
        self.assertEqual(received["method"], "POST")
        self.assertEqual(received["path"], "/sms?x=1")
        self.assertEqual(received["body"], b"Body=hi&To=%2B15005550006")
        self.assertEqual(received["headers"]["X-Twilio-Signature"], "abc")
        self.assertEqual(received["headers"]["Authorization"], "Bearer my-token")
        self.assertEqual(received["headers"]["Host"], f"127.0.0.1:{self.port}")

    def test_forward_to_appends_path_to_base_path(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=f"{upstream_url}/api/")

        # WHEN
        with self.captured_output():
            requests.get(f"http://127.0.0.1:{self.port}/planner/events/?page=2")

        # THEN
        self.assertEqual(UpstreamHandler.received[0]["path"], "/api/planner/events/?page=2")

    def test_forward_to_keeps_encoded_path(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output():
            requests.get(f"http://127.0.0.1:{self.port}/files/a%20b/c%2Fd?name=%26")

        # THEN
        self.assertEqual(UpstreamHandler.received[0]["path"], "/files/a%20b/c%2Fd?name=%26")

    def test_forward_to_forwards_root(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output():
            response = requests.get(f"http://127.0.0.1:{self.port}/")

        # THEN
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UpstreamHandler.received[0]["path"], "/")

    def test_forward_to_streams_response(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output() as (out, err):
            start = time.monotonic()
            with requests.get(f"http://127.0.0.1:{self.port}/stream", stream=True) as response:
                lines = response.iter_lines()
                first_event = next(lines)
                first_event_elapsed = time.monotonic() - start
                remaining_events = [line for line in lines if line]

        # THEN
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_event, b"data: event 0")
        self.assertLess(first_event_elapsed, 0.5)
        self.assertEqual(remaining_events, [b"data: event 1", b"data: event 2"])
        self.assertIn("Body: <streamed, shown below as it arrives>", out.getvalue())
        self.assertIn("Streamed: data: event 2", out.getvalue())

    def test_save_dir_saves_streamed_response_when_finished(self):
        # GIVEN
        upstream_url = self.given_upstream()
        save_dir = os.path.join(self.config_dir, "requests")
        self.given_server(forward_to=upstream_url, save_dir=save_dir)

        # WHEN
        with self.captured_output():
            requests.get(f"http://127.0.0.1:{self.port}/stream")

        # THEN
        with open(os.path.join(save_dir, os.listdir(save_dir)[0])) as f:
            saved = json.load(f)
        self.assertEqual(saved["response"]["body"], "data: event 0\n\ndata: event 1\n\ndata: event 2\n\n")

    def test_forward_to_returns_upstream_error(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output():
            response = requests.post(f"http://127.0.0.1:{self.port}/error", data={"a": "1"})

        # THEN
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, "upstream failed")

    def test_forward_to_does_not_follow_redirect(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output():
            response = requests.post(f"http://127.0.0.1:{self.port}/redirect", data={"a": "1"},
                                     allow_redirects=False)

        # THEN
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/elsewhere")
        self.assertEqual(len(UpstreamHandler.received), 1)

    def test_forward_to_with_response_route_injects_faults(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url, status_code=503, response_route="^GET /planner/")

        # WHEN
        with self.captured_output():
            planner_response = requests.get(f"http://127.0.0.1:{self.port}/planner/events/")
            auth_response = requests.post(f"http://127.0.0.1:{self.port}/auth/token/", data={"a": "1"})

        # THEN
        self.assertEqual(planner_response.status_code, 503)
        self.assertEqual(auth_response.status_code, 201)
        self.assertEqual(len(UpstreamHandler.received), 2)

    def test_forward_to_unreachable_returns_502(self):
        # GIVEN
        self.given_server(forward_to=f"http://127.0.0.1:{self.upstream_port}")

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(f"http://127.0.0.1:{self.port}/sms", data={"a": "1"})

        # THEN
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.text, "Bad Gateway")
        self.assertIn(f"hookee could not forward the request to http://127.0.0.1:{self.upstream_port}/sms",
                      out.getvalue())

    def test_forward_to_rejects_request_target_with_userinfo(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output() as (out, err):
            status_line = self.send_raw_request("@example.com/x")

        # THEN
        self.assertEqual(status_line, "HTTP/1.1 400 BAD REQUEST")
        self.assertIn("hookee only forwards requests for a path", out.getvalue())
        self.assertEqual(len(UpstreamHandler.received), 0)

    def test_forward_to_rejects_absolute_request_target(self):
        # GIVEN
        upstream_url = self.given_upstream()
        self.given_server(forward_to=upstream_url)

        # WHEN
        with self.captured_output():
            status_line = self.send_raw_request("http://example.com/x")

        # THEN
        self.assertEqual(status_line, "HTTP/1.1 400 BAD REQUEST")
        self.assertEqual(len(UpstreamHandler.received), 0)

    def test_build_forward_url_keeps_forward_to_host(self):
        # GIVEN
        config = Config(port=self.port, forward_to="http://localhost:5000")
        plugin_manager = HookeeManager(config=config).plugin_manager
        request = mock.Mock(environ={"RAW_URI": "@evil.example.com/x"})

        # WHEN
        url = plugin_manager._build_forward_url(request)

        # THEN
        self.assertIsNone(url)

    def test_forward_to_itself_fails(self):
        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, forward_to=f"http://localhost:{self.port}"))

        # THEN
        self.assertIn(f"`--forward-to` cannot point at hookee itself, which is using port {self.port}",
                      str(cm.exception))

    def test_forward_to_with_credentials_fails(self):
        # WHEN
        with self.assertRaises(HookeeError) as cm:
            HookeeManager(config=Config(port=self.port, forward_to="http://user:secret@127.0.0.1:5000"))

        # THEN
        self.assertIn("`--forward-to` cannot include credentials in its URL", str(cm.exception))

    def test_forward_to_shown_in_registered_endpoints(self):
        # GIVEN
        self.given_server(forward_to="http://localhost:5000/")

        # WHEN
        with self.captured_output() as (out, err):
            self.hookee_manager.print_ready()

        # THEN
        self.assertIn(f" * http://localhost:{self.port}/ -> http://localhost:5000/ (all paths are forwarded)",
                      out.getvalue())

    def test_webhook_verified_shown_with_verify_webhook(self):
        # GIVEN
        self.given_server(verify_webhook="twilio:secret")

        # WHEN
        with self.captured_output() as (out, err):
            requests.post(self.webhook_url, data={"a": "1"}, headers={"X-Hookee-Webhook-Verified": "true"})

        # THEN
        self.assertIn("Webhook Verified: Yes", out.getvalue())
        self.assertNotIn("X-Hookee-Webhook-Verified", out.getvalue())

    def test_webhook_verified_not_shown_without_verify_webhook(self):
        # GIVEN
        self.given_server()

        # WHEN
        with self.captured_output() as (out, err):
            requests.post(self.webhook_url, data={"a": "1"}, headers={"X-Hookee-Webhook-Verified": "true"})

        # THEN
        self.assertNotIn("Webhook Verified", out.getvalue())
        self.assertIn("\"X-Hookee-Webhook-Verified\": \"true\"", out.getvalue())
