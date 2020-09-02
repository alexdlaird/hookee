import click

from hookee import util

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.4"

plugin_type = util.REQUEST_PLUGIN
manager = None


def setup(_manager):
    global manager

    manager = _manager


def run(request):
    # TODO: pretty this up further
    if request.headers and "X-Forwarded-For" in request.headers:
        click.secho("Client IP: {}".format(request.headers.get("X-Forwarded-For")), fg="magenta")
    if request.headers:
        click.secho("Headers: {}".format(dict(request.headers)), fg="magenta")

    return request
