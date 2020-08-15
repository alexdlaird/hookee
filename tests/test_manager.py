import time
import unittest

from hookee.manager import Manager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


class TestManager(unittest.TestCase):

    def test_manager(self):
        # GIVEN
        port = 5000
        manager = Manager.get_instance(port)

        # WHEN
        manager.start()

        # THEN
        self.assertIsNotNone(manager.server._thread)
        self.assertIsNotNone(manager.tunnel._thread)

        # THEN
        manager.stop()

        # Wait for things to tear down
        time.sleep(2)

        self.assertIsNone(manager.server._thread)
        self.assertIsNone(manager.tunnel._thread)
