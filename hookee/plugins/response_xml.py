from flask import current_app

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
    if not response:
        response = current_app.response_class(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>Ok</Response>",
            mimetype="application/xml",
        )

    return response
