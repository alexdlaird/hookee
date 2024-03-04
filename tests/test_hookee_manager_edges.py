__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import os
import unittest

import requests

from hookee import HookeeManager
from hookee.conf import Config
from tests.testcase import HookeeTestCase


class TestHookeeManagerEdges(HookeeTestCase):
    def test_not_click_logging(self):
        self.assertFalse(self.config.click_logging)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_hookee_manager(self):
        # GIVEN
        config = Config(port=8001)
        hookee_manager = HookeeManager(config=config)

        # THEN
        self.assertIsNone(hookee_manager.server._thread)
        self.assertIsNone(hookee_manager.tunnel._thread)

        # WHEN
        hookee_manager._init_server_and_tunnel()

        # THEN
        self.assertIsNotNone(hookee_manager.server._thread)
        self.assertIsNotNone(hookee_manager.tunnel._thread)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_custom_response(self):
        # GIVEN
        response_body = "<Response>Ok</Response>"
        config = Config(response=response_body, auth_token=os.environ["NGROK_AUTHTOKEN"], port=8002)
        hookee_manager = HookeeManager(config=config)
        hookee_manager._init_server_and_tunnel()

        webhook_url = f"{hookee_manager.tunnel.public_url}/webhook"

        # WHEN
        response = requests.get(webhook_url)

        # THEN
        self.assertEqual(response.content.decode("utf-8"), response_body)
