import time
import sys
from contextlib import contextmanager

from click import Context

from hookee.cli import hookee as hookee_command
from hookee import HookeeManager, util
from tests.testcase import HookeeTestCase

if util.python3_gte():
    from io import StringIO
else:
    from io import BytesIO as StringIO

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.0"


class ManagedTestCase(HookeeTestCase):
    port = 5000
    hookee_manager = None
    webhook_url = None

    def setUp(self):
        super(ManagedTestCase, self).setUp()

        self.webhook_url = "{}/webhook".format(self.hookee_manager.tunnel.public_url)

    @classmethod
    def setUpClass(cls):
        cls.hookee_manager = HookeeManager()

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
