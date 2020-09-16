import time

import requests
from hookee import conf

from hookee.hookeemanager import HookeeManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.1.0"


class TestHookeeManagerEdges(HookeeTestCase):
    def test_hookee_manager(self):
        # GIVEN
        hookee_manager = HookeeManager(self.ctx)
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

    def test_custom_response(self):
        # GIVEN
        response_body = "<Response>Ok</Response>"
        hookee_manager = HookeeManager(conf.Context({"response": response_body}))
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
