import logging

import click

from hookee import conf
from hookee.manager import Manager

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.3"

logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=5000, help="The port for the local webserver.")
def hookee(port):
    """
    Entry point for the package's :code:`console_scripts` and the CLI.
    """
    _banner()

    manager = Manager.get_instance(port)
    manager.start()

    manager.wait_for_signal()

    manager.stop()


def _banner():
    click.echo("")
    click.secho("=" * conf.CONSOLE_WIDTH, fg="red", bold=True)
    click.secho("""                .__                   __                  
                |  |__   ____   ____ |  | __ ____   ____  
                |  |  \ /  _ \ /  _ \|  |/ // __ \_/ __ \ 
                |   Y  (  <_> |  <_> )    <\  ___/\  ___/ 
                |___|  /\____/ \____/|__|_ \\___  >\___  >
                     \/                   \/    \/     \/ 
                                                   v{}""".format(__version__), fg="red", bold=True)
    click.secho("=" * conf.CONSOLE_WIDTH, fg="red", bold=True)


if __name__ == "__main__":
    hookee()
