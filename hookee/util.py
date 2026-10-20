__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

import base64
import inspect
import json
import logging
import os
import uuid
from datetime import datetime
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union
from xml.parsers.expat import ExpatError

import click
from defusedxml import DefusedXmlException
from defusedxml.minidom import parseString
from flask import Request, Response
from werkzeug.datastructures import MultiDict

from hookee.conf import Config

logger = logging.getLogger(__name__)

#: The header ``ngrok`` sets with the result of verifying a webhook's signature, when ``verify_webhook`` is given.
WEBHOOK_VERIFIED_HEADER = "X-Hookee-Webhook-Verified"

AUTHORIZATION_HEADERS = ["authorization", "proxy-authorization"]
COOKIE_HEADERS = ["cookie", "set-cookie"]
MASK = "<masked>"


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
    """

    def __init__(self, config: Config) -> None:
        #: The ``hookee`` configuration.
        self.config: Config = config

    @property
    def console_width(self) -> int:
        return self.config.get("console_width")

    @property
    def header_color(self) -> str:
        return self.config.get("header_color")

    @property
    def default_color(self) -> str:
        return self.config.get("default_color")

    @property
    def request_color(self) -> str:
        return self.config.get("request_color")

    def print_config_update(self, msg: str) -> None:
        self.print_basic(f"\n--> {msg}\n", color=self.header_color)

    def print_open_header(self,
                          title: str,
                          delimiter: str = "-",
                          color: Optional[str] = None) -> None:
        """
        Log an opening header with a title and a new line before and after.

        :param title: The header title.
        :param delimiter: The character to draw the header with.
        :param color: The color to make the text.
        """
        if color is None:
            color = self.header_color

        width = int((self.console_width - len(title)) / 2)

        self.print_basic()
        self.print_basic(f"{delimiter * width}{title}{delimiter * width}", color=color, bold=True)
        self.print_basic()

    def print_close_header(self,
                           delimiter: str = "-",
                           color: Optional[str] = None,
                           blank_line: bool = True) -> None:
        """
        Log a closing header with an optional new line before.

        :param delimiter: The character to draw the header with.
        :param color: The color to make the text.
        :param blank_line: ``True`` if a blank line should precede the closing header.
        """
        if color is None:
            color = self.header_color

        if blank_line:
            self.print_basic()
        self.print_basic(delimiter * self.console_width, color=color, bold=True)

    def print_dict(self,
                   title: str,
                   data: Any,
                   color: Optional[str] = None) -> None:
        """
        Log data formatted as JSON.

        :param title: The title of the data.
        :param data: The JSON-serializable data.
        :param color: The color to make the text.
        """
        if color is None:
            color = self.default_color

        self.print_basic(f"{title}: {json.dumps(data, indent=4)}", color=color)

    def print_xml(self,
                  title: str,
                  data: str,
                  color: Optional[str] = None) -> None:
        """
        Log formatted XML. If ``data`` is not valid XML, it is logged as-is.

        :param title: The title of the XML blob.
        :param data: An XML string.
        :param color: The color to make the text.
        """
        if color is None:
            color = self.default_color

        try:
            xml = parseString(data).toprettyxml()
        except (ExpatError, DefusedXmlException):
            xml = data

        self.print_basic(f"{title}: {xml}", color=color)

    def print_basic(self,
                    msg: str = "",
                    color: Optional[str] = None,
                    bold: bool = False,
                    print_when_logging: bool = False) -> None:
        """
        Log a basic message. The message will be logged via ``click``, if ``click_logging`` is enabled in
        :class:`~hookee.conf.Config`, or appended to the logger.

        :param msg: The update to print.
        :param color: The color to make the text.
        :param bold: ``True`` if the output should be bold.
        :param print_when_logging: ``True`` if, when ``click_logging`` is ``False``, ``msg`` should print to the
            console instead of appending to the logger.
        """
        if color is None:
            color = self.default_color

        if self.config.click_logging:
            click.secho(msg, fg=color, bold=bold)
        elif not print_when_logging:
            logger.info(msg)
        else:
            print(msg)


def get_functions(mod: ModuleType) -> List[str]:
    """
    Get a list of function names for the given module.

    :param mod: The module to inspect for functions.
    :return: The list of function names.
    """
    return [o[0] for o in inspect.getmembers(mod, inspect.isfunction)]


def get_args(func: Callable) -> List[str]:
    """
    Get a list of args for the given function.

    :param func: The function to inspect for args.
    :return: The list of args.
    """
    return inspect.getfullargspec(func)[0]


def get_module_name(module: ModuleType) -> str:
    """
    Get the name of the module from the basename of its path.

    :param module: The module.
    :return: The base name of the module.
    """
    return os.path.splitext(os.path.basename(module.__file__))[0]


def multidict_to_dict(multidict: MultiDict) -> Dict[str, Any]:
    """
    Convert a :class:`~werkzeug.datastructures.MultiDict` to a ``dict``, keeping every value of a repeated key.

    :param multidict: The ``MultiDict`` to convert.
    :return: The converted ``dict``, with a list of values for any key that was repeated.
    """
    return {key: values if len(values) > 1 else values[0] for key, values in multidict.lists()}


def decode_body(data: bytes) -> str:
    """
    Decode a request or response body so it can be printed.

    :param data: The raw body.
    :return: The body as text, or a description of it if it is not text.
    """
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return f"<{len(data)} bytes of binary data>"


def is_xml(mimetype: Optional[str]) -> bool:
    """
    Check if the given mimetype is for XML, which some webhook providers expect in a response.

    :param mimetype: The mimetype.
    :return: ``True`` if the mimetype is for XML.
    """
    return mimetype is not None and (mimetype in ["application/xml", "text/xml"] or mimetype.endswith("+xml"))


def mask_sensitive_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Mask the values of headers that carry credentials, like ``Authorization`` and ``Cookie``. For authorization
    headers, the scheme (like ``Basic`` or ``Bearer``) is kept.

    :param headers: The headers.
    :return: A copy of the headers with sensitive values masked.
    """
    masked_headers = {}
    for name, value in headers.items():
        if name.lower() in AUTHORIZATION_HEADERS:
            scheme, _, credentials = value.partition(" ")
            masked_headers[name] = f"{scheme} {MASK}" if credentials else MASK
        elif name.lower() in COOKIE_HEADERS:
            masked_headers[name] = MASK
        else:
            masked_headers[name] = value

    return masked_headers


