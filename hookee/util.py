import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.6"

BLUEPRINT_PLUGIN = "blueprint"
REQUEST_PLUGIN = "request"
RESPONSE_PLUGIN = "response"

VALID_PLUGIN_TYPES = [BLUEPRINT_PLUGIN, REQUEST_PLUGIN, RESPONSE_PLUGIN]


class PrintUtil:
    def __init__(self, config):
        self.config = config

    @property
    def console_width(self):
        return self.config.get("console_width")

    def print_config_update(self, msg):
        click.secho("\n--> {}\n".format(msg), fg="green")

    def print_hookee_banner(self):
        click.echo("")
        click.secho("=" * self.console_width, fg="green", bold=True)
        click.secho("""                .__                   __                  
                |  |__   ____   ____ |  | __ ____   ____  
                |  |  \ /  _ \ /  _ \|  |/ // __ \_/ __ \ 
                |   Y  (  <_> |  <_> )    <\  ___/\  ___/ 
                |___|  /\____/ \____/|__|_ \\___  >\___  >
                     \/                   \/    \/     \/ 
                                                   v{}""".format(__version__), fg="green", bold=True)
        click.secho("=" * self.console_width, fg="green", bold=True)

    def print_open_header(self, title, fg="green"):
        width = int((self.console_width - len(title)) / 2)

        click.echo("")
        click.secho("{}{}{}".format("-" * width, title, "-" * width), fg=fg, bold=True)
        click.echo("")

    def print_close_header(self, delimiter="-", fg="green"):
        click.secho(delimiter * self.console_width, fg=fg, bold=True)