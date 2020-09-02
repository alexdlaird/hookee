import click

from flask import Blueprint, request

from hookee import util

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.4"

blueprint = Blueprint("default", __name__)

plugin_type = util.BLUEPRINT_PLUGIN
manager = None


def setup(_manager):
    global manager

    manager = _manager


@blueprint.route("/webhook",
                 methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"])
def webhook():
    for plugin in manager.get_plugins_by_type(util.REQUEST_PLUGIN):
        plugin.run(request)

    manager.print_util.print_open_header("Response", fg="magenta")

    response = None
    for plugin in manager.get_plugins_by_type(util.RESPONSE_PLUGIN):
        response = plugin.run(request, response)

    manager.print_util.print_close_header("=", fg="magenta")
    click.echo("")

    return response


@blueprint.route("/status")
def status():
    return "", 200


@blueprint.route("/shutdown", methods=["POST"])
def shutdown():
    request.environ.get("werkzeug.server.shutdown")()

    return "", 204
