import importlib
import pkgutil
import hookee.plugins

from flask import Blueprint, request, Response

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.2"

blueprint = Blueprint("default", __name__)

plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules(hookee.plugins.__path__, hookee.plugins.__name__ + ".")
}


@blueprint.route("/webhook",
                 methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"])
def webhook():
    print("--- Request ---")
    # TODO: will refactor this to support a real plugin arch after POC
    for name in filter(lambda n: n.startswith("hookee.plugins.default_request"), plugins.keys()):
        plugins[name].call(request)

    print("\n--- Response ---")

    response = Response()
    for name in filter(lambda n: n.startswith("hookee.plugins.default_response"), plugins.keys()):
        plugins[name].call(request, response)

    print("\n{}\n".format("-" * 70))

    return response


@blueprint.route("/status")
def status():
    return "", 200


@blueprint.route("/shutdown", methods=["POST"])
def shutdown():
    request.environ.get("werkzeug.server.shutdown")()

    return "", 204
