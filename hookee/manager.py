import inspect
import os
import time

import click

from hookee import conf, util
from hookee.server import Server
from hookee.tunnel import Tunnel
from hookee.util import PrintUtil

from pluginbase import PluginBase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"


class Manager:
    def __init__(self, ctx):
        self.ctx = ctx

        self.config = conf.Config(self.ctx)
        self.last_request = None
        self.last_response = None
        self.loaded_plugins = self.load_plugins()
        self.print_util = PrintUtil(self.config)

        # TODO: validate if no plugins are loaded (for instance, if no Blueprints loaded, hookee will hang on startup)

        self.tunnel = Tunnel(self)
        self.server = Server(self)

        self.alive = False

        self.print_util.print_hookee_banner()

    def start(self):
        if not self.alive:
            try:
                self.alive = True
                self.server.start()
                self.tunnel.start()

                self.print_ready()

                while self.alive:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                # self.alive = False
                # self.server.stop()
                # self.tunnel.stop()

            self.stop()

    def stop(self):
        if self.alive:
            self.server.stop()
            if self.tunnel._thread:
                self.tunnel._thread.alive = False

            # Wait for the other threads to teardown
            while self.server._thread and self.tunnel._thread:
                time.sleep(1)

            self.alive = False

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

    def validate_plugin(self, plugin):
        try:
            functions_list = [o[0] for o in inspect.getmembers(plugin, inspect.isfunction)]
            attributes = dir(plugin)

            if not all(elem in attributes for elem in ["plugin_type", "manager"]):
                self.ctx.fail("Plugin \"{}\" does not conform to the plugin spec.".format(plugin.__name__))

            if plugin.plugin_type in [util.REQUEST_PLUGIN, util.RESPONSE_PLUGIN]:
                all(elem in functions_list for elem in ["setup", "run"])
            elif plugin.plugin_type == util.BLUEPRINT_PLUGIN:
                all(elem in functions_list for elem in ["setup"])
            else:
                self.ctx.fail("Plugin \"{}\" is not a valid plugin type.".format(plugin.__name__))

            # TODO: additionally validate the functions have correct num args

            return plugin
        except ModuleNotFoundError:
            self.ctx.fail("Plugin \"{}\" could not be found.".format(plugin.__name__))

    def load_plugins(self):
        builtin_plugins_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins"))
        plugins_dir = self.config.get("plugins_dir")
        enabled_plugins = self.config.get("plugins")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

        loaded_plugins = []
        for plugin_name in enabled_plugins:
            plugin = self.validate_plugin(self.source.load_plugin(plugin_name))
            plugin.setup(self)
            loaded_plugins.append(plugin)

        last_request = self.config.get("last_request")
        if last_request:
            self.last_request = __import__(last_request.__name__, globals(), {}, ['__name__'])
            self.validate_plugin(self.last_request)
        last_response = self.config.get("last_response")
        if last_response:
            self.last_response = __import__(last_response.__name__, globals(), {}, ['__name__'])
            self.validate_plugin(self.last_response)

        return loaded_plugins

    def get_plugins_by_type(self, plugin_type):
        return filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins)
