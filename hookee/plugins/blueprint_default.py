import click

from flask import Blueprint, request

from hookee import util

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"

blueprint = Blueprint("default", __name__)

plugin_type = util.BLUEPRINT_PLUGIN
plugin_manager = None
print_util = None


def setup(cli_manager):
    global plugin_manager, print_util

    plugin_manager = cli_manager.plugin_manager
    print_util = cli_manager.print_util


@blueprint.route("/webhook",
                 methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"])
def webhook():
    print_util.print_close_header(delimiter="=", fg="magenta")
    print_util.print_open_header("Request", delimiter="-", fg="magenta")

    for plugin in plugin_manager.get_plugins_by_type(util.REQUEST_PLUGIN):
        plugin.run(request)
    if plugin_manager.last_request:
        plugin_manager.last_request.run(request)

    print_util.print_open_header("Response", fg="magenta")

    response = None
    for plugin in plugin_manager.get_plugins_by_type(util.RESPONSE_PLUGIN):
        response = plugin.run(request, response)
    if plugin_manager.last_response:
        response = plugin_manager.last_response.run(request, response)

    print_util.print_close_header("=", fg="magenta")
    click.echo("")

    return response


@blueprint.route("/status")
def status():
    return "", 200


@blueprint.route("/shutdown", methods=["POST"])
def shutdown():
    request.environ.get("werkzeug.server.shutdown")()

    return "", 204
