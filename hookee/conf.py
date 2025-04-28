__copyright__ = "Copyright (c) 2020-2025 Alex Laird"
__license__ = "MIT"

import os
import threading

import click
import confuse

from hookee.exception import HookeeConfigError

template = {
    "default_route": confuse.String(default="/webhook$"),
    "default_route_methods": confuse.String(default="^(GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS|TRACE|CONNECT)$"),
    "port": int,
    "no_tunnel": confuse.OneOf([True, False], default=False),
    "tunnel_name": confuse.String(default=None),
    "subdomain": confuse.String(default=None),
    "region": confuse.Choice(["us", "eu", "ap", "au", "sa", "jp", "in", "us-cal-1"], default=None),
    "domain": confuse.String(default=None),
    # Deprecated, use "domain" instead
    "hostname": confuse.String(default=None),
    "basic_auth": confuse.String(default=None),
    # Deprecated, use "basic_auth" instead
    "auth": confuse.String(default=None),
    "host_header": confuse.String(default=None),
    "response": confuse.String(default=None),
    "content_type": confuse.String(default=None),
    "request_script": confuse.Filename(default=None),
    "response_script": confuse.Filename(default=None),
    "auth_token": confuse.String(default=os.environ.get("NGROK_AUTHTOKEN")),
    "api_key": confuse.String(default=os.environ.get("NGROK_API_KEY")),
    "plugins_dir": confuse.Filename(),
    "plugins": list,
    "console_width": confuse.Integer(default=80),
    "header_color": confuse.Integer(default="green"),
    "default_color": confuse.Integer(default="white"),
    "request_color": confuse.Integer(default="white"),
}

config_file_lock = threading.Lock()


class Config:
    """
    An object with accessor methods containing ``hookee``'s configuration. Default configuration can be
    overridden by creating a custom config at ``~/.config/hookee/config.yaml`` (when setting config
    values from the command line, this is where updated values are stored) which in turn can be overridden by
    passing args to the CLI.

    If instantiating for a custom integration, args that would otherwise have been passed to and validated by the CLI
    (see ``hookee --help``) can instead be passed as ``kwargs`` here to ensure the same validation is done.
    For example:

    .. code-block:: python

        from hookee.conf import Config

        config = Config(subdomain="my_domain",
                        region="eu")

    A callback function can also be passed instead of ``response`` and ``content-type`` (or needing to use
    plugins) when integrating with ``hookee``'s APIs:

    .. code-block:: python

        from hookee.conf import Config

        def response_callback(request, response):
            response.data = "<Response>Ok</Response>"
            response.headers["Content-Type"] = "application/xml"
            return response

        config = Config(response_callback=response_callback)

    :var config_obj: The templated config object.
    :vartype config_obj: confuse.core.Configuration
    :var config_dir: The directory of the config being used.
    :vartype config_dir: str
    :var config_path: The full path to the config file being used.
    :vartype config_path: str
    :var config_data: The parsed and validated config data. Use :func:`get`, :func:`set`, and other accessors
        to interact with the data.
    :vartype config_data: confuse.templates.AttrDict
    :var click_logging: ``True`` if ``click`` should be used for log output, which enables colors and formatting when
        logging to a console, ``False`` if a logger should be used. If not passed, ``True`` if a :class:`click.Context`
        is found to be active. Not persisted to the config file.
    :vartype click_logging: bool
    :var response_callback: The response callback function, if defined. Not persisted to the config file.
    :vartype response_callback: types.FunctionType, optional
    """

    def __init__(self, click_logging=None, **kwargs):
        try:
            if click_logging is None:
                click_logging = click.get_current_context(silent=True) is not None

            self.response_callback = kwargs.pop("response_callback", None)

            config = confuse.Configuration("hookee", __name__)
            config.set_args(kwargs)

            self.config_obj = config
            self.config_dir = self.config_obj.config_dir()
            self.config_path = os.path.join(self.config_dir, confuse.CONFIG_FILENAME)

            self.config_data = config.get(template)

            self.click_logging = click_logging

            if self.config_data.get("response") and self.response_callback:
                raise HookeeConfigError("Can't define both \"response\" and \"response_callback\".")
            elif self.response_callback and not callable(self.response_callback):
                raise HookeeConfigError("\"response_callback\" must be a function.")

            plugins_dir = os.path.expanduser(self.config_data["plugins_dir"])
            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)
        except confuse.NotFoundError as e:
            raise HookeeConfigError(f"The config file is invalid: {str(e)}.")
        except (confuse.ConfigReadError, ValueError):
            raise HookeeConfigError("The config file is not valid YAML.")

    def get(self, key, default=None):
        """
        Get the config value for the given key of persisted data.

        :param key: The key.
        :type key: str
        :param default: The default, if config not set.
        :type key: str
        :return: The config value.
        :rtype: object
        """
        return self.config_data.get(key, default)

    def set(self, key, value):
        """
        Update the config key to the given value, persisting to ``config.yaml``.

        :param key: The key.
        :type key: str
        :param value: The value to set.
        :type key: object
        """
        if value != self.config_data[key]:
            self._update_config_objects(key, value)

    def append(self, key, value):
        """
        Update the config key by appending to the list the given value, persisting to ``config.yaml``.

        :param key: The key.
        :type key: str
        :param value: The value to append.
        :type value: object
        """
        list_item = list(self.config_data[key])

        if value not in list_item:
            list_item.append(value)
            self._update_config_objects(key, list_item)

    def remove(self, key, value):
        """
        Update the config key by removing from the list the given value from the list for the given key, persisting to
        ``config.yaml``.

        :param key: The key.
        :type key: str
        :param value: The value to remove.
        :type value: object
        """
        list_item = list(self.config_data[key])

        if value in list_item:
            list_item.remove(value)
            self._update_config_objects(key, list_item)

    def _update_config_objects(self, key, value):
        self.config_data[key] = value
        self.config_obj[key] = value

        self._write_config_objects_to_file()

    def _write_config_objects_to_file(self):
        with config_file_lock:
            with open(self.config_path, "w") as f:
                f.write(self.config_obj.dump())
