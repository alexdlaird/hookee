from hookee.climanager import CliManager
from hookee.pluginmanager import PluginManager

from hookee import util
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"


class TestUtil(HookeeTestCase):
    def test_get_functions(self):
        # GIVEN
        cli_manager = CliManager(self.ctx)
        plugin_manager = PluginManager(cli_manager)
        plugin = plugin_manager.get_plugin("request_url_info")

        # WHEN
        funcs = util.get_functions(plugin)

        # THEN
        self.assertEqual(funcs, ["run", "setup"])

    def get_args(self):
        # GIVEN
        cli_manager = CliManager(self.ctx)
        plugin_manager = PluginManager(cli_manager)
        plugin = plugin_manager.get_plugin("request_url_info")

        # WHEN
        args = util.get_args(plugin.run)

        # THEN
        self.assertEqual(args, ["request"])
