import click
from flask import current_app

from hookee import util

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"

plugin_type = util.RESPONSE_PLUGIN
print_util = None


def setup(cli_manager):
    global print_util

    print_util = cli_manager.print_util


def run(request, response):
    if not response:
        response = current_app.response_class(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>Ok</Response>",
            mimetype="application/xml",
        )

    click.secho("Status Code: {}".format(response.status_code), fg="magenta")
    if response.headers:
        print_util.print_dict("Headers", dict(response.headers), fg="magenta")
    if response.data:
        print_util.print_xml("Body", response.data.decode("utf-8"), fg="magenta")

    return response
