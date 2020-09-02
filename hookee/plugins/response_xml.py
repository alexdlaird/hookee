import click
from flask import jsonify, Response, current_app

from hookee import util

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.4"

plugin_type = util.RESPONSE_PLUGIN
manager = None


def setup(_manager):
    global manager

    manager = _manager


def run(request, response):
    if not response:
        response = current_app.response_class(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>Ok</Response>",
            mimetype="application/xml",
        )

    # TODO: pretty this up further
    click.secho("Status Code: {}".format(response.status_code), fg="magenta")
    if response.headers:
        click.secho("Headers: {}".format(dict(response.headers)), fg="magenta")
    if response.data:
        click.secho("Body: {}".format(response.data.decode("utf-8")), fg="magenta")

    return response
