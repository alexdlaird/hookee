import unittest

from hookie import hookie

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.0.0"


class TestNgrok(unittest.TestCase):

    def test_main(self):
        # WHEN
        hookie.main()

        # THEN
        pass
