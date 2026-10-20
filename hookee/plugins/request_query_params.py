__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from typing import TYPE_CHECKING

from flask import Request

from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import PrintUtil, multidict_to_dict  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = REQUEST_PLUGIN
description = "Print the `request`'s query parameters, if defined."

print_util = None  # type: PrintUtil


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util

    print_util = hookee_manager.print_util


def run(request: Request) -> Request:
    if request.args:
        print_util.print_dict("Query Params", multidict_to_dict(request.args), color=print_util.request_color)

    return request
