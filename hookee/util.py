import inspect
import json
import logging
import os
import sys

import click

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "2.0.8"

from defusedxml.minidom import parseString

logger = logging.getLogger(__name__)


class PrintUtil:
    """
    An object that provides helper methods for logging output. If :class:`~hookee.conf.Config`'s ``click_logging`` is
    ``True`` (which will happen by default if a :class:`click.Context` is found to be active), this logging will be
    done through ``click``, otherwise the ``hookee`` logger will be used.

    If ``click_logging`` is disabled, output sent through this utility can still be interacted with by ensuring the a
    logger is setup. For example, this would add a handler to the ``hookee`` logger that just logs output back to
    the console:

    .. code-block:: python

        import logging

        logger = logging.getLogger("hookee")
        logger.setLevel(logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())

    :var config: The ``hookee`` configuration.
    :vartype config: Config
    """

    def __init__(self, config):
        self.config = config

    @property
    def console_width(self):
        return self.config.get("console_width")

    @property
    def header_color(self):
        return self.config.get("header_color")

    @property
    def default_color(self):
        return self.config.get("default_color")

    @property
    def request_color(self):
        return self.config.get("request_color")

    def print_config_update(self, msg):
        self.print_basic("\n--> {}\n".format(msg), color=self.header_color)

    def print_open_header(self, title, delimiter="-", color=None):
        """
        Log an opening header with a title and a new line before and after.

        :param title: The header title.
        :type title: str
        :param delimiter: The title of the XML blob.
        :type delimiter: str, optional
        :param color: The color to make the text.
        :type color: str, optional
        """
        if color is None:
            color = self.header_color

        width = int((self.console_width - len(title)) / 2)

        self.print_basic()
        self.print_basic("{}{}{}".format(delimiter * width, title, delimiter * width), color=color, bold=True)
        self.print_basic()

    def print_close_header(self, delimiter="-", color=None, blank_line=True):
        """
        Log a closing header with an optional new line before.

        :param delimiter: The title of the XML blob.
        :type delimiter: str
        :param color: The color to make the text.
        :type color: str, optional
        :param blank_line: ``True`` if a blank line should precede the closing header.
        :type blank_line: bool
        """
        if color is None:
            color = self.header_color

        if blank_line:
            self.print_basic()
        self.print_basic(delimiter * self.console_width, color=color, bold=True)

    def print_dict(self, title, data, color=None):
        """
        Log formatted dictionary data.

        :param title: The title of the XML blob.
        :type title: str
        :param data: A dictionary.
        :type data: dict
        :param color: The color to make the text.
        :type color: str, optional
        """
        if color is None:
            color = self.default_color

        self.print_basic("{}: {}".format(title, json.dumps(data, indent=4)), color=color)

    def print_xml(self, title, data, color=None):
        """
        Log formatted XML.

        :param title: The title of the XML blob.
        :type title: str
        :param data: An XML string.
        :type data: str
        :param color: The color to make the text.
        :type color: str, optional
        """
        if color is None:
            color = self.default_color

        self.print_basic("{}: {}".format(title, parseString(data).toprettyxml()), color=color)

    def print_basic(self, msg="", color=None, bold=False, print_when_logging=False):
        """
        Log a basic message. The message will be logged via ``click``, if ``click_logging`` is enabled in
        :class:`~hookee.conf.Config`, or appended to the logger.

        :param msg: The update to print.
        :type msg: str, optional
        :param color: The color to make the text.
        :type color: str, optional
        :param bold: ``True`` if the output should be bold.
        :type bold: bool, optional
        :param print_when_logging: ``True`` if, when ``click_logging`` is ``False``, ``msg`` should print to the
            console instead of appending to the logger.
        :type print_when_logging: bool, optional
        """
        if color is None:
            color = self.default_color

        if self.config.click_logging:
            click.secho(msg, fg=color, bold=bold)
        elif not print_when_logging:
            logger.info(msg)
        else:
            print(msg)


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
    return inspect.getfullargspec(func)[0]


def get_module_name(module):
    """
    Get the name of the module from the basename of its path.

    :param module: The module.
    :type module: types.ModuleType
    :return: The base name of the module.
    :rtype: str
    """
    return os.path.splitext(os.path.basename(module.__file__))[0]
