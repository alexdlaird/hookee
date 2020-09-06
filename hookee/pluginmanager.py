import os

from hookee import util

from pluginbase import PluginBase

if util.is_python_3():
    import importlib.util
else:
    import imp

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"

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
    :var ctx: The ``click`` CLI context.
    :vartype ctx: click.Context
    :var config: The ``hookee`` configuration.
    :vartype config: Config
    :var source: The ``hookee`` configuration.
    :vartype source: pluginbase.PluginSource
    :var request_script: A request plugin loaded from the script at ``--request_script``, run last.
    :vartype request_script: module
    :var response_script: A response plugin loaded from the script at ``--response_script``, run last.
    :vartype response_script: module
    :var response_body: The response body loaded from ``--response``, overrides any body data from response plugins.
    :vartype response_body: module
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
        self.request_script = None
        self.response_script = None
        self.response_body = None
        self.response_content_type = None

        self.builtin_plugins_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins"))

        self.loaded_plugins = []

        self.source_plugins()

    def validate_plugin(self, plugin):
        """
        Validate a given module to see if it is a valid ``hookee`` plugin. If validation fails, an exception
        will be thrown.

        :param plugin: The module to validate as a valid plugin.
        :type plugin: module
        :return: ``True`` if the validated plugin has a ``setup()`` method, ``False`` otherwise.
        :type: bool
        """
        try:
            functions_list = util.get_functions(plugin)
            attributes = dir(plugin)

            if "plugin_type" not in attributes:
                self.ctx.fail("Plugin \"{}\" does not conform to the plugin spec.".format(self.get_plugin_name(plugin)))
            elif plugin.plugin_type not in VALID_PLUGIN_TYPES:
                self.ctx.fail("Plugin \"{}\" must specify a valid `plugin_type`.".format(self.get_plugin_name(plugin)))
            elif plugin.plugin_type == REQUEST_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail("Plugin \"{}\" must implement run(request).".format(self.get_plugin_name(plugin)))
                elif len(util.get_args(plugin.run)[0]) < 1:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request)` must be defined.".format(
                            self.get_plugin_name(plugin)))
            elif plugin.plugin_type == RESPONSE_PLUGIN:
                if "run" not in functions_list:
                    self.ctx.fail(
                        "Plugin \"{}\" must implement run(request, response).".format(self.get_plugin_name(plugin)))
                elif len(util.get_args(plugin.run)[0]) < 2:
                    self.ctx.fail(
                        "Plugin \"{}\" does not conform to the plugin spec, `run(request, response)` must be defined.".format(
                            self.get_plugin_name(plugin)))
            elif plugin.plugin_type == BLUEPRINT_PLUGIN and "blueprint" not in attributes:
                self.ctx.fail(
                    "Plugin \"{}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.".format(
                        self.get_plugin_name(plugin)))

            return "setup" in functions_list
        except ModuleNotFoundError:
            self.ctx.fail("Plugin \"{}\" could not be found.".format(self.get_plugin_name(plugin)))

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

        self.request_script = self.import_from_file(self.config.get("request_script"))
        self.response_script = self.import_from_file(self.config.get("response_script"))
        self.response_body = self.config.get("response")
        self.response_content_type = self.config.get("content_type")

        if self.response_content_type and not self.response_body:
            self.ctx.fail("If `--content_type` is given, `--response` must also be given.")

    def get_plugin_name(self, plugin):
        """
        Get the name of the plugin from the module.

        :param plugin: The plugin.
        :type plugin: module
        :return: The name of the plugin.
        :rtype: str
        """
        return os.path.basename(plugin.__file__).strip(".py")

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

    def run_request_plugins(self, request):
        """
        Run all enabled request plugins.

        :param request: The request object being processed.
        :type request: flask.Request
        :return: The processed request.
        :rtype: flask.Request
        """
        for plugin in self.get_plugins_by_type(REQUEST_PLUGIN):
            request = plugin.run(request)
        if self.request_script:
            self.request_script.run(request)

        return request

    def run_response_plugins(self, request=None, response=None):
        """
        Run all enabled response plugins, running the ``response_info`` plugin (if enabled) last.

        :param request: The request object being processed.
        :type request: flask.Request, optional
        :param response: The response object being processed.
        :type response: flask.Response, optional
        :return: The processed response.
        :rtype: flask.Response
        """
        response_info_plugin = None
        for plugin in self.get_plugins_by_type(RESPONSE_PLUGIN):
            if self.get_plugin_name(plugin) == "response_info":
                response_info_plugin = plugin
            else:
                response = plugin.run(request, response)
        if self.response_script:
            response = self.response_script.run(request, response)
        if self.response_body:
            response.data = self.response_body
            response.headers[
                "Content-Type"] = self.response_content_type if self.response_content_type else "text/plain"
        if response_info_plugin:
            response = response_info_plugin.run(request, response)

        return response
