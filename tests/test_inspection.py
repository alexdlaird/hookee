import requests

from tests.testcase import ManagedTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


class TestInspection(ManagedTestCase):

    def test_http_get_query_params(self):
        # GIVEN
        params = {"param_1": "param_value_1"}

        # WHEN
        requests.get(self.webhook_url, params=params)

        # TODO: finish out test assertions

    def test_http_post_form_data(self):
        # GIVEN
        data = {"form_data_1": "form_data_value_1"}

        # WHEN
        requests.post(self.webhook_url, data=data)

        # TODO: finish out test assertions

    def test_http_post_json_data(self):
        # GIVEN
        headers = {"Content-Type": "application/json"}
        data = {"json_data_1": "json_data_value_1"}

        # WHEN
        requests.post(self.webhook_url, headers=headers, json=data)

        # TODO: finish out test assertions