def save_request(request: Request,
                 response: Response,
                 save_dir: str,
                 show_sensitive_headers: bool = False) -> str:
    """
    Save the given request, and the response sent for it, to a new JSON file in the given directory. If the response
    is streamed, it is saved once the stream finishes.

    :param request: The request to save.
    :param response: The response sent for the request.
    :param save_dir: The directory to save the request to, which is created if it does not exist.
    :param show_sensitive_headers: ``True`` if headers that carry credentials should be saved without being masked.
    :return: The path to the saved file.
    """
    request_headers = dict(request.headers)
    if not show_sensitive_headers:
        request_headers = mask_sensitive_headers(request_headers)

    now = datetime.now()
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{now:%Y%m%d-%H%M%S-%f}-{uuid.uuid4().hex[:8]}.json")
    saved_request = {
        "method": request.method,
        "path": request.path,
        "query": multidict_to_dict(request.args),
        "headers": request_headers,
        **_encode_body(request.get_data()),
    }

    if response.is_streamed:
        response.response = _save_when_streamed(response.response, path, now, saved_request, response,
                                                show_sensitive_headers)
    else:
        _write_saved_request(path, now, saved_request, response, response.get_data(), show_sensitive_headers)

    return path


def _save_when_streamed(chunks: Iterable[Union[str, bytes]],
                        path: str,
                        now: datetime,
                        saved_request: Dict[str, Any],
                        response: Response,
                        show_sensitive_headers: bool) -> Iterator[Union[str, bytes]]:
    streamed_body = []
    for chunk in chunks:
        streamed_body.append(chunk.encode("utf-8") if isinstance(chunk, str) else chunk)
        yield chunk

    _write_saved_request(path, now, saved_request, response, b"".join(streamed_body), show_sensitive_headers)


def _write_saved_request(path: str,
                         now: datetime,
                         saved_request: Dict[str, Any],
                         response: Response,
                         response_body: bytes,
                         show_sensitive_headers: bool) -> None:
    response_headers = dict(response.headers)
    if not show_sensitive_headers:
        response_headers = mask_sensitive_headers(response_headers)

    with open(path, "w") as f:
        json.dump({
            "timestamp": now.isoformat(),
            "request": saved_request,
            "response": {
                "status_code": response.status_code,
                "headers": response_headers,
                **_encode_body(response_body),
            },
        }, f, indent=4)


def _encode_body(data: bytes) -> Dict[str, str]:
    try:
        return {"body": data.decode("utf-8"), "body_encoding": "utf-8"}
    except UnicodeDecodeError:
        return {"body": base64.b64encode(data).decode("ascii"), "body_encoding": "base64"}
