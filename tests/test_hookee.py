import unittest

from hookee import tunnel

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"


class TestHookee(unittest.TestCase):

    def test_tunnel(self):
        # WHEN
        tunnel.start_tunnel(5000)

        # THEN
        # TODO: We'll come back to this after the POC
        pass
