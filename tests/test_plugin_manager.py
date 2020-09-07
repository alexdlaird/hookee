import os
from types import ModuleType

from hookee.pluginmanager import PluginManager

from hookee.climanager import CliManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"


class TestPluginManager(HookeeTestCase):
    def setUp(self):
        super(TestPluginManager, self).setUp()

        self.cli_manager = CliManager(self.ctx)
        self.plugin_manager = PluginManager(self.cli_manager)

    def test_validate_plugin(self):
        # GIVEN
        plugin = self.plugin_manager.get_plugin("request_body")

        # WHEN
        has_setup = self.plugin_manager.validate_plugin(plugin)

        # THEN
        self.assertTrue(has_setup)

    def test_validate_plugin_not_conform_to_spec(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_plugin_type(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_run(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_wrong_args(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_validate_plugin_no_blueprint(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_load_plugins(self):
        # GIVEN
        self.assertEqual(0, len(self.plugin_manager.loaded_plugins))
        request_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins",
                                           "request_body.py")
        response_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins",
                                            "response_echo.py")
        self.cli_manager.config.set("request_script", request_script_path)
        self.cli_manager.config.set("response_script", response_script_path)
        self.cli_manager.config.set("response", "<Response>Ok</Response>")
        self.cli_manager.config.set("content_type", "application/xml")

        # WHEN
        self.plugin_manager.load_plugins()

        # THEN
        self.assertEqual(8, len(self.plugin_manager.loaded_plugins))
        for plugin in self.plugin_manager.loaded_plugins:
            self.assertTrue(isinstance(plugin, ModuleType))
        self.assertTrue(isinstance(self.plugin_manager.request_script, ModuleType))
        self.assertEqual(self.plugin_manager.request_script.__name__, "request_body")
        self.assertTrue(isinstance(self.plugin_manager.response_script, ModuleType))
        self.assertEqual(self.plugin_manager.response_script.__name__, "response_echo")
        self.assertEqual(self.plugin_manager.response_body, "<Response>Ok</Response>")
        self.assertEqual(self.plugin_manager.response_content_type, "application/xml")
