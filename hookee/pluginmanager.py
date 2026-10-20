__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import importlib.util
import mimetypes
import os
import re
import time
import urllib.request
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Iterator, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

from flask import Blueprint, Request, Response, current_app
from pluginbase import PluginBase, PluginSource

from hookee import util
from hookee.conf import Config
from hookee.exception import HookeePluginValidationError

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

BLUEPRINT_PLUGIN = "blueprint"
REQUEST_PLUGIN = "request"
RESPONSE_PLUGIN = "response"

VALID_PLUGIN_TYPES = [BLUEPRINT_PLUGIN, REQUEST_PLUGIN, RESPONSE_PLUGIN]
REQUIRED_PLUGINS = ["blueprint_default"]

LOCAL_HOSTNAMES = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
STREAM_CHUNK_SIZE = 64 * 1024

_HOP_BY_HOP_HEADERS = ["connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers",
                       "transfer-encoding", "upgrade", "content-length"]


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


_forward_opener = build_opener(ProxyHandler({}), _NoRedirectHandler)


class Plugin:
    """
    An object that represents a validated and loaded ``hookee`` plugin.
    """

    def __init__(self,
                 module: ModuleType,
                 plugin_type: str,
                 name: str,
                 has_setup: bool,
                 description: Optional[str] = None) -> None:
        #: The underlying plugin module.
        self.module: ModuleType = module

        #: The type of plugin.
        self.plugin_type: str = plugin_type
        #: The name of the plugin.
        self.name: str = name
        #: ``True`` if the plugin has a ``setup(hookee_manager)`` method.
        self.has_setup: bool = has_setup
        #: The description of the plugin.
        self.description: Optional[str] = description

        if self.plugin_type == BLUEPRINT_PLUGIN:
            self.blueprint: Blueprint = self.module.blueprint

    def setup(self, *args: Any) -> Any:
        """
        Passes through to the underlying module's ``setup(*args)``, if it exists.

        :param args: The args to pass through.
        :return: The value returned by the module's function (or nothing if the module's function returns nothing).
        """
        if self.has_setup:
            return self.module.setup(*args)

    def run(self, *args: Any) -> Any:
        """
        Passes through to the underlying module's ``run(*args)``.

        :param args: The args to pass through.
        :return: The value returned by the module's function (or nothing if the module's function returns nothing).
        """
        return self.module.run(*args)

    @staticmethod
    def build_from_module(module: ModuleType) -> "Plugin":
        """
        Validate and build a ``hookee`` plugin for the given module. If the module is not a valid ``hookee`` plugin,
        an exception will be thrown.

        :param module: The module to validate as a valid plugin.
        :return: An object representing the validated plugin.
        """
        name = util.get_module_name(module)

        functions_list = util.get_functions(module)
        attributes = dir(module)

        if "plugin_type" not in attributes:
            raise HookeePluginValidationError(
                f"Plugin \"{name}\" does not conform to the plugin spec.")
        elif module.plugin_type not in VALID_PLUGIN_TYPES:
            raise HookeePluginValidationError(
                f"Plugin \"{name}\" must specify a valid `plugin_type`.")
        elif module.plugin_type == REQUEST_PLUGIN:
            if "run" not in functions_list:
                raise HookeePluginValidationError(
                    f"Plugin \"{name}\" must implement `run(request)`.")
            elif len(util.get_args(module.run)) < 1:
                raise HookeePluginValidationError(
                    f"Plugin \"{name}\" does not conform to the plugin spec, `run(request)` must be defined.")
        elif module.plugin_type == RESPONSE_PLUGIN:
            if "run" not in functions_list:
                raise HookeePluginValidationError(
                    f"Plugin \"{name}\" must implement `run(request, response)`.")
            elif len(util.get_args(module.run)) < 2:
                raise HookeePluginValidationError(
                    f"Plugin \"{name}\" does not conform to the plugin spec, `run(request, response)` "
                    f"must be defined.")
        elif module.plugin_type == BLUEPRINT_PLUGIN and "blueprint" not in attributes:
            raise HookeePluginValidationError(
                f"Plugin \"{name}\" must define `blueprint = Blueprint(\"plugin_name\", __name__)`.")

        has_setup = "setup" in functions_list and len(util.get_args(module.setup)) == 1

        return Plugin(module, module.plugin_type, name, has_setup, getattr(module, "description", None))

    @staticmethod
    def build_from_file(path: str) -> "Plugin":
        """
        Import a Python script at the given path, then import it as a ``hookee`` plugin.

        :param path: The path to the script to import.
        :return: The imported script as a plugin.
        """
        module_name = os.path.splitext(os.path.basename(path))[0]

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return Plugin.build_from_module(module)


