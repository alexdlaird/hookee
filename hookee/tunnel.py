import threading
import time

import click
from hookee import conf
from pyngrok import ngrok

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


class Tunnel:
    def __init__(self, port):
        self.port = port

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
            self._open_banner()

            self._thread = threading.Thread(target=self._loop)
            self._thread.daemon = True
            self._thread.start()

            while self.public_url is None:
                time.sleep(1)

            self._close_banner()

    def _start_tunnel(self):
        self.public_url = ngrok.connect(self.port).replace("http", "https")
        self.ngrok_process = ngrok.get_ngrok_process()

    def stop(self):
        if self._thread:
            ngrok.kill()

            self.public_url = None
            self.ngrok_process = None
            self._thread = None

    def _open_banner(self):
        title = "Opening Tunnel"
        width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

        click.echo("")
        click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="red", bold=True)
        click.echo("")

    def _close_banner(self):
        click.echo(
            "* Tunnel: {} -> http://127.0.0.1:{}".format(self.public_url.replace("http://", "https://"), self.port))
        click.echo("")
        click.secho("-" * conf.CONSOLE_WIDTH, fg="red", bold=True)
