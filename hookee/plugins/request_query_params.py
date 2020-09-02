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
    if request.args:
        click.secho("Query: {}".format(dict(request.args)), fg="magenta")

    return request
