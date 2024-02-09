import os
import unittest

import requests

from hookee import util
from tests.managedtestcase import ManagedTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.0.0"


@unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
class TestHookeeManager(ManagedTestCase):
    def test_http_get_query_params(self):
        # GIVEN
        params = {"param_1": ["param_value_1"]}

        # WHEN
        with self.captured_output() as (out, err):
            response = requests.get(self.webhook_url, params=params)

        self.assertEqual(response.status_code, 200)
        self.assertIn("""Query Params: {
    "param_1": "param_value_1"
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
        self.assertIn("""Body: {
    "form_data_1": "form_data_value_1"
}""", out.getvalue())
        self.assertEqual(response.json(), data)

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
