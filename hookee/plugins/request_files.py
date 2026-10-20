__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from typing import TYPE_CHECKING, Any, Dict

from flask import Request
from werkzeug.datastructures import FileStorage, MultiDict

from hookee.pluginmanager import REQUEST_PLUGIN
from hookee.util import PrintUtil, multidict_to_dict  # noqa: F401

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager

plugin_type = REQUEST_PLUGIN
description = "Print the `request`'s files, if defined."

print_util = None  # type: PrintUtil


def setup(hookee_manager: "HookeeManager") -> None:
    global print_util

    print_util = hookee_manager.print_util


def run(request: Request) -> Request:
    if request.files:
        files: MultiDict = MultiDict()
        for name, file in request.files.items(multi=True):
            files.add(name, _describe_file(file))
        print_util.print_dict("Files", multidict_to_dict(files), color=print_util.request_color)

    return request


def _describe_file(file: FileStorage) -> Dict[str, Any]:
    size = len(file.read())
    file.seek(0)

    return {"filename": file.filename, "content_type": file.content_type, "size": size}
