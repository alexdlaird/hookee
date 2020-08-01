import logging
import sys

from hookee.server import start_server
from hookee.tunnel import start_tunnel

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"

logger = logging.getLogger(__name__)


def main():
    """
    Entry point for the package's :code:`console_scripts`.

    TODO: At present, this is here as an example and POC, will be completely refactored and configurable in the near future
    """
    # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

    start_tunnel(port)

    start_server(port)


if __name__ == "__main__":
    main()
