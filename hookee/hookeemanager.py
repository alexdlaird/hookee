__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import os
import time
from typing import NoReturn, Optional

import click

from hookee import __version__
from hookee.conf import Config
from hookee.exception import HookeeConfigError, HookeeError
from hookee.pluginmanager import PluginManager
from hookee.server import Server
from hookee.tunnel import Tunnel
from hookee.util import PrintUtil

banner_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "banner.txt")
with open(banner_path) as f:
    banner = f.read()


class HookeeManager:
    """
    An object that manages the state of a ``hookee`` runtime. Reads app configuration, loads enabled plugins,
    and manages the long-lived state of ``hookee`` if a server and tunnel are started.

    If instantiating for a custom integration, pass a :class:`~hookee.conf.Config` with args that otherwise would have
    been passed to the CLI (see ``hookee --help``). For example:

    .. code-block:: python

        from hookee import HookeeManager
        from hookee.conf import Config

        config = Config(url="https://my-hooks.ngrok.io")
        hookee_manager = HookeeManager(config=config)

    A ``response_callback`` function can also be passed instead of defining a raw ``response`` and ``content-type``
    (or needing to use plugins) when integrating with ``hookee``:

    .. code-block:: python

        from hookee import HookeeManager
        from hookee.conf import Config

        def response_callback(request, response):
            response.data = "<Response>Ok</Response>"
            response.headers["Content-Type"] = "application/xml"
            return response

        config = Config(response_callback=response_callback)
        hookee_manager = HookeeManager(config=config)
    """

    def __init__(self,
                 config: Optional[Config] = None,
                 load_plugins: bool = True) -> None:
        #: The ``click`` context.
        self.ctx: Optional[click.Context] = click.get_current_context(silent=True)

        if config is None:
            try:
                data = self.ctx.obj if self.ctx is not None else {}
                config = Config(**data)
            except HookeeConfigError as e:
                self.fail(str(e), e)

        #: The ``hookee`` configuration.
        self.config: Config = config
        #: Reference to the Plugin Manager.
        self.plugin_manager: PluginManager = PluginManager(self)
        #: Reference to the PrintUtil.
        self.print_util: PrintUtil = PrintUtil(self.config)

        if load_plugins:
            self.plugin_manager.load_plugins()

        #: Reference to the Tunnel.
        self.tunnel: Tunnel = Tunnel(self)
        #: Reference to the Server.
        self.server: Server = Server(self)

        #: ``True`` when this object is managing an active tunnel and server.
        self.alive: bool = False

        self.print_hookee_banner()

    def run(self) -> None:
        """
        If one is not already running, start a managed server and tunnel and block until an interrupt
        is received (or ``alive`` is set to ``False``).
        """
        if not self.alive:
            try:
                self._init_server_and_tunnel()

                while self.alive:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

            self.stop()

    def stop(self) -> None:
        """
        If running, shutdown the managed server and tunnel.
        """
        if self.alive:
            self.server.stop()
            if self.tunnel._thread:
                self.tunnel._thread.alive = False

            # Wait for the other threads to teardown
            while self.server._thread and self.tunnel._thread:
                time.sleep(1)

            self.alive = False

    def print_hookee_banner(self) -> None:
        self.print_util.print_open_header("", "=")
        self.print_util.print_basic(banner.format(version=__version__), color="green", bold=True)
        self.print_util.print_basic()
        self.print_util.print_close_header("=", blank_line=False)

    def print_ready(self) -> None:
        self.print_util.print_open_header("Registered Plugins")

        plugins = self.plugin_manager.enabled_plugins()
        self.print_util.print_basic(f" * Enabled Plugins: {plugins}")
        if self.plugin_manager.response_callback:
            self.print_util.print_basic("   Response callback: enabled")

        self.print_util.print_close_header()

        self.print_util.print_open_header("Registered Endpoints")

        if self.tunnel.public_url:
            host = self.tunnel.public_url
        else:
            host = f"http://localhost:{self.server.port}"

        forward_to = self.config.get("forward_to")
        if forward_to:
            self.print_util.print_basic(f" * {host}/ -> {forward_to.rstrip('/')}/ (all paths are forwarded)",
                                        print_when_logging=True)
        else:
            default_route = self.config.get("default_route")
            default_route_methods = self.config.get("default_route_methods").split(",")
            self.print_util.print_basic(f" * {host}{default_route}", print_when_logging=True)
            self.print_util.print_basic(f"   Methods: {sorted(list(default_route_methods))}", print_when_logging=True)

        rules = list(filter(lambda r: r.rule not in ["/<path:uri>", "/status", "/static/<path:filename>"],
                            self.server.app.url_map.iter_rules()))
        for rule in rules:
            self.print_util.print_basic(f" * {host}{rule.rule}", print_when_logging=True)
            self.print_util.print_basic(f"   Methods: {sorted(list(rule.methods))}", print_when_logging=True)

        self.print_util.print_close_header()

        self.print_util.print_basic()
        self.print_util.print_basic("--> Ready, send a request to a registered endpoint ...", color="green", bold=True)
        self.print_util.print_basic()

    def fail(self,
             msg: str,
             e: Optional[HookeeError] = None) -> NoReturn:
        """
        Shutdown the current application with a failure. If a CLI Context exists, that will be used to invoke the
        failure, otherwise an exception will be thrown for failures to be caught.

        :param msg: The failure message.
        :param e: The error being raised.
        """
        if self.ctx is not None:
            self.ctx.fail(msg)
        elif e:
            raise e
        else:
            raise HookeeError(msg)

    def _init_server_and_tunnel(self) -> None:
        self.alive = True
        self.server.start()
        if not self.config.get("no_tunnel"):
            self.tunnel.start()

        self.print_ready()
