__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import json
from typing import TYPE_CHECKING, Optional, Union

from flask import current_app, Request, Response

from hookee.pluginmanager import RESPONSE_PLUGIN
from hookee.util import PrintUtil, multidict_to_dict  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = RESPONSE_PLUGIN
description = "If the `response` object has not been initialized, create a response that echo's back the request data."

print_util = None  # type: PrintUtil


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util

    print_util = hookee_manager.print_util


def run(request: Request, response: Optional[Response]) -> Response:
    if not response:
        data: Union[str, bytes] = ""
        content_type = request.headers.get("Content-Type")
        if request.form:
            data = json.dumps(multidict_to_dict(request.form))
            content_type = "application/json"
        elif request.data:
            data = request.data

        response = current_app.response_class(
            data,
            mimetype=content_type,
        )

    return response
