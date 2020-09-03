import click

from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"

plugin_type = pluginmanager.REQUEST_PLUGIN
print_util = None


def setup(cli_manager):
    global print_util

    print_util = cli_manager.print_util


def run(request):
    if request.headers and "X-Forwarded-For" in request.headers:
        click.secho("Client IP: {}".format(request.headers.get("X-Forwarded-For")), fg="magenta")
    if request.headers:
        print_util.print_dict("Headers", dict(request.headers), fg="magenta")

    return request
