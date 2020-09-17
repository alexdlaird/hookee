import inspect
import json
import logging
import os
import sys
import xml.dom.minidom

import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.1"

logger = logging.getLogger(__name__)


class PrintUtil:
    """
    An object that provides helpful methods for printing to the console through ``click`` and the CLI.

    :var config: The ``hookee`` configuration.
    :vartype config: Config
    """

    def __init__(self, config):
        self.config = config

    @property
    def console_width(self):
        return self.config.get("console_width")

    def print_config_update(self, msg):
        self.print_basic("\n--> {}\n".format(msg), fg="green")

    def print_open_header(self, title, delimiter="-", fg="green"):
        """
        Print an opening header to the CLI.

        :param title: The header title.
        :type title: str
        :param delimiter: The title of the XML blob.
        :type delimiter: str, optional
        :param fg: The color to make the text.
        :type fg: str, optional
        """
        width = int((self.console_width - len(title)) / 2)

        self.print_basic()
        self.print_basic("{}{}{}".format(delimiter * width, title, delimiter * width), fg=fg, bold=True)
        self.print_basic()

    def print_close_header(self, delimiter="-", fg="green", blank_line=True):
        """
        Print a closing header to the CLI.

        :param delimiter: The title of the XML blob.
        :type delimiter: str
        :param fg: The color to make the text.
        :type fg: str, optional
        :param blank_line: ``True`` if a blank line should preceed the closing header.
        :type blank_line: bool
        """
        if blank_line:
            self.print_basic()
        self.print_basic(delimiter * self.console_width, fg=fg, bold=True)

    def print_dict(self, title, data, fg="green"):
        """
        Print formatted dictionary data to the CLI.

        :param title: The title of the XML blob.
        :type title: str
        :param data: A dictionary.
        :type data: dict
        :param fg: The color to make the text.
        :type fg: str, optional
        """
        self.print_basic("{}: {}".format(title, json.dumps(data, indent=4)), fg=fg)

    def print_xml(self, title, data, fg="green"):
        """
        Print formatted XML to the CLI.

        :param title: The title of the XML blob.
        :type title: str
        :param data: An XML string.
        :type data: str
        :param fg: The color to make the text.
        :type fg: str, optional
        """
        self.print_basic("{}: {}".format(title, xml.dom.minidom.parseString(data).toprettyxml()), fg=fg)

    def print_basic(self, msg="", fg="white", bold=False, print_when_logging=False):
        """
        Print a status update in a boot sequence.

        :param msg: The update to print.
        :type msg: str, optional
        :param fg: The color to make the text.
        :type fg: str, optional
        :param bold: ``True`` if the output should be bold.
        :type bold: bool, optional
        :param print_when_logging: ``True`` if, when ``click_ctx`` is ``False``, ``msg`` should print to the console
            instead appended to the logger.
        :type print_when_logging: bool, optional
        """
        if self.config.click_logging:
            click.secho(msg, fg=fg, bold=bold)
        elif not print_when_logging:
            logger.info(msg)
        else:
            print(msg)


def python3_gte():
    """
    Check if running on a Python 3.x interpreter.

    :return: ``True`` if Python 3.
    :rtype: bool
    """
    return sys.version_info >= (3, 0)


def python36_gte():
    """
    Check if running on a Python 3.6 or higher interpreter.

    :return: ``True`` if Python 3.6 or higher.
    :rtype: bool
    """
    return sys.version_info >= (3, 6)


def get_functions(mod):
    """
    Get a list of functions for the given module.

    :param mod: The module to inspect for functions.
    :type mod: types.ModuleType
    :return: The list of functions.
    :rtype: list[types.FunctionType]
    """
    return [o[0] for o in inspect.getmembers(mod, inspect.isfunction)]


def get_args(func):
    """
    Get a list of args for the given function.

    :param func: The function to inspect for args.
    :type func: types.FunctionType
    :return: The list of args.
    :rtype: list[str]
    """
    if python3_gte():
        return inspect.getfullargspec(func)[0]
    else:
        return inspect.getargspec(func)[0]


def get_module_name(module):
    """
    Get the name of the module from the basename of its path.

    :param module: The module.
    :type module: types.ModuleType
    :return: The base name of the module.
    :rtype: str
    """
    return os.path.splitext(os.path.basename(module.__file__))[0]
