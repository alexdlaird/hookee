import logging
import threading
import time

import click

from flask import Flask

from future.standard_library import install_aliases

from hookee import util

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
__version__ = "0.0.4"

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


class Server:
    def __init__(self, manager):
        self.manager = manager
        self.port = self.manager.config.get("port")

        self.app = self.create_app()

        self._thread = None

    def create_app(self):
        app = Flask(__name__)

        app.config.from_mapping(
            ENV="development"
        )

        for plugin in self.manager.get_plugins_by_type(util.BLUEPRINT_PLUGIN):
            app.register_blueprint(plugin.blueprint)

        return app

    def _loop(self):
        thread = threading.current_thread()
        thread.alive = True

        # This will block until stop() is invoked to shutdown the Werkzeug server
        self.app.run(host="127.0.0.1", port=self.port, debug=True, use_reloader=False)

        thread.alive = False

    def start(self):
        if self._thread is None:
            self.manager.print_util.print_open_header("Starting Server")

            self._thread = threading.Thread(target=self._loop)
            self._thread.start()

            while self._server_status() != StatusCodes.OK:
                time.sleep(1)

            self.print_close_header()

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

    def print_close_header(self):
        click.echo(" * Port: {}".format(self.port))
        click.echo(" * Blueprints: registered")
        click.echo("")
        self.manager.print_util.print_close_header()
