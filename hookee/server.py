import logging
import threading
import time

import click

from flask import Flask

from future.standard_library import install_aliases

from hookee import pluginmanager

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
__version__ = "0.0.8"

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


class Server:
    """
    An object that manages a non-blocking Flask server thread.

    :var cli_manager: Reference to the CLI Manager.
    :vartype cli_manager: CliManager
    :var plugin_manager: Reference to the Plugin Manager.
    :vartype plugin_manager: PluginManager
    :var print_util: Reference to the PrintUtil.
    :vartype print_util: PrintUtil
    :var port: The server's port.
    :vartype port: int
    :var app: The Flask app.
    :vartype app: flask.Flask
    """

    def __init__(self, cli_manager):
        self.cli_manager = cli_manager
        self.plugin_manager = cli_manager.plugin_manager
        self.print_util = cli_manager.print_util
        self.port = self.cli_manager.config.get("port")

        self.app = self.create_app()

        self._thread = None

    def create_app(self):
        """
        Create a Flask app and register all Blueprints found in enabled plugins.

        :return: The Flask app.
        :rtype: flask.Flask
        """
        app = Flask(__name__)

        app.config.from_mapping(
            ENV="development"
        )

        for plugin in self.plugin_manager.get_plugins_by_type(pluginmanager.BLUEPRINT_PLUGIN):
            app.register_blueprint(plugin.blueprint)

        return app

    def _loop(self):
        thread = threading.current_thread()
        thread.alive = True

        # This will block until stop() is invoked to shutdown the Werkzeug server
        self.app.run(host="127.0.0.1", port=self.port, debug=True, use_reloader=False)

        thread.alive = False

    def start(self):
        """
        If one is not already running, start a server in a new thread.
        """
        if self._thread is None:
            self.print_util.print_open_header("Starting Server")

            self._thread = threading.Thread(target=self._loop)
            self._thread.start()

            while self._server_status() != StatusCodes.OK:
                time.sleep(1)

            self.print_close_header()

    def stop(self):
        """
        If running, kill the server and cleanup its thread.
        """
        if self._thread:
            req = Request("http://127.0.0.1:{}/shutdown".format(self.port), method="POST")
            urlopen(req)

            self._thread = None

    def _server_status(self):
        """
        Get the status code of the server's ``/status`` endpoint.

        :return: The status code.
        :rtype: http.HTTPStatus
        """
        try:
            return urlopen("http://127.0.0.1:{}/status".format(self.port)).getcode()
        except URLError:
            return StatusCodes.INTERNAL_SERVER_ERROR

    def print_close_header(self):
        click.echo(" * Port: {}".format(self.port))
        click.echo(" * Blueprints: registered")
        click.echo("")
        self.print_util.print_close_header()
