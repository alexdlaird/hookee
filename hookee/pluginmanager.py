import importlib.util
import os

from flask import current_app
from pluginbase import PluginBase

from hookee import util
from hookee.exception import HookeePluginValidationError

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "2.0.0"

BLUEPRINT_PLUGIN = "blueprint"
REQUEST_PLUGIN = "request"
RESPONSE_PLUGIN = "response"

VALID_PLUGIN_TYPES = [BLUEPRINT_PLUGIN, REQUEST_PLUGIN, RESPONSE_PLUGIN]
REQUIRED_PLUGINS = ["blueprint_default"]


class Plugin:
    """
    An object that represents a validated and loaded ``hookee`` plugin.

    :var module: The underlying plugin module.
    :vartype module: types.ModuleType
    :var plugin_type: The type of plugin.
    :vartype plugin_type: str
    :var name: The name of the plugin.
    :vartype name: str
    :var name: The description of the plugin.
    :vartype name: str, optional
    :var has_setup: ``True`` if the plugin has a ``setup(hookee_manager)`` method.
    :vartype has_setup: bool
    """

    def __init__(self, module, plugin_type, name, has_setup, description=None):
        self.module = module

        self.plugin_type = plugin_type
        self.name = name
        self.has_setup = has_setup
        self.description = description

        if self.plugin_type == BLUEPRINT_PLUGIN:
            self.blueprint = self.module.blueprint

    def setup(self, *args):
        """
        Passes through to the underlying module's ``setup(*args)``, if it exists.

        :param args: The args to pass through.
        :type args: tuple
        :return: The value returned by the module's function (or nothing if the module's function returns nothing).
        :rtype: object
        """
        if self.has_setup:
            return self.module.setup(*args)

    def run(self, *args):
        """
        Passes through to the underlying module's ``run(*args)``.

        :param args: The args to pass through.
        :type args: tuple
        :return: The value returned by the module's function (or nothing if the module's function returns nothing).
        :rtype: object
        """
        return self.module.run(*args)

    @staticmethod
    def build_from_module(module):
        """
        Validate and build a ``hookee`` plugin for the given module. If the module is not a valid ``hookee`` plugin,
        an exception will be thrown.

        :param module: The module to validate as a valid plugin.
        :type module: types.ModuleType
        :return: An object representing the validated plugin.
        :rtype: Plugin
        """
        name = util.get_module_name(module)

        functions_list = util.get_functions(module)
        attributes = dir(module)

        if "plugin_type" not in attributes:
            raise HookeePluginValidationError(
                "Plugin \"{}\" does not conform to the plugin spec.".format(name))
        elif module.plugin_type not in VALID_PLUGIN_TYPES:
            raise HookeePluginValidationError(
                "Plugin \"{}\" must specify a valid `plugin_type`.".format(name))
        elif module.plugin_type == REQUEST_PLUGIN:
            if "run" not in functions_list:
                raise HookeePluginValidationError(
                    "Plugin \"{}\" must implement `run(request)`.".format(name))
            elif len(util.get_args(module.run)) < 1:
                raise HookeePluginValidationError(
                    "Plugin \"{}\" does not conform to the plugin spec, `run(request)` must be defined.".format(
                        name))
        elif module.plugin_type == RESPONSE_PLUGIN:
            if "run" not in functions_list:
                raise HookeePluginValidationError(
                    "Plugin \"{}\" must implement `run(request, response)`.".format(name))
            elif len(util.get_args(module.run)) < 2:
                raise HookeePluginValidationError(
                    "Plugin \"{}\" does not conform to the plugin spec, `run(request, response)` must be defined.".format(
                        name))
        elif module.plugin_type == BLUEPRINT_PLUGIN and "blueprint" not in attributes:
            raise HookeePluginValidationError(
                "Plugin \"{}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.".format(
                    name))

        has_setup = "setup" in functions_list and len(util.get_args(module.setup)) == 1

        return Plugin(module, module.plugin_type, name, has_setup, getattr(module, "description", None))

    @staticmethod
    def build_from_file(path):
        """
        Import a Python script at the given path, then import it as a ``hookee`` plugin.

        :param path: The path to the script to import.
        :type path: str
        :return: The imported script as a plugin.
        :rtype: Plugin
        """
        module_name = os.path.splitext(os.path.basename(path))[0]

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return Plugin.build_from_module(module)


