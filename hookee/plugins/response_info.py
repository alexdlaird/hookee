__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from hookee.pluginmanager import RESPONSE_PLUGIN
from hookee.util import PrintUtil  # noqa: F401

plugin_type = RESPONSE_PLUGIN
description = "Print the `response`'s status code, headers, and body, if defined."

print_util = None  # type: PrintUtil


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request, response):
    print_util.print_basic(f"Status Code: {response.status_code}", color=print_util.request_color)
    if response.headers:
        print_util.print_dict("Headers", dict(response.headers), color=print_util.request_color)
    if response.data:
        if response.is_json:
            print_util.print_dict("Body", response.get_json(), color=print_util.request_color)
        else:
            print_util.print_basic(f"Body: {response.data.decode('utf-8')}", color=print_util.request_color)

    return response
