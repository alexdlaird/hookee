__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from typing import TYPE_CHECKING

from flask import Request

from hookee.conf import Config  # noqa: F401
from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import WEBHOOK_VERIFIED_HEADER, PrintUtil, mask_sensitive_headers  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = REQUEST_PLUGIN
description = "Print the `request`'s headers, if defined."

print_util = None  # type: PrintUtil
config = None  # type: Config


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util, config

    print_util = hookee_manager.print_util
    config = hookee_manager.config


def run(request: Request) -> Request:
    if request.headers and "X-Forwarded-For" in request.headers:
        print_util.print_basic(f"Client IP: {request.headers.get('X-Forwarded-For')}",
                               color=print_util.request_color)
    headers = dict(request.headers)
    if config.get("verify_webhook") and not config.get("no_tunnel"):
        verified = "Yes" if request.headers.get(WEBHOOK_VERIFIED_HEADER) == "true" else "No"
        print_util.print_basic(f"Webhook Verified: {verified}", color=print_util.request_color)
        headers = {name: value for name, value in headers.items() if name.lower() != WEBHOOK_VERIFIED_HEADER.lower()}
    if not config.get("show_sensitive_headers"):
        headers = mask_sensitive_headers(headers)
    if headers:
        print_util.print_dict("Headers", headers, color=print_util.request_color)

    return request
