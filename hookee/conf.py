import os

import confuse

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"

template = {
    "auth_token": confuse.String(default=None),
    "region": confuse.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"], default=None),
    "subdomain": confuse.String(default=None),
    "auth": confuse.String(default=None),
    "port": int,
    "plugins_dir": confuse.Filename(),
    "plugins": list,
    "console_width": confuse.Integer(default=80),
    "last_request": confuse.Filename(default=None),
    "last_response": confuse.Filename(default=None),
}


class Config:
    """
    An object with accessor methods containing :code:`hookee`'s configuration. Default configuration can be
    overridden by creating a custom :code:`config.yaml` in :code:`~/.config/hookee` (when setting config
    values from the command lind, this is where values are updated) which in turn can be overridden by
    passing args to the CLI.

    :var ctx: The :code:`click` CLI context.
    :vartype ctx: click.Context
    :var config_obj: The templated config object.
    :vartype config_obj: confuse.Configuration
    :var config_dir: The directory of the config being used.
    :vartype config_dir: str
    :var config_filename: The full path to the config file being used.
    :vartype config_filename: str
    :var config_data: The parsed and validated config data. Use :func:`get`, :func:`set`, and other accessors
        to interact with the data.
    :vartype config_data: confuse.AttrDict
    """

    def __init__(self, ctx):
        self.ctx = ctx

        try:
            config = confuse.Configuration("hookee", __name__)
            config.set_args(ctx.obj)

            self.config_obj = config
            self.config_dir = self.config_obj.config_dir()
            self.config_path = os.path.join(self.config_dir, confuse.CONFIG_FILENAME)

            self.config_data = config.get(template)

            plugins_dir = os.path.expanduser(self.config_data["plugins_dir"])
            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)
        except confuse.NotFoundError as e:
            ctx.fail("The config file is invalid: {}.".format(str(e)))
        except (confuse.ConfigReadError, ValueError):
            ctx.fail("The config file is not valid YAML.")

    def get(self, key):
        """
        Get the config value for the given key.

        :param key: The key.
        :type key: str
        :return: The config value.
        :rtype: object
        """
        return self.config_data[key]

    def set(self, key, value):
        """
        Update the config value for the given key, persisting to user's :code:`config.yaml`.

        :param key: The key.
        :type key: str
        :param value: The value to set.
        :type key: object
        """
        if value != self.config_data[key]:
            self.config_data[key] = value

            self.config_obj[key] = value
            with open(self.config_path, "w") as f:
                f.write(self.config_obj.dump())

    def append(self, key, value):
        """
        Update the config value by appending to the list for the given key, persisting to
        user's :code:`config.yaml`.

        :param key: The key.
        :type key: str
        :param value: The value to append.
        :type value: object
        """
        list_item = list(self.config_data[key])

        if value not in list_item:
            list_item.append(value)
            self.config_data[key] = list_item

            self.config_obj[key] = list_item
            with open(self.config_path, "w") as f:
                f.write(self.config_obj.dump())

    def remove(self, key, value):
        """
        Update the config value by removing the given value from the list for the given key, persisting to
        user's :code:`config.yaml`.

        :param key: The key.
        :type key: str
        :param value: The value to remove.
        :type value: object
        """
        list_item = list(self.config_data[key])

        if value in list_item:
            list_item.remove(value)
            self.config_data[key] = list_item

            self.config_obj[key] = list_item
            with open(self.config_path, "w") as f:
                f.write(self.config_obj.dump())
