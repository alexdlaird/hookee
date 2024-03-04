__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import sys
from contextlib import contextmanager
from io import StringIO

from hookee import HookeeManager
from hookee.conf import Config
from tests.testcase import HookeeTestCase


class ManagedTestCase(HookeeTestCase):
    hookee_manager = None
    webhook_url = None

    def setUp(self):
        super(ManagedTestCase, self).setUp()

        self.webhook_url = f"{self.hookee_manager.tunnel.public_url}/webhook"

    @classmethod
    def setUpClass(cls):
        cls.config = Config(click_logging=True, port=8000)
        cls.hookee_manager = HookeeManager(config=cls.config)

        cls.hookee_manager._init_server_and_tunnel()

    @contextmanager
    def captured_output(self):
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err
