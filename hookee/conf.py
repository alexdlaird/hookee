import os

import confuse

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.4"


class Config:
    auth_token = confuse.as_template(str)
    auth_token.default = None

    console_width = confuse.as_template(int)
    console_width.default = 80

    template = {
        "auth_token": auth_token,
        "port": int,
        "plugins_dir": confuse.Filename(),
        "plugins": list,
        "console_width": console_width
    }

    def __init__(self, ctx):
        self.ctx = ctx

        try:
            config = confuse.Configuration("hookee", __name__)
            config.set_args(ctx.obj)

            self.config_obj = config
            self.config_dir = self.config_obj.config_dir()
            self.config_filename = os.path.join(self.config_dir, confuse.CONFIG_FILENAME)

            self.config = config.get(self.template)

            plugins_dir = os.path.expanduser(self.config["plugins_dir"])
            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)
        except confuse.NotFoundError as e:
            ctx.fail("The config file is invalid: {}.".format(str(e)))
        except (confuse.ConfigReadError, ValueError):
            ctx.fail("The config file is not valid YAML.")

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        if value != self.config[key]:
            self.config[key] = value

            self.config_obj[key] = value
            with open(self.config_filename, "w") as f:
                f.write(self.config_obj.dump())

    def append(self, key, value):
        list_item = list(self.config[key])

        if value not in list_item:
            list_item.append(value)
            self.config[key] = list_item

            self.config_obj[key] = list_item
            with open(self.config_filename, "w") as f:
                f.write(self.config_obj.dump())

    def remove(self, key, value):
        list_item = list(self.config[key])

        if value in list_item:
            list_item.remove(value)
            self.config[key] = list_item

            self.config_obj[key] = list_item
            with open(self.config_filename, "w") as f:
                f.write(self.config_obj.dump())
