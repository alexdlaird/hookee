import time

import click

from hookee import conf
from hookee.pluginmanager import PluginManager
from hookee.server import Server
from hookee.tunnel import Tunnel
from hookee.util import PrintUtil

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.12"


class CliManager:
    """
    An object that manages the state of a CLI application. Reads application configuration, loads enabled plugins,
    and manages the long-lived state of the application if a server and tunnel are started.

    :var ctx: The ``click`` CLI context.
    :vartype ctx: click.Context
    :var config: The ``hookee`` configuration.
    :vartype config: Config
    :var plugin_manager: Reference to the Plugin Manager.
    :vartype plugin_manager: PluginManager
    :var print_util: Reference to the PrintUtil.
    :vartype print_util: PrintUtil
    :var tunnel: Reference to the Tunnel.
    :vartype tunnel: Tunnel
    :var server: Reference to the Server.
    :vartype server: Server
    :var alive: ``True`` when this object is managing an active tunnel and server, ``False`` otherwise.
    :vartype alive: bool
    """

    def __init__(self, ctx, load_plugins=True):
        self.ctx = ctx

        self.config = conf.Config(self.ctx)
        self.plugin_manager = PluginManager(self)
        self.print_util = PrintUtil(self.config)

        if load_plugins:
            self.plugin_manager.load_plugins()

        self.tunnel = Tunnel(self)
        self.server = Server(self)

        self.alive = False

        self.print_hookee_banner()

    def start(self):
        """
        If one is not already running, start a managed server and tunnel and block until an interrupt
        is received (or ``alive`` is set to False).
        """
        if not self.alive:
            try:
                self._init_server_and_tunnel()

                while self.alive:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

            self.stop()

    def stop(self):
        """
        If running, shutdown server and tunnel.
        """
        if self.alive:
            self.server.stop()
            if self.tunnel._thread:
                self.tunnel._thread.alive = False

            # Wait for the other threads to teardown
            while self.server._thread and self.tunnel._thread:
                time.sleep(1)

            self.alive = False

    def print_hookee_banner(self):
        self.print_util.print_open_header("", "=")
        click.secho("""                .__                   __                  
                |  |__   ____   ____ |  | __ ____   ____  
                |  |  \ /  _ \ /  _ \|  |/ // __ \_/ __ \ 
                |   Y  (  <_> |  <_> )    <\  ___/\  ___/ 
                |___|  /\____/ \____/|__|_ \\___  >\___  >
                     \/                   \/    \/     \/ 
                                                   v{}""".format(__version__), fg="green", bold=True)
        self.print_util.print_close_header("=")

    def print_ready(self):
        self.print_util.print_open_header("Registered Endpoints")

        rules = list(filter(lambda r: r.rule not in ["/shutdown", "/static/<path:filename>", "/status"],
                            self.server.app.url_map.iter_rules()))
        for rule in rules:
            click.secho("* {}{}".format(self.tunnel.public_url, rule.rule))
            click.secho("  Methods: {}".format(sorted(list(rule.methods))))
            click.echo("")

        self.print_util.print_close_header()

        click.echo("")
        click.secho("--> Ready, send a request to a registered endpoint ...", fg="green", bold=True)
        click.echo("")

    def _init_server_and_tunnel(self):
        self.alive = True
        self.server.start()
        self.tunnel.start()

        self.print_ready()
