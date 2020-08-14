import importlib
import logging
import pkgutil
import threading
import time

import click

import hookee.plugins

from flask import Flask

from future.standard_library import install_aliases

from hookee import conf
from hookee.blueprints import default_blueprint

install_aliases()

from urllib.request import urlopen, Request
from urllib.error import URLError

try:
    from http import HTTPStatus as StatusCodes
except ImportError:  # pragma: no cover
    try:
        from http import client as StatusCodes
    except ImportError:
        import httplib as StatusCodes

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

blueprints = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules(hookee.blueprints.__path__, hookee.blueprints.__name__ + ".")
}


class Server:
    def __init__(self, port):
        self.port = port

        self.app = self.create_app()

        self._thread = None

    def create_app(self):
        app = Flask(__name__)

        app.config.from_mapping(
            ENV="development"
        )

        # TODO: will refactor this to support a real plugin arch after POC
        for b in blueprints.values():
            app.register_blueprint(b.blueprint)

        return app

    def _loop(self):
        thread = threading.current_thread()
        thread.alive = True

        # This will block until stop() is invoked to shutdown the Werkzeug server
        self.app.run(host="127.0.0.1", port=self.port, debug=True, use_reloader=False)

        thread.alive = False

    def start(self):
        if self._thread is None:
            self._open_banner()

            self._thread = threading.Thread(target=self._loop)
            self._thread.start()

            while self._server_status() != StatusCodes.OK:
                time.sleep(1)

            self._close_banner()

    def stop(self):
        if self._thread:
            req = Request("http://127.0.0.1:{}/shutdown".format(self.port), method="POST")
            urlopen(req)

            self._thread = None

    def _server_status(self):
        try:
            return urlopen("http://127.0.0.1:{}/status".format(self.port)).getcode()
        except URLError:
            return StatusCodes.INTERNAL_SERVER_ERROR

    def _open_banner(self):
        title = "Starting Server"
        width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

        click.echo("")
        click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="red", bold=True)
        click.echo("")

    def _close_banner(self):
        click.echo(" * Port: {}".format(self.port))
        click.echo(" * Blueprints: registered")
        click.echo("")
        click.secho("-" * conf.CONSOLE_WIDTH, fg="red", bold=True)
