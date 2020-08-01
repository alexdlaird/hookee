import time
import unittest

from pyngrok import ngrok

from hookee import cli, server

from future.standard_library import install_aliases

install_aliases()

from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"


class TestCLI(unittest.TestCase):

    def test_main(self):
        # TODO: We'll come back to this after the POC
        # WHEN
        cli.main()
        time.sleep(2)

        # THEN
        req = Request("http://127.0.0.1:5000/webhook", method="POST")
        urlopen(req)

        ngrok.kill()
        server.stop_server()
