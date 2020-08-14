import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


def call(request):
    # TODO: pretty this up further
    click.secho("Form Data: {}".format(dict(request.form)), fg="magenta")
    click.secho("Body: {}".format(request.data.decode("utf-8")), fg="magenta")