class PluginManager:
    """
    An object that loads, validates, and manages available plugins.
    """

    def __init__(self, hookee_manager: "HookeeManager") -> None:
        #: Reference to the ``hookee`` Manager.
        self.hookee_manager: "HookeeManager" = hookee_manager
        #: The ``hookee`` configuration.
        self.config: Config = self.hookee_manager.config

        #: The source that plugins are loaded from.
        self.source: Optional[PluginSource] = None
        #: The response callback generated from either ``--response`` or ``--response-file``, or the function
        #: defined in the config's ``response_callback``. Overrides any body data from response plugins.
        self.response_callback: Optional[Callable] = None
        #: The headers given with ``--response-header`` to set on every response.
        self.response_headers: List[Tuple[str, str]] = []
        #: The regex given with ``--response-route`` for the requests to apply response options to.
        self.response_route: Optional[re.Pattern] = None

        #: The directory where built-in plugins reside.
        self.builtin_plugins_dir: str = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                      "plugins"))

        #: A list of plugins that have been validated and imported.
        self.loaded_plugins: List[Plugin] = []

        self.source_plugins()

    def source_plugins(self) -> None:
        """
        Source all paths to look for plugins (defined in the config) to prepare them for loading and validation.
        """
        plugins_dir = self.config.get("plugins_dir")

        plugin_base = PluginBase(package="hookee.plugins",
                                 searchpath=[self.builtin_plugins_dir])
        self.source = plugin_base.make_plugin_source(searchpath=[plugins_dir])

    def load_plugins(self) -> None:
        """
        Load and validate all built-in plugins and custom plugins from sources in the plugin base.
        """
        enabled_plugins = self.enabled_plugins()

        for plugin_name in REQUIRED_PLUGINS:
            if plugin_name not in enabled_plugins:
                self.hookee_manager.fail(
                    f"Sorry, the plugin {plugin_name} is required. Run `hookee enable-plugin {plugin_name}` "
                    f"before continuing.")

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
        response_file = self.config.get("response_file")
        response_content_type = self.config.get("content_type")

        if response_body and response_file:
            self.hookee_manager.fail("`--response` and `--response-file` cannot both be given.")
        if response_content_type and not (response_body or response_file):
            self.hookee_manager.fail("If `--content-type` is given, `--response` or `--response-file` must also be "
                                     "given.")
        forward_to = self.config.get("forward_to")
        if forward_to and (response_body or response_file):
            self.hookee_manager.fail("`--forward-to` cannot be combined with `--response` or `--response-file`.")
        if forward_to and urlsplit(forward_to).username is not None:
            self.hookee_manager.fail("`--forward-to` cannot include credentials in its URL.")
        if forward_to and self._forwards_to_itself(forward_to):
            self.hookee_manager.fail(f"`--forward-to` cannot point at hookee itself, which is using port "
                                     f"{self.config.get('port')}. Start hookee on a different port with `--port`.")

        if response_file:
            with open(response_file, "rb") as f:
                response_body = f.read()
            if not response_content_type:
                response_content_type = mimetypes.guess_type(response_file)[0]

        self.response_headers = self._parse_response_headers()
        self.response_route = self._compile_response_route()

        self.response_callback = self.config.response_callback

        if self.response_callback and response_body:
            self.hookee_manager.fail("If `response_callback` is given, `response` cannot also be given.")
        elif response_body and not self.response_callback:
            def response_callback(request: Request, response: Response) -> Response:
                if not self._matches_response_route(request):
                    return response

                response.data = response_body
                response.headers[
                    "Content-Type"] = response_content_type if response_content_type else "text/plain"
                return response

            self.response_callback = response_callback

        if len(self.get_plugins_by_type(RESPONSE_PLUGIN)) == 0 and not self.response_callback:
            self.hookee_manager.fail(
                "No response plugin was loaded. Enable a plugin like `response_echo`, or pass `--response` "
                "or `--response-script`.")

    def get_plugins_by_type(self, plugin_type: str) -> List[Plugin]:
        """
        Get loaded plugins by the given plugin type.

        :param plugin_type: The plugin type for filtering.
        :return: The filtered list of plugins.
        """
        return list(filter(lambda p: p.plugin_type == plugin_type, self.loaded_plugins))

    def _forwards_to_itself(self, forward_to: str) -> bool:
        forward_to_url = urlsplit(forward_to)
        port = forward_to_url.port or (443 if forward_to_url.scheme == "https" else 80)

        return forward_to_url.hostname in LOCAL_HOSTNAMES and port == self.config.get("port")

    def _parse_response_headers(self) -> List[Tuple[str, str]]:
        response_headers = []
        for header in self.config.get("response_headers"):
            name, separator, value = header.partition(":")
            if not separator or not name.strip():
                self.hookee_manager.fail(f"`--response-header` must be given as \"Name: value\", not \"{header}\".")
            response_headers.append((name.strip(), value.strip()))

        return response_headers

    def _compile_response_route(self) -> Optional[re.Pattern]:
        response_route = self.config.get("response_route")
        if not response_route:
            return None

        try:
            return re.compile(response_route)
        except re.error as e:
            self.hookee_manager.fail(f"`--response-route` is not a valid regex: {e}")

    def run_request_plugins(self, request: Request) -> Request:
        """
        Run all enabled request plugins.

        :param request: The request object being processed.
        :return: The processed request.
        """
        for plugin in self.get_plugins_by_type(REQUEST_PLUGIN):
            request = plugin.run(request)

        return request

    def run_response_plugins(self,
                             request: Optional[Request] = None,
                             response: Optional[Response] = None) -> Response:
        """
        Run all enabled response plugins, running the ``response_info`` plugin (if enabled) last.

        :param request: The request object being processed.
        :param response: The response object being processed.
        :return: The processed response.
        """
        if response is None and request is not None and self.config.get("forward_to"):
            response = self._forward_request(request)

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

        response = self._apply_response_options(request, response)

        if response_info_plugin:
            response = response_info_plugin.run(request, response)

        return response

    def get_plugin(self,
                   plugin_name: str,
                   throw_error: bool = False) -> Plugin:
        """
        Get the given plugin name from modules parsed by :func:`~hookee.pluginmanager.PluginManager.source_plugins`.

        :param plugin_name: The name of the plugin to load.
        :param throw_error: ``True`` if errors encountered should be thrown to the caller, ``False`` if
            :func:`~hookee.hookeemanager.HookeeManager.fail` should be called.
        :return: The loaded plugin.
        """
        try:
            return Plugin.build_from_module(self.source.load_plugin(plugin_name))
        except ImportError as e:
            if throw_error:
                raise e

            self.hookee_manager.fail(f"Plugin \"{plugin_name}\" could not be found.")
        except HookeePluginValidationError as e:
            if throw_error:
                raise e

            self.hookee_manager.fail(str(e), e)

    def enabled_plugins(self) -> List[str]:
        """
        Get a list of enabled plugins.

        :return: The list of enabled plugins.
        """
        return list(str(p) for p in self.config.get("plugins"))

    def available_plugins(self) -> List[str]:
        """
        Get a sorted list of available plugins.

        :return: The list of available plugins.
        """
        return sorted([str(p) for p in self.source.list_plugins()])

    def _forward_request(self, request: Request) -> Response:
        print_util = self.hookee_manager.print_util

        url = self._build_forward_url(request)
        if url is None:
            print_util.print_basic("hookee only forwards requests for a path, so this request was not forwarded.",
                                   color=print_util.request_color)
            return current_app.response_class("Bad Request", status=400, mimetype="text/plain")

        headers = {name: value for name, value in request.headers.items() if name.lower() not in _HOP_BY_HOP_HEADERS}
        forward = urllib.request.Request(url, data=request.get_data() or None, headers=headers, method=request.method)

        print_util.print_basic(f"Forwarded To: {url}", color=print_util.request_color)

        try:
            upstream = _forward_opener.open(forward)
        except HTTPError as e:
            upstream = e
        except URLError as e:
            print_util.print_basic(f"hookee could not forward the request to {url}: {e.reason}",
                                   color=print_util.request_color)
            return current_app.response_class("Bad Gateway", status=502, mimetype="text/plain")

        response_headers = [(name, value) for name, value in upstream.headers.items()
                            if name.lower() not in _HOP_BY_HOP_HEADERS]

        if upstream.headers.get("Content-Length") is None:
            return current_app.response_class(self._stream_body(upstream), status=upstream.status,
                                              headers=response_headers)

        with upstream:
            body = upstream.read()

        return current_app.response_class(body, status=upstream.status, headers=response_headers)

    def _build_forward_url(self, request: Request) -> Optional[str]:
        # The raw URI is forwarded as it was received, since Flask's path has already been decoded
        request_uri = request.environ.get("RAW_URI", request.full_path.rstrip("?"))
        forward_to = self.config.get("forward_to").rstrip("/")
        url = f"{forward_to}{request_uri}"

        # A request target that isn't a path, like "@evil.com/", must not be able to change where it's forwarded
        if not request_uri.startswith("/") or urlsplit(url).netloc != urlsplit(forward_to).netloc:
            return None

        return url

    def _stream_body(self, upstream: Any) -> Iterator[bytes]:
        print_util = self.hookee_manager.print_util

        with upstream:
            while chunk := upstream.read1(STREAM_CHUNK_SIZE):
                print_util.print_basic(f"Streamed: {util.decode_body(chunk).rstrip()}", color=print_util.request_color)
                yield chunk

    def _apply_response_options(self, request: Optional[Request], response: Response) -> Response:
        if not self._matches_response_route(request):
            return response

        status_code = self.config.get("status_code")
        if status_code:
            response.status_code = status_code
        for name, value in self.response_headers:
            response.headers[name] = value

        delay = self.config.get("delay")
        if delay:
            time.sleep(delay)

        return response

    def _matches_response_route(self, request: Optional[Request]) -> bool:
        if self.response_route is None:
            return True
        if request is None:
            return False

        return self.response_route.search(f"{request.method} {request.path}") is not None
