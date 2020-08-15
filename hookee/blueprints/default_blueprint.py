import importlib
import pkgutil
from datetime import datetime

import click

import hookee.plugins

from flask import Blueprint, request, Response, jsonify
from hookee import conf

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"

blueprint = Blueprint("default", __name__)

plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules(hookee.plugins.__path__, hookee.plugins.__name__ + ".")
}


@blueprint.route("/webhook",
                 methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"])
def webhook():
    now = datetime.now()

    click.secho("=" * conf.CONSOLE_WIDTH, fg="magenta")
    click.echo("")
    click.secho(
        "[{}] \"{} {} {}\"".format(now.isoformat(), request.method, request.base_url,
                                   request.environ["SERVER_PROTOCOL"]),
        fg="magenta", bold=True)

    title = "Request"
    width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

    click.echo("")
    click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="magenta", bold=True)
    click.echo("")

    # TODO: will refactor this to support a real plugin arch after POC
    for name in filter(lambda n: n.startswith("hookee.plugins.default_request"), plugins.keys()):
        plugins[name].call(request)

    title = "Response"
    width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

    click.echo("")
    click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="magenta", bold=True)
    click.echo("")

    response = jsonify({})
    for name in filter(lambda n: n.startswith("hookee.plugins.default_response"), plugins.keys()):
        plugins[name].call(request, response)

    click.echo("")
    click.secho("=" * conf.CONSOLE_WIDTH, fg="magenta")
    click.echo("")

    return response


@blueprint.route("/status")
def status():
    return "", 200


@blueprint.route("/shutdown", methods=["POST"])
def shutdown():
    request.environ.get("werkzeug.server.shutdown")()

    return "", 204
