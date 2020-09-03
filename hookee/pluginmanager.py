import inspect
import os

from hookee import util

from pluginbase import PluginBase

if util.is_python_3():
    import importlib.util
else:
    import imp

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

        self.source_plugins()

    def validate_plugin(self, plugin):
        try:
            functions_list = [o[0] for o in inspect.getmembers(plugin, inspect.isfunction)]
            attributes = dir(plugin)

            if "plugin_type" not in attributes:
                self.ctx.fail("Plugin \"{}\" does not conform to the plugin spec.".format(plugin.__name__))
            elif plugin.plugin_type not in util.VALID_PLUGIN_TYPES:
                self.ctx.fail("Plugin \"{}\" must specify a valid `plugin_type`.".format(plugin.__name__))
            elif plugin.plugin_type == util.REQUEST_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail("Plugin \"{}\" must implement run(request).".format(plugin.__name__))
                elif len(inspect.getargspec(plugin.run)[0]) < 1:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request)` must be defined.".format(
                            plugin.__name__))
            elif plugin.plugin_type == util.RESPONSE_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail("Plugin \"{}\" must implement run(request, response).".format(plugin.__name__))
                elif len(inspect.getargspec(plugin.run)[0]) < 2:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request, response)` must be defined.".format(
                            plugin.__name__))
            elif plugin.plugin_type == util.BLUEPRINT_PLUGIN and "blueprint" not in attributes:
                self.ctx.fail(
                    "Plugin \"{}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.".format(
                        plugin.__name__))

            return plugin, "setup" in functions_list
        except ModuleNotFoundError:
            self.ctx.fail("Plugin \"{}\" could not be found.".format(plugin.__name__))

    def source_plugins(self):
        plugins_dir = self.config.get("plugins_dir")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[self.builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

    def load_plugins(self):
        enabled_plugins = self.config.get("plugins")

        for plugin_name in util.REQUIRED_PLUGINS:
            if plugin_name not in enabled_plugins:
                self.ctx.fail(
                    "Sorry, the plugin {} is required. Run `hookee enable-plugin {}` before continuing.".format(
                        plugin_name, plugin_name))

        self.source_plugins()

        self.loaded_plugins = []
        for plugin_name in enabled_plugins:
            plugin, has_setup = self.validate_plugin(self.source.load_plugin(plugin_name))
            if has_setup:
                plugin.setup(self.cli_manager)
            self.loaded_plugins.append(plugin)

        self.last_request = self.import_from_file(self.config.get("last_request"))
        self.last_response = self.import_from_file(self.config.get("last_response"))

    def get_plugins_by_type(self, plugin_type):
        return filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins)

    def import_from_file(self, filename):
        if filename:
            module_name = os.path.basename(filename).strip(".py")

            if util.is_python_3():
                spec = importlib.util.spec_from_file_location(module_name, filename)
                plugin = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin)
            else:
                plugin = imp.load_source(module_name, filename)

            plugin, has_setup = self.validate_plugin(plugin)
            if has_setup:
                plugin.setup(self.cli_manager)

            return plugin
