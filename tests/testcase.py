import os
import shutil
import unittest

from click.testing import CliRunner

from hookee.conf import Config

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.4"


class HookeeTestCase(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.normpath(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), ".config", "hookee"))
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        os.environ["HOOKEEDIR"] = self.config_dir

        self.config = Config()

        self.plugins_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "plugins_dir")
        self.config.set("plugins_dir", self.plugins_dir)

        self.runner = CliRunner()

    def tearDown(self):
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
