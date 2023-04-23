from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import PrintUtil

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "1.2.2"

plugin_type = REQUEST_PLUGIN
description = "Print the `request`'s body, if defined, and attempt to identify the body type."

print_util = None  # type: PrintUtil


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request):
    if request.is_json:
        print_util.print_basic("Body Type: JSON", color=print_util.request_color)
        print_util.print_dict("Body", dict(request.json), color=print_util.request_color)
    elif request.form and not request.data:
        print_util.print_basic("Body Type: FORM")
        print_util.print_dict("Body", dict(request.form), color=print_util.request_color)
    elif request.data:
        print_util.print_basic("Body: {}".format(request.data.decode("utf-8")), color=print_util.request_color)

    return request
