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
    if request.is_json:
        click.secho("Body Type: JSON", fg="magenta")
        print_util.print_dict("Body", dict(request.json), fg="magenta")
    elif request.form and not request.data:
        click.secho("Body Type: FORM")
        print_util.print_dict("Body", dict(request.form), fg="magenta")
    elif request.data:
        click.secho("Body: {}".format(request.data.decode("utf-8")), fg="magenta")

    return request
