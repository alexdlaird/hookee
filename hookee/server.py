from flask import Flask, request

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"


def create_app():
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

    return app


def start_server(port):
    # TODO: this needs to start a separate thread that is terminated at exit
    app = create_app()

    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
