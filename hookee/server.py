__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import logging
import threading
import time
from http import HTTPStatus
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Flask

from hookee import pluginmanager

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.ERROR)


class Server:
    """
    An object that manages a non-blocking Flask server and thread.

    :var hookee_manager: Reference to the ``hookee`` Manager.
    :vartype hookee_manager: HookeeManager
    :var plugin_manager: Reference to the Plugin Manager.
    :vartype plugin_manager: PluginManager
    :var print_util: Reference to the PrintUtil.
    :vartype print_util: PrintUtil
    :var port: The server's port.
    :vartype port: int
    :var app: The Flask app.
    :vartype app: flask.Flask
    """

    def __init__(self, hookee_manager):
        self.hookee_manager = hookee_manager
        self.plugin_manager = self.hookee_manager.plugin_manager
        self.print_util = self.hookee_manager.print_util
        self.port = self.hookee_manager.config.get("port")

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
        thread = None

        try:
            thread = threading.current_thread()
            thread.alive = True

            # This will block until stop() is invoked to shutdown the Werkzeug server
            self.app.run(host="127.0.0.1", port=self.port, debug=True, use_reloader=False)
        except OSError as e:
            self.print_util.print_basic(e)

            self.stop()

        if thread:
            thread.alive = False

    def start(self):
        """
        If one is not already running, start a server in a new thread.
        """
        if self._thread is None:
            self.print_util.print_open_header("Starting Server")

            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

            while self._server_status() != HTTPStatus.OK:
                time.sleep(1)

            self.print_close_header()

    def stop(self):
        """
        This method is only useful when the Flask version has been overridden to use an older version (<2). With
        recent versions of Flask, the underlying server daemon will terminate when ``hookee`` terminates.
        """
        if self._thread:
            req = Request(f"http://127.0.0.1:{self.port}/shutdown", method="POST")
            urlopen(req)

            self._thread = None

    def _server_status(self):
        """
        Get the response code of the server's ``/status`` endpoint.

        :return: The status code.
        :rtype: http.HTTPStatus
        """
        try:
            return urlopen(f"http://127.0.0.1:{self.port}/status").getcode()
        except URLError:
            return HTTPStatus.INTERNAL_SERVER_ERROR

    def print_close_header(self):
        self.print_util.print_basic(f" * Port: {self.port}")
        self.print_util.print_basic(" * Blueprints: registered")
        self.print_util.print_close_header()
