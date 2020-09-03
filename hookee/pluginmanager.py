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

BLUEPRINT_PLUGIN = "blueprint"
REQUEST_PLUGIN = "request"
RESPONSE_PLUGIN = "response"

VALID_PLUGIN_TYPES = [BLUEPRINT_PLUGIN, REQUEST_PLUGIN, RESPONSE_PLUGIN]
REQUIRED_PLUGINS = ["blueprint_default"]


class PluginManager:
    """
    An object that loads, validates, and manages available and enabled plugins.

    :var cli_manager: Reference to the CLI Manager.
    :vartype cli_manager: CliManager
    :var ctx: The :code:`click` CLI context.
    :vartype ctx: click.Context
    :var config: The :code:`hookee` configuration.
    :vartype config: Config
    :var source: The :code:`hookee` configuration.
    :vartype source: pluginbase.PluginSource
    :var last_request: A plugin loaded from the script at :code:`--request` from the CLI arg.
    :vartype last_request: module
    :var last_response: A plugin loaded from the script at :code:`--response` from the CLI arg.
    :vartype last_response: module
    :var builtin_plugins_dir: The directory where built-in plugins reside.
    :vartype builtin_plugins_dir: str
    :var loaded_plugins: A list of plugins that have been validated and imported.
    :vartype loaded_plugins: list[module]
    """

    def __init__(self, cli_manager):
        self.cli_manager = cli_manager
        self.ctx = cli_manager.ctx
        self.config = cli_manager.config

        self.source = None
        self.last_request = None
        self.last_response = None

        self.builtin_plugins_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins"))

        self.loaded_plugins = []

        self.source_plugins()

    def validate_plugin(self, plugin):
        """
        Validate a given module to see if it is a valid `hookee` plugin. If validation fails, an exception
        will be thrown.

        :param plugin: The module to validate as a valid plugin.
        :type plugin: module
        :return: :code:`True` if the validated plugin has a `setup()` method, :code:`False` otherwise.
        :type: bool
        """
        try:
            functions_list = util.get_functions(plugin)
            attributes = dir(plugin)

            if "plugin_type" not in attributes:
                self.ctx.fail("Plugin \"{}\" does not conform to the plugin spec.".format(plugin.__name__))
            elif plugin.plugin_type not in VALID_PLUGIN_TYPES:
                self.ctx.fail("Plugin \"{}\" must specify a valid `plugin_type`.".format(plugin.__name__))
            elif plugin.plugin_type == REQUEST_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail("Plugin \"{}\" must implement run(request).".format(plugin.__name__))
                elif len(util.get_args(plugin.run)[0]) < 1:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request)` must be defined.".format(
                            plugin.__name__))
            elif plugin.plugin_type == RESPONSE_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail("Plugin \"{}\" must implement run(request, response).".format(plugin.__name__))
                elif len(util.get_args(plugin.run)[0]) < 2:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request, response)` must be defined.".format(
                            plugin.__name__))
            elif plugin.plugin_type == BLUEPRINT_PLUGIN and "blueprint" not in attributes:
                self.ctx.fail(
                    "Plugin \"{}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.".format(
                        plugin.__name__))

            return "setup" in functions_list
        except ModuleNotFoundError:
            self.ctx.fail("Plugin \"{}\" could not be found.".format(plugin.__name__))

    def source_plugins(self):
        """
        Source all paths in the plugin base to prepare for loading and validating plugins.
        """
        plugins_dir = self.config.get("plugins_dir")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[self.builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

    def load_plugins(self):
        """
        Load and validate all built-in plugins and custom plugins from sources in the plugin base.
        """
        enabled_plugins = self.config.get("plugins")

        for plugin_name in REQUIRED_PLUGINS:
            if plugin_name not in enabled_plugins:
                self.ctx.fail(
                    "Sorry, the plugin {} is required. Run `hookee enable-plugin {}` before continuing.".format(
                        plugin_name, plugin_name))

        self.source_plugins()

        self.loaded_plugins = []
        for plugin_name in enabled_plugins:
            plugin = self.source.load_plugin(plugin_name)
            if self.validate_plugin(plugin):
                plugin.setup(self.cli_manager)
            self.loaded_plugins.append(plugin)

        self.last_request = self.import_from_file(self.config.get("last_request"))
        self.last_response = self.import_from_file(self.config.get("last_response"))

    def get_plugins_by_type(self, plugin_type):
        """
        Filter loaded plugins by the given plugin type.

        :param plugin_type: The plugin type for filtering.
        :type plugin_type: str
        :return: The filtered list of plugins.
        :rtype: list[module]
        """
        return filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins)

    def import_from_file(self, path):
        """
        Import a Python script at the given path as a module that is executable.

        :param path: The path to the script to import.
        :type path: str
        :return: The imported script as a module.
        :rtype: module
        """
        if path:
            module_name = os.path.basename(path).strip(".py")

            if util.is_python_3():
                spec = importlib.util.spec_from_file_location(module_name, path)
                plugin = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin)
            else:
                plugin = imp.load_source(module_name, path)

            if self.validate_plugin(plugin):
                plugin.setup(self.cli_manager)

            return plugin
