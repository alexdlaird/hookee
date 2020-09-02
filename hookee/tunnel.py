import threading
import time

import click

from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.4"


class Tunnel:
    def __init__(self, manager):
        self.manager = manager
        self.port = self.manager.config.get("port")

        self.pyngrok_config = PyngrokConfig(auth_token=self.manager.config.get("auth_token"))

        self.public_url = None
        self.ngrok_process = None
        self._thread = None

    def _loop(self):
        self._start_tunnel()

        thread = threading.current_thread()
        thread.alive = True
        while thread.alive:
            time.sleep(1)

        thread.alive = False

        self.stop()

    def start(self):
        if self._thread is None:
            self.manager.print_util.print_open_header("Opening Tunnel")

            self._thread = threading.Thread(target=self._loop)
            self._thread.daemon = True
            self._thread.start()

            while self.public_url is None:
                time.sleep(1)

            self.print_close_header()

    def _start_tunnel(self):
        self.public_url = ngrok.connect(self.port, pyngrok_config=self.pyngrok_config).replace("http", "https")
        self.ngrok_process = ngrok.get_ngrok_process()

    def stop(self):
        if self._thread:
            ngrok.kill()

            self.public_url = None
            self.ngrok_process = None
            self._thread = None

    def print_close_header(self):
        click.echo(
            "* Tunnel: {} -> http://127.0.0.1:{}".format(self.public_url.replace("http://", "https://"), self.port))
        click.echo("")
        self.manager.print_util.print_close_header()
