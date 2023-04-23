import json

from flask import current_app

from hookee.pluginmanager import RESPONSE_PLUGIN
from hookee.util import PrintUtil

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "1.2.2"

plugin_type = RESPONSE_PLUGIN
description = "If the `response` object has not been initialized, create a response that echo's back the request data."

print_util = None  # type: PrintUtil


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
