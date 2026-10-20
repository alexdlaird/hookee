__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import re
from typing import TYPE_CHECKING, Optional, Tuple

from flask import Blueprint, Response, abort, request

from hookee.conf import Config  # noqa: F401
from hookee.pluginmanager import BLUEPRINT_PLUGIN, PluginManager  # noqa: F401
from hookee.util import PrintUtil, save_request  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

WEBHOOK_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"]

blueprint = Blueprint("default", __name__)
plugin_type = BLUEPRINT_PLUGIN
description = ("Mount the required `/status` endpoint along with the default `/webhook` endpoint that processes "
               "incoming requests with enabled plugins.")

plugin_manager = None  # type: PluginManager
print_util = None  # type: PrintUtil
config = None  # type: Config


def setup(hookee_manager: "HookeeManager") -> None:
    global plugin_manager, print_util, config

    plugin_manager = hookee_manager.plugin_manager
    print_util = hookee_manager.print_util
    config = hookee_manager.config


@blueprint.route("/", defaults={"uri": ""}, methods=WEBHOOK_METHODS)
@blueprint.route("/<path:uri>", methods=WEBHOOK_METHODS)
def webhook(uri: str) -> Response:
    if not config.get("forward_to") and not _matches_default_route(uri):
        abort(404)

    print_util.print_close_header(delimiter="=", color=print_util.request_color)

    print_util.print_open_header("Request", delimiter="-", color=print_util.request_color)

    # Read the raw body before plugins parse it as a form, which would otherwise consume it
    request.get_data()

    plugin_manager.run_request_plugins(request)

    print_util.print_open_header("Response", color=print_util.request_color)

    response = plugin_manager.run_response_plugins(request)

    save_dir = config.get("save_dir")
    if save_dir:
        path = save_request(request, response, save_dir, config.get("show_sensitive_headers"))
        print_util.print_basic(f"Saved To: {path}", color=print_util.request_color)

    print_util.print_close_header("=", color=print_util.request_color)
    print_util.print_basic()

    return response


def _matches_default_route(uri: str) -> Optional[re.Match]:
    route = f"/{uri.rstrip('/')}"

    return (re.compile(config.get("default_route_methods")).match(request.method) and
            re.compile(config.get("default_route")).match(route))


@blueprint.route("/status")
def status() -> Tuple[str, int]:
    return "", 200
