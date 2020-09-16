import json

from flask import current_app

from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.1.0"

plugin_type = pluginmanager.RESPONSE_PLUGIN
print_util = None


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request, response):
    if not response:
        data = ""
        content_type = request.headers.get("Content-Type")
        if request.form and not request.data:
            data = json.dumps(dict(request.form))
            content_type = "application/json"
        elif request.data:
            data = request.data.decode("utf-8")

        response = current_app.response_class(
            data,
            mimetype=content_type,
        )

    return response
