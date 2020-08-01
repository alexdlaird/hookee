import time
import unittest
from urllib import request

from pyngrok import ngrok

from hookee import cli, server

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
        req = request.Request("http://127.0.0.1:5000/webhook", method="POST")
        request.urlopen(req)

        ngrok.kill()
        server.stop_server()
