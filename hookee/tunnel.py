__copyright__ = "Copyright (c) 2020-2025 Alex Laird"
__license__ = "MIT"

import threading
import time

from pyngrok import conf, ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokError


class Tunnel:
    """
    An object that manages a non-blocking ``pyngrok`` tunnel and thread.

    :var hookee_manager: Reference to the ``hookee`` Manager.
    :vartype hookee_manager: HookeeManager
    :var plugin_manager: Reference to the Plugin Manager.
    :vartype plugin_manager: PluginManager
    :var print_util: Reference to the PrintUtil.
    :vartype print_util: PrintUtil
    :var port: The server's port.
    :vartype port: int
    :var pyngrok_config: The ``pyngrok`` config.
    :vartype pyngrok_config: pyngrok.conf.PyngrokConfig
    :var public_url: The public URL of the tunnel.
    :vartype public_url: str
    :var ngrok_process: The ``ngrok`` process.
    :vartype ngrok_process: pyngrok.process.NgrokProcess
    """

    def __init__(self, hookee_manager):
        self.hookee_manager = hookee_manager
        self.config = self.hookee_manager.config
        self.plugin_manager = self.hookee_manager.plugin_manager
        self.print_util = self.hookee_manager.print_util
        self.port = self.config.get("port")

        self.pyngrok_config = PyngrokConfig(auth_token=self.config.get("auth_token"),
                                            api_key=self.config.get("api_key"),
                                            region=self.config.get("region"))
        conf.set_default(self.pyngrok_config)

        self.public_url = None
        self.ngrok_process = None
        self._thread = None

    def _loop(self):
        thread = None

        try:
            self._start_tunnel()

            thread = threading.current_thread()
            thread.alive = True
            while thread.alive:
                time.sleep(1)
        except PyngrokError:
            # pyngrok already logged this to the console for us
            pass

        if thread:
            thread.alive = False

        self.stop()

    def start(self):
        """
        If one is not already running, start a tunnel in a new thread.
        """
        if self._thread is None:
            self.print_util.print_open_header("Opening Tunnel")

            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

            while self.public_url is None:
                time.sleep(1)

            self.print_close_header()

    def _start_tunnel(self):
        options = {"schemes": ["https"]}
        name = self.config.get("tunnel_name")
        subdomain = self.config.get("subdomain")
        domain = self.config.get("domain", self.config.get("hostname"))
        host_header = self.config.get("host_header")
        basic_auth = self.config.get("basic_auth", self.config.get("auth"))
        if name:
            options["name"] = name
        if subdomain:
            options["subdomain"] = subdomain
        if domain:
            options["domain"] = domain
        if host_header:
            options["host_header"] = host_header
        if basic_auth:
            if isinstance(basic_auth, list):
                options["basic_auth"] = basic_auth
            else:
                options["basic_auth"] = [basic_auth]

        self.public_url = ngrok.connect(self.port,
                                        **options).public_url
        self.ngrok_process = ngrok.get_ngrok_process()

    def stop(self):
        """
        If running, kill the tunnel and cleanup its thread.
        """
        if self._thread:
            ngrok.kill()

            self.public_url = None
            self.ngrok_process = None
            self._thread = None

    def print_close_header(self):
        self.print_util.print_basic(
            f" * Tunnel: {self.public_url} -> http://127.0.0.1:{self.port}",
            print_when_logging=True)
        self.print_util.print_close_header()
