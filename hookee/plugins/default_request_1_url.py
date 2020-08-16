from datetime import datetime

import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"

from hookee import conf


def call(request):
    now = datetime.now()

    click.secho("=" * conf.CONSOLE_WIDTH, fg="magenta")
    click.echo("")
    click.secho(
        "[{}] \"{} {} {}\"".format(now.isoformat(), request.method, request.base_url,
                                   request.environ["SERVER_PROTOCOL"]),
        fg="magenta", bold=True)

    title = "Request"
    width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

    click.echo("")
    click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="magenta", bold=True)
    click.echo("")

    return request
