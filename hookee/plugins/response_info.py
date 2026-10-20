__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from typing import TYPE_CHECKING

from flask import Request, Response

from hookee.conf import Config  # noqa: F401
from hookee.pluginmanager import RESPONSE_PLUGIN
from hookee.util import PrintUtil, decode_body, is_xml, mask_sensitive_headers  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = RESPONSE_PLUGIN
description = "Print the `response`'s status code, headers, and body, if defined."

print_util = None  # type: PrintUtil
config = None  # type: Config


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util, config

    print_util = hookee_manager.print_util
    config = hookee_manager.config


def run(request: Request, response: Response) -> Response:
    print_util.print_basic(f"Status Code: {response.status_code}", color=print_util.request_color)
    headers = dict(response.headers)
    if not config.get("show_sensitive_headers"):
        headers = mask_sensitive_headers(headers)
    if headers:
        print_util.print_dict("Headers", headers, color=print_util.request_color)
    if response.is_streamed:
        print_util.print_basic("Body: <streamed, shown below as it arrives>", color=print_util.request_color)
    elif response.data:
        json_body = response.get_json(silent=True) if response.is_json else None
        if json_body is not None:
            print_util.print_dict("Body", json_body, color=print_util.request_color)
        elif is_xml(response.mimetype):
            print_util.print_xml("Body", decode_body(response.data), color=print_util.request_color)
        else:
            print_util.print_basic(f"Body: {decode_body(response.data)}", color=print_util.request_color)

    return response
