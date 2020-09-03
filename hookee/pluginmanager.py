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


class PluginManager:
    def __init__(self, cli_manager):

        self.cli_manager = cli_manager
        self.ctx = cli_manager.ctx
        self.config = cli_manager.config

        self.last_request = None
        self.last_response = None

        self.builtin_plugins_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins"))

        self.loaded_plugins = []

    def validate_plugin(self, plugin):
        try:
            functions_list = [o[0] for o in inspect.getmembers(plugin, inspect.isfunction)]
            attributes = dir(plugin)

            if "plugin_type" not in attributes:
                self.ctx.fail("Plugin \"{}\" does not conform to the plugin spec.".format(plugin.__name__))
            elif plugin.plugin_type not in util.VALID_PLUGIN_TYPES:
                self.ctx.fail("Plugin \"{}\" must specify a valid `plugin_type`.".format(plugin.__name__))
            elif plugin.plugin_type in [util.REQUEST_PLUGIN, util.RESPONSE_PLUGIN] and \
                    "run" not in functions_list:
                self.ctx.fail("Plugin \"{}\" must implement a run().".format(plugin.__name__))
            elif plugin.plugin_type == util.BLUEPRINT_PLUGIN and "blueprint" not in attributes:
                self.ctx.fail(
                    "Plugin \"{}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.".format(
                        plugin.__name__))

            # TODO: additionally validate the functions have correct num args

            return plugin, "setup" in functions_list
        except ModuleNotFoundError:
            self.ctx.fail("Plugin \"{}\" could not be found.".format(plugin.__name__))

    def load_plugins(self):
        plugins_dir = self.config.get("plugins_dir")
        enabled_plugins = self.config.get("plugins")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[self.builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

        self.loaded_plugins = []
        for plugin_name in enabled_plugins:
            plugin, has_setup = self.validate_plugin(self.source.load_plugin(plugin_name))
            if has_setup:
                plugin.setup(self.cli_manager)
            self.loaded_plugins.append(plugin)

        last_request = self.config.get("last_request")
        if last_request:
            self.last_request = __import__(last_request.__name__, globals(), {}, ['__name__'])
            self.validate_plugin(self.last_request)
        last_response = self.config.get("last_response")
        if last_response:
            self.last_response = __import__(last_response.__name__, globals(), {}, ['__name__'])
            self.validate_plugin(self.last_response)

    def get_plugins_by_type(self, plugin_type):
        return filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins)
