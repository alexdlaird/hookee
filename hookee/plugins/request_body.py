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
    if request.is_json:
        click.secho("Body Type: JSON", fg="magenta")
        click.secho("Body: {}".format(request.json), fg="magenta")
    elif request.form and not request.data:
        click.secho("Body Type: FORM")
        click.secho("Body: {}".format(dict(request.form)), fg="magenta")
    elif request.data:
        click.secho("Body: {}".format(dict(request.data)), fg="magenta")

    return request
