import time

import requests

from hookee.climanager import CliManager
from tests.managedtestcase import ManagedTestCase
from tests.testcase import Context, HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.11"


class TestCliManager(HookeeTestCase):
    def test_cli_manager(self):
        # GIVEN
        cli_manager = CliManager(self.ctx)
        cli_manager._init_server_and_tunnel()

        self.assertIsNotNone(cli_manager.server._thread)
        self.assertIsNotNone(cli_manager.tunnel._thread)

        # WHEN
        cli_manager.stop()

        # Wait for things to tear down
        time.sleep(2)

        # THEN
        self.assertIsNone(cli_manager.server._thread)
        self.assertIsNone(cli_manager.tunnel._thread)

    def test_custom_response(self):
        # GIVEN
        response_body = "<Response>Ok</Response>"
        cli_manager = CliManager(Context({"response": response_body}))
        cli_manager._init_server_and_tunnel()

        webhook_url = "{}/webhook".format(cli_manager.tunnel.public_url)

        # WHEN
        response = requests.get(webhook_url)

        # THEN
        self.assertEqual(response.content.decode("utf-8"), response_body)

        # WHEN
        cli_manager.stop()

        # Wait for things to tear down
        time.sleep(2)
