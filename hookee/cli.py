import logging

import click

from hookee.manager import Manager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.2"

logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=5000, help="The port for the local webserver.")
def hookee(port):
    """
    Entry point for the package's :code:`console_scripts` and the CLI.
    """
    manager = Manager.get_instance(port)
    manager.start()

    manager.wait_for_signal()

    manager.stop()


if __name__ == "__main__":
    hookee()
