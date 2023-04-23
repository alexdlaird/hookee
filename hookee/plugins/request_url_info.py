from datetime import datetime

from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import PrintUtil

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "1.2.2"

plugin_type = REQUEST_PLUGIN
description = "Print the timestamp along with the request URL and method being invoked."

print_util = None  # type: PrintUtil


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request):
    now = datetime.now()

    timestamp = now.strftime("%m-%d-%Y %I:%M:%S %p")

    print_util.print_basic("[{}] \"{} {} {}\"".format(timestamp, request.method, request.base_url,
                                                      request.environ["SERVER_PROTOCOL"]),
                           color=print_util.request_color, bold=True)
    print_util.print_basic()

    return request
