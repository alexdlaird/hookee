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
    if request.files:
        print_util.print_dict("Files", dict(request.files), fg="magenta")

    return request
