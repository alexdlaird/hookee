from hookee import pluginmanager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"

plugin_type = pluginmanager.REQUEST_PLUGIN
print_util = None


def setup(cli_manager):
    global print_util

    print_util = cli_manager.print_util


def run(request):
    if request.args:
        print_util.print_dict("Query Params", dict(request.args), fg="magenta")

    return request
