__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from hookee import HookeeManager, util
from hookee.pluginmanager import PluginManager
from tests.testcase import HookeeTestCase


class TestUtil(HookeeTestCase):
    def setUp(self):
        super(TestUtil, self).setUp()

        self.hookee_manager = HookeeManager()
        self.plugin_manager = PluginManager(self.hookee_manager)
        self.plugin = self.plugin_manager.get_plugin("request_url_info")

    def test_get_functions(self):
        # WHEN
        funcs = util.get_functions(self.plugin.module)

        # THEN
        self.assertEqual(funcs, ["run", "setup"])

    def get_args(self):
        # WHEN
        args = util.get_args(self.plugin.module.run)

        # THEN
        self.assertEqual(args, ["request"])
