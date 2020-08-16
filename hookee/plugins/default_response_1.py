import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"


def call(request, response=None):
    # TODO: pretty this up further
    click.secho("Status Code: {}".format(response.status_code), fg="magenta")
    if response.headers:
        click.secho("Headers: {}".format(dict(response.headers)), fg="magenta")
    if response.data:
        click.secho("Body: {}".format(response.data.decode("utf-8")), fg="magenta")

    return response
