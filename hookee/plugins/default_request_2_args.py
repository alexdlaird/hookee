import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


def call(request):
    # TODO: pretty this up further
    click.secho("Args: {}".format(dict(request.args)), fg="magenta")
