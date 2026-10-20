__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from typing import TYPE_CHECKING

from flask import Request

from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import PrintUtil, decode_body, is_xml, multidict_to_dict  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = REQUEST_PLUGIN
description = "Print the `request`'s body, if defined, and attempt to identify the body type."

print_util = None  # type: PrintUtil


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util

    print_util = hookee_manager.print_util


def run(request: Request) -> Request:
    json_body = request.get_json(silent=True) if request.is_json else None
    if json_body is not None:
        print_util.print_basic("Body Type: JSON", color=print_util.request_color)
        print_util.print_dict("Body", json_body, color=print_util.request_color)
    elif request.form:
        print_util.print_basic("Body Type: FORM")
        print_util.print_dict("Body", multidict_to_dict(request.form), color=print_util.request_color)
    elif request.data and not request.files:
        if is_xml(request.mimetype):
            print_util.print_basic("Body Type: XML", color=print_util.request_color)
            print_util.print_xml("Body", decode_body(request.data), color=print_util.request_color)
        else:
            print_util.print_basic(f"Body: {decode_body(request.data)}", color=print_util.request_color)

    return request
