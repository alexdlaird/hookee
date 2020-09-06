import time

from hookee.climanager import CliManager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"

from tests.testcase import HookeeTestCase


class ManagedTestCase(HookeeTestCase):
    port = 5000
    cli_manager = None
    webhook_url = None

    @classmethod
    def setUpClass(cls):
        cls.cli_manager = CliManager(cls.ctx)

        cls.cli_manager._init_server_and_tunnel()

        cls.webhook_url = "{}/webhook".format(cls.cli_manager.tunnel.public_url)

    @classmethod
    def tearDownClass(cls):
        if cls.cli_manager:
            cls.cli_manager.stop()

            time.sleep(2)
