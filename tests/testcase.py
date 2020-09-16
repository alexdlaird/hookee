import os
import shutil
import unittest

from click.testing import CliRunner
from hookee import conf

from hookee.conf import Config

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.1.0"


class HookeeTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), ".config", "hookee"))
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        os.environ["HOOKEEDIR"] = self.config_dir

        self.ctx = conf.default_context
        self.config = Config(self.ctx)

        self.plugins_dir = os.path.normpath(os.path.join(self.config_dir, "plugins"))
        self.config.set("plugins_dir", self.plugins_dir)
        if not os.path.exists(self.plugins_dir):
            os.mkdir(self.plugins_dir)

        self.runner = CliRunner()

    def tearDown(self):
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
