from datetime import datetime

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
    now = datetime.now()

    manager.print_util.print_close_header("=", fg="magenta")
    click.echo("")
    click.secho(
        "[{}] \"{} {} {}\"".format(now.isoformat(), request.method, request.base_url,
                                   request.environ["SERVER_PROTOCOL"]),
        fg="magenta")

    manager.print_util.print_open_header("Request", fg="magenta")

    return request
