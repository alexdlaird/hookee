import sys
import time
from contextlib import contextmanager
from io import StringIO

from hookee import HookeeManager
from hookee.conf import Config
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2022, Alex Laird"
__version__ = "2.1.0"


class ManagedTestCase(HookeeTestCase):
    port = 8000
    hookee_manager = None
    webhook_url = None

    def setUp(self):
        super(ManagedTestCase, self).setUp()

        self.webhook_url = "{}/webhook".format(self.hookee_manager.tunnel.public_url)

    @classmethod
    def setUpClass(cls):
        cls.config = Config(click_logging=True)
        cls.hookee_manager = HookeeManager(config=cls.config)

        cls.hookee_manager._init_server_and_tunnel()

    @classmethod
    def tearDownClass(cls):
        if cls.hookee_manager:
            cls.hookee_manager.stop()

            time.sleep(2)

    @contextmanager
    def captured_output(self):
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err
