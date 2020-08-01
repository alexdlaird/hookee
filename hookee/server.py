import threading

from flask import Flask, request

from future.standard_library import install_aliases

install_aliases()

from urllib.request import urlopen, Request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"

app = Flask(__name__)

# Initialize our ngrok settings into Flask
app.config.from_mapping(
    ENV="development"
)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # TODO: make this pretty
    print(request.method)
    print(request.headers)
    print(request.args)
    print(request.query_string)
    print(request.data)
    print(request.form)

    # TODO: add support for plugins and other hooks, custom processing, responses, etc.

    return "{}"


def shutdown():
    request.environ.get("werkzeug.server.shutdown")()


@app.route("/shutdown", methods=("POST",))
def route_shutdown():
    shutdown()
    return "", 204


def start_server(port):
    # TODO: this needs to start a separate thread that is terminated at exit
    flask_kwargs = {"host": "127.0.0.1", "port": port, "debug": True, "use_reloader": False}
    threading.Thread(target=app.run, kwargs=flask_kwargs).start()


def stop_server():
    req = Request("http://127.0.0.1:5000/shutdown", method="POST")
    urlopen(req)
