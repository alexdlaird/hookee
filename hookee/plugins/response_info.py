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
    print_util.print_basic("Status Code: {}".format(response.status_code), fg="magenta")
    if response.headers:
        print_util.print_dict("Headers", dict(response.headers), fg="magenta")
    if response.data:
        if response.is_json:
            print_util.print_dict("Body", response.get_json(), fg="magenta")
        else:
            print_util.print_basic("Body: {}".format(response.data.decode("utf-8")), fg="magenta")

    return response
