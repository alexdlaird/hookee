from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.1.0"

plugin_type = pluginmanager.REQUEST_PLUGIN
print_util = None


def setup(hookee_manager):
    global print_util

    print_util = hookee_manager.print_util


def run(request):
    if request.headers and "X-Forwarded-For" in request.headers:
        print_util.print_basic("Client IP: {}".format(request.headers.get("X-Forwarded-For")), fg="magenta")
    if request.headers:
        print_util.print_dict("Headers", dict(request.headers), fg="magenta")

    return request
