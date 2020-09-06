import time

import requests

from hookee import util
from tests.managedtestcase import ManagedTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"


class TestCliManager(ManagedTestCase):
    def test_cli_manager(self):
        # GIVEN / WHEN
        # The test setup started the manager for us, so just assert the assumed state
        self.assertIsNotNone(self.cli_manager.server._thread)
        self.assertIsNotNone(self.cli_manager.tunnel._thread)

        # THEN
        self.cli_manager.stop()

        # Wait for things to tear down
        time.sleep(2)

        self.assertIsNone(self.cli_manager.server._thread)
        self.assertIsNone(self.cli_manager.tunnel._thread)

        # Restart the manager for the next tests
        self.cli_manager._init_server_and_tunnel()

    def test_http_get_query_params(self):
        # GIVEN
        params = {"param_1": ["param_value_1"]}

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.get(self.webhook_url, params=params)

        self.assertEqual(response.status_code, 200)
        if util.is_python_3():
            self.assertIn("""Query Params: {
    "param_1": "param_value_1"
}""", out.getvalue())
        else:
            self.assertIn("""Query Params: {
    "param_1": [
        "param_value_1"
    ]
}""", out.getvalue())

    def test_http_post_form_data(self):
        # GIVEN
        data = {"form_data_1": "form_data_value_1"}

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("\"Content-Type\": \"application/x-www-form-urlencoded\"", out.getvalue())
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        if util.is_python_36_or_higher():
            self.assertIn("""Body: {
    "form_data_1": "form_data_value_1"
}""", out.getvalue())
            self.assertEqual(response.json(), data)
        else:
            self.assertIn("""Body: {
    "form_data_1": [
        "form_data_value_1"
    ]
}""", out.getvalue())
            self.assertEqual(response.content, "{\"form_data_1\": [\"form_data_value_1\"]}")

    def test_http_post_json_data(self):
        # GIVEN
        headers = {"Content-Type": "application/json"}
        data = {"json_data_1": "json_data_value_1"}

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.post(self.webhook_url, headers=headers, json=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("\"Content-Type\": \"application/json\"", out.getvalue())
        self.assertIn("""Body: {
    "json_data_1": "json_data_value_1"
}""", out.getvalue())
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
        self.assertEqual(response.json(), data)
