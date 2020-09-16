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
    if request.is_json:
        print_util.print_basic("Body Type: JSON", fg="magenta")
        print_util.print_dict("Body", dict(request.json), fg="magenta")
    elif request.form and not request.data:
        print_util.print_basic("Body Type: FORM")
        print_util.print_dict("Body", dict(request.form), fg="magenta")
    elif request.data:
        print_util.print_basic("Body: {}".format(request.data.decode("utf-8")), fg="magenta")

    return request
