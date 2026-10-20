__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import logging
import threading
from typing import TYPE_CHECKING, Optional

from flask import Flask
from werkzeug.serving import BaseWSGIServer, make_server

from hookee import pluginmanager
from hookee.pluginmanager import PluginManager
from hookee.util import PrintUtil

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.ERROR)


class Server:
    """
    An object that manages a non-blocking Flask server and thread.
    """

    def __init__(self, hookee_manager: "HookeeManager") -> None:
        #: Reference to the ``hookee`` Manager.
        self.hookee_manager: "HookeeManager" = hookee_manager
        #: Reference to the Plugin Manager.
        self.plugin_manager: PluginManager = self.hookee_manager.plugin_manager
        #: Reference to the PrintUtil.
        self.print_util: PrintUtil = self.hookee_manager.print_util
        #: The server's port.
        self.port: int = self.hookee_manager.config.get("port")

        #: The Flask app.
        self.app: Flask = self.create_app()

        self._server: Optional[BaseWSGIServer] = None
        self._thread: Optional[threading.Thread] = None

    def create_app(self) -> Flask:
        """
        Create a Flask app and register all Blueprints found in enabled plugins.

        :return: The Flask app.
        """
        app = Flask(__name__)

        for plugin in self.plugin_manager.get_plugins_by_type(pluginmanager.BLUEPRINT_PLUGIN):
            app.register_blueprint(plugin.blueprint)

        return app

    def start(self) -> None:
        """
        If one is not already running, start a server in a new thread.
        """
        if self._thread is None:
            self.print_util.print_open_header("Starting Server")

            self._server = make_server("127.0.0.1", self.port, self.app, threaded=True)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()

            self.print_close_header()

    def stop(self) -> None:
        """
        If running, shutdown the server and its thread.
        """
        if self._thread:
            self._server.shutdown()
            self._server.server_close()

            self._server = None
            self._thread = None

    def print_close_header(self) -> None:
        self.print_util.print_basic(f" * Port: {self.port}")
        self.print_util.print_basic(" * Blueprints: registered")
        self.print_util.print_close_header()
