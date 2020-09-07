import os
import shutil
import unittest

from click.testing import CliRunner

from hookee.conf import Config

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.10"


class Context:
    def __init__(self, obj=None):
        if obj is None:
            obj = {}

        self.obj = obj


class HookeeTestCase(unittest.TestCase):
    ctx = Context()

    def setUp(self):
        self.config_dir = os.path.normpath(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), ".config", "hookee"))
        os.environ["HOOKEEDIR"] = self.config_dir
        self.config = Config(self.ctx)

        self.plugins_dir = os.path.normpath(os.path.join(self.config_dir, "plugins"))
        self.config.set("plugins_dir", self.plugins_dir)
        os.makedirs(self.plugins_dir)

        self.runner = CliRunner()

    def tearDown(self):
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