class PluginManager:
    """
    An object that loads, validates, and manages available plugins.

    :var hookee_manager: Reference to the ``hookee`` Manager.
    :vartype hookee_manager: HookeeManager
    :var config: The ``hookee`` configuration.
    :vartype config: Config
    :var source: The ``hookee`` configuration.
    :vartype source: pluginbase.PluginSource
    :var request_script: A request plugin loaded from the script at ``--request_script``, run last.
    :vartype request_script: Plugin
    :var response_script: A response plugin loaded from the script at ``--response_script``, run last.
    :vartype response_script: Plugin
    :var response_callback: The response body loaded from either ``--response``, or the lambda defined in the config's
        ``response_callback``. Overrides any body data from response plugins.
    :vartype response_body: str
    :var builtin_plugins_dir: The directory where built-in plugins reside.
    :vartype builtin_plugins_dir: str
    :var loaded_plugins: A list of plugins that have been validated and imported.
    :vartype loaded_plugins: list[Plugin]
    """

    def __init__(self, hookee_manager):
        self.hookee_manager = hookee_manager
        self.config = self.hookee_manager.config

        self.source = None
        self.response_callback = None

        self.builtin_plugins_dir = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins"))

        self.loaded_plugins = []

        self.source_plugins()

    def source_plugins(self):
        """
        Source all paths to look for plugins (defined in the config) to prepare them for loading and validation.
        """
        plugins_dir = self.config.get("plugins_dir")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[self.builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

    def load_plugins(self):
        """
        Load and validate all built-in plugins and custom plugins from sources in the plugin base.
        """
        enabled_plugins = self.enabled_plugins()

        for plugin_name in REQUIRED_PLUGINS:
            if plugin_name not in enabled_plugins:
                self.hookee_manager.fail(
                    "Sorry, the plugin {} is required. Run `hookee enable-plugin {}` before continuing.".format(
                        plugin_name, plugin_name))

        self.source_plugins()

        self.loaded_plugins = []
        for plugin_name in enabled_plugins:
            plugin = self.get_plugin(plugin_name)
            plugin.setup(self.hookee_manager)
            self.loaded_plugins.append(plugin)

        request_script = self.config.get("request_script")
        if request_script:
            request_script = Plugin.build_from_file(request_script)
            request_script.setup(self.hookee_manager)
            self.loaded_plugins.append(request_script)

        response_script = self.config.get("response_script")
        if response_script:
            response_script = Plugin.build_from_file(response_script)
            response_script.setup(self.hookee_manager)
            self.loaded_plugins.append(response_script)

        response_body = self.config.get("response")
        response_content_type = self.config.get("content_type")

        if response_content_type and not response_body:
            self.hookee_manager.fail("If `--content-type` is given, `--response` must also be given.")

        self.response_callback = self.config.response_callback

        if self.response_callback and response_body:
            self.hookee_manager.fail("If `response_callback` is given, `response` cannot also be given.")
        elif response_body and not self.response_callback:
            def response_callback(request, response):
                response.data = response_body
                response.headers[
                    "Content-Type"] = response_content_type if response_content_type else "text/plain"
                return response

            self.response_callback = response_callback

        if len(self.get_plugins_by_type(RESPONSE_PLUGIN)) == 0 and not self.response_callback:
            self.hookee_manager.fail(
                "No response plugin was loaded. Enable a pluing like `response_echo`, or pass `--response` "
                "or `--response-script`.")

    def get_plugins_by_type(self, plugin_type):
        """
        Get loaded plugins by the given plugin type.

        :param plugin_type: The plugin type for filtering.
        :type plugin_type: str
        :return: The filtered list of plugins.
        :rtype: list[Plugin]
        """
        return list(filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins))

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
            if plugin.name == "response_info":
                response_info_plugin = plugin
            else:
                response = plugin.run(request, response)

        if not response:
            response = current_app.response_class("")
        if self.response_callback:
            response = self.response_callback(request, response)

        if response_info_plugin:
            response = response_info_plugin.run(request, response)

        return response

    def get_plugin(self, plugin_name, throw_error=False):
        """
        Get the given plugin name from modules parsed by :func:`~hookee.pluginmanager.PluginManager.source_plugins`.

        :param plugin_name: The name of the plugin to load.
        :type plugin_name: str
        :param throw_error: ``True`` if errors encountered should be thrown to the caller, ``False`` if
            :func:`~hookee.hookeemanager.HookeeManager.fail` should be called.
        :return: The loaded plugin.
        :rtype: Plugin
        """
        try:
            return Plugin.build_from_module(self.source.load_plugin(plugin_name))
        except ImportError as e:
            if throw_error:
                raise e

            self.hookee_manager.fail("Plugin \"{}\" could not be found.".format(plugin_name))
        except HookeePluginValidationError as e:
            if throw_error:
                raise e

            self.hookee_manager.fail(str(e), e)

    def enabled_plugins(self):
        """
        Get a list of enabled plugins.

        :return: The list of enabled plugins.
        :rtype: list[str]
        """
        return list(str(p) for p in self.config.get("plugins"))

    def available_plugins(self):
        """
        Get a sorted list of available plugins.

        :return: The list of available plugins.
        :rtype: list[str]
        """
        return sorted([str(p) for p in self.source.list_plugins()])
