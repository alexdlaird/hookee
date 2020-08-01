import logging
import os
import sys

from flask import Flask, request
from pyngrok import ngrok

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.0.0"

logger = logging.getLogger(__name__)


def main():
    """
    Entry point for the package's :code:`console_scripts`.

    TODO: At present, this is here as an example and POC, will be completely refactored and configurable in the near future
    """
    app = Flask(__name__)

    # Initialize our ngrok settings into Flask
    app.config.from_mapping(
        ENV="development",
        START_NGROK=os.environ.get("WERKZEUG_RUN_MAIN") != "true"
    )

    if app.config["START_NGROK"]:
        # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port)
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))

        @app.route("/webhook", methods=["GET", "POST"])
        def hello():
            print(request.method)
            print(request.headers)
            print(request.args)
            print(request.query_string)
            print(request.data)
            print(request.form)

            return "{}"

        app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
