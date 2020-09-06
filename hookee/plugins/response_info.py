import click

from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"

plugin_type = pluginmanager.RESPONSE_PLUGIN
print_util = None


def setup(cli_manager):
    global print_util

    print_util = cli_manager.print_util


def run(request, response):
    click.secho("Status Code: {}".format(response.status_code), fg="magenta")
    if response.headers:
        print_util.print_dict("Headers", dict(response.headers), fg="magenta")
    if response.data:
        if response.is_json:
            print_util.print_dict("Body", response.get_json(), fg="magenta")
        else:
            click.secho("Body: {}".format(response.data.decode("utf-8")), fg="magenta")

    return response
