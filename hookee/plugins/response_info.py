from hookee.pluginmanager import RESPONSE_PLUGIN
from hookee.util import PrintUtil

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "1.2.2"

plugin_type = RESPONSE_PLUGIN
description = "Print the `response`'s status code, headers, and body, if defined."

print_util = None  # type: PrintUtil


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request, response):
    print_util.print_basic("Status Code: {}".format(response.status_code), color=print_util.request_color)
    if response.headers:
        print_util.print_dict("Headers", dict(response.headers), color=print_util.request_color)
    if response.data:
        if response.is_json:
            print_util.print_dict("Body", response.get_json(), color=print_util.request_color)
        else:
            print_util.print_basic("Body: {}".format(response.data.decode("utf-8")), color=print_util.request_color)

    return response
