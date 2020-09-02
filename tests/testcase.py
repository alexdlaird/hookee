import time
import unittest

from hookee.manager import Manager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


class ManagedTestCase(unittest.TestCase):
    port = 5000
    manager = None
    webhook_url = None

    @classmethod
    def setUpClass(cls):
        cls.manager = Manager({})

        cls.manager.start()

        cls.webhook_url = "{}/webhook".format(cls.manager.tunnel.public_url)

    @classmethod
    def tearDownClass(cls):
        if cls.manager:
            cls.manager.stop()

            time.sleep(2)
