import time
import unittest

from hookee.climanager import CliManager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"


class Context:
    obj = {}


class ManagedTestCase(unittest.TestCase):
    port = 5000
    cli_manager = None
    webhook_url = None

    @classmethod
    def setUpClass(cls):
        cls.cli_manager = CliManager(Context())

        cls.cli_manager.server.start()
        cls.cli_manager.tunnel.start()
        cls.cli_manager.alive = True

        cls.webhook_url = "{}/webhook".format(cls.cli_manager.tunnel.public_url)

    @classmethod
    def tearDownClass(cls):
        if cls.cli_manager:
            cls.cli_manager.stop()

            time.sleep(2)
