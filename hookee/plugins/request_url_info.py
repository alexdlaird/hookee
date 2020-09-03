from datetime import datetime

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
    now = datetime.now()

    click.secho(
        "[{}] \"{} {} {}\"".format(now.isoformat(), request.method, request.base_url,
                                   request.environ["SERVER_PROTOCOL"]),
        fg="magenta", bold=True)
    click.echo("")

    return request
