import inspect
import json
import sys
import xml.dom.minidom

import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"


class PrintUtil:
    """
    An object that provides helpful methods for printing to the console through ``click`` CLI.

    :var config: The ``hookee`` configuration.
    :vartype config: Config
    """

    def __init__(self, config):
        self.config = config

    @property
    def console_width(self):
        return self.config.get("console_width")

    def print_config_update(self, msg):
        click.secho("\n--> {}\n".format(msg), fg="green")

    def print_open_header(self, title, delimiter="-", fg="green"):
        """
        Print an opening header to the CLI.

        :param delimiter: The title of the XML blob.
        :type delimiter: str
        :param fg: The color to make the text.
        :type fg: str
        """
        width = int((self.console_width - len(title)) / 2)

        click.echo("")
        click.secho("{}{}{}".format(delimiter * width, title, delimiter * width), fg=fg, bold=True)
        click.echo("")

    def print_close_header(self, delimiter="-", fg="green"):
        """
        Print a closing header to the CLI.

        :param delimiter: The title of the XML blob.
        :type delimiter: str
        :param fg: The color to make the text.
        :type fg: str
        """
        click.secho(delimiter * self.console_width, fg=fg, bold=True)

    def print_dict(self, title, data, fg="green"):
        """
        Print formatted dictionary data to the CLI.

        :param title: The title of the XML blob.
        :type title: str
        :param data: A dictionary.
        :type data: dict
        :param fg: The color to make the text.
        :type fg: str
        """
        click.secho("{}: {}".format(title, json.dumps(data, indent=4)), fg=fg)

    def print_xml(self, title, data, fg="green"):
        """
        Print formatted XML to the CLI.

        :param title: The title of the XML blob.
        :type title: str
        :param data: An XML string.
        :type data: str
        :param fg: The color to make the text.
        :type fg: str
        """
        click.secho("{}: {}".format(title, xml.dom.minidom.parseString(data).toprettyxml()), fg=fg)


def python3_gte():
    """
    Check if running on a Python 3.x interpreter.

    :return: True if Python 3, False otherwise.
    :rtype: bool
    """
    return sys.version_info >= (3, 0)


def python36_gte():
    """
    Check if running on a Python 3.6 or higher interpreter.

    :return: True if Python 3.6 or higher, False otherwise.
    :rtype: bool
    """
    return sys.version_info >= (3, 6)


def get_functions(mod):
    """
    Get a list of functions for the given module.

    :param mod: The module to inspect for functions.
    :type mod: module
    :return: The list of functions.
    :rtype: list[function]
    """
    return [o[0] for o in inspect.getmembers(mod, inspect.isfunction)]


def get_args(func):
    """
    Get a list of args for the given function.

    :param func: The function to inspect for args.
    :type func: function
    :return: The list of args.
    :rtype: list[str]
    """
    if python3_gte():
        return inspect.getfullargspec(func)[0]
    else:
        return inspect.getargspec(func)[0]
