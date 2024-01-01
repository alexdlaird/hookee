import os
import time
import unittest

import requests
from hookee.conf import Config

from hookee import HookeeManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.0"


class TestHookeeManagerEdges(HookeeTestCase):
    def test_not_click_logging(self):
        self.assertFalse(self.config.click_logging)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_hookee_manager(self):
        # GIVEN
        hookee_manager = HookeeManager()
        hookee_manager._init_server_and_tunnel()

        self.assertIsNotNone(hookee_manager.server._thread)
        self.assertIsNotNone(hookee_manager.tunnel._thread)

        # WHEN
        hookee_manager.stop()

        # Wait for things to tear down
        time.sleep(2)

        # THEN
        self.assertIsNone(hookee_manager.server._thread)
        self.assertIsNone(hookee_manager.tunnel._thread)

    @unittest.skipIf(not os.environ.get("NGROK_AUTHTOKEN"), "NGROK_AUTHTOKEN environment variable not set")
    def test_custom_response(self):
        # GIVEN
        response_body = "<Response>Ok</Response>"
        config = Config(response=response_body, auth_token=os.environ["NGROK_AUTHTOKEN"])
        hookee_manager = HookeeManager(config=config)
        hookee_manager._init_server_and_tunnel()

        webhook_url = "{}/webhook".format(hookee_manager.tunnel.public_url)

        # WHEN
        response = requests.get(webhook_url)

        # THEN
        self.assertEqual(response.content.decode("utf-8"), response_body)

        # WHEN
        hookee_manager.stop()

        # Wait for things to tear down
        time.sleep(2)
