from flask import Blueprint, request

from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.1.0"

blueprint = Blueprint("default", __name__)

plugin_type = pluginmanager.BLUEPRINT_PLUGIN
plugin_manager = None
print_util = None


def setup(hookee_manager):
    global plugin_manager, print_util

    plugin_manager = hookee_manager.plugin_manager
    print_util = hookee_manager.print_util


@blueprint.route("/webhook",
                 methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"])
def webhook():
    print_util.print_close_header(delimiter="=", fg="magenta")

    print_util.print_open_header("Request", delimiter="-", fg="magenta")

    plugin_manager.run_request_plugins(request)

    print_util.print_open_header("Response", fg="magenta")

    response = plugin_manager.run_response_plugins(request)

    print_util.print_close_header("=", fg="magenta")
    print_util.print_basic()

    return response


@blueprint.route("/status")
def status():
    return "", 200


@blueprint.route("/shutdown", methods=["POST"])
def shutdown():
    request.environ.get("werkzeug.server.shutdown")()

    return "", 204
