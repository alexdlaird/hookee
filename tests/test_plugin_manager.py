import os
from types import ModuleType

from flask import Response

from hookee.pluginmanager import PluginManager, Plugin

from hookee import HookeeManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.0"


class TestPluginManager(HookeeTestCase):
    def setUp(self):
        super(TestPluginManager, self).setUp()

        self.hookee_manager = HookeeManager()
        self.plugin_manager = PluginManager(self.hookee_manager)

    def test_build_from_module(self):
        # GIVEN
        plugin = self.plugin_manager.source.load_plugin("request_body")

        # WHEN
        plugin = Plugin.build_from_module(plugin)

        # THEN
        self.assertTrue(isinstance(plugin, Plugin))
        self.assertTrue(isinstance(plugin.module, ModuleType))
        self.assertEqual(plugin.plugin_type, "request")
        self.assertEqual(plugin.name, "request_body")
        self.assertTrue(plugin.has_setup)

    def test_build_from_module_not_conform_to_spec(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_build_from_module_no_plugin_type(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_build_from_module_no_run(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_build_from_module_wrong_args(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_build_from_module_no_blueprint(self):
        # TODO implement
        pass
        # GIVEN

        # WHEN

        # THEN

    def test_response_callback(self):
        # GIVEN
        def response_callback(request, response):
            response.data = "<Response>Ok</Response>"
            response.headers["Content-Type"] = "application/xml"
            return response

        self.assertEqual(0, len(self.plugin_manager.loaded_plugins))
        self.hookee_manager.config.set("response_callback", response_callback)

        # WHEN
        self.plugin_manager.load_plugins()

        # THEN
        self.assertIsNotNone(self.plugin_manager.response_callback)
        response = self.plugin_manager.response_callback(None, Response())
        self.assertEqual(response.data.decode("utf-8"), "<Response>Ok</Response>")
        self.assertEqual(response.headers["Content-Type"], "application/xml")

    def test_load_plugins(self):
        # GIVEN
        self.assertEqual(0, len(self.plugin_manager.loaded_plugins))
        request_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins",
                                           "request_body.py")
        response_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins",
                                            "response_echo.py")
        self.hookee_manager.config.set("request_script", request_script_path)
        self.hookee_manager.config.set("response_script", response_script_path)
        self.hookee_manager.config.set("response", "<Response>Ok</Response>")
        self.hookee_manager.config.set("content_type", "application/xml")

        # WHEN
        self.plugin_manager.load_plugins()

        # THEN
        self.assertEqual(8, len(self.plugin_manager.loaded_plugins))
        for plugin in self.plugin_manager.loaded_plugins:
            self.assertTrue(isinstance(plugin, Plugin))
        self.assertTrue(isinstance(self.plugin_manager.request_script, Plugin))
        self.assertEqual(self.plugin_manager.request_script.name, "request_body")
        self.assertTrue(isinstance(self.plugin_manager.response_script, Plugin))
        self.assertEqual(self.plugin_manager.response_script.name, "response_echo")
        self.assertIsNotNone(self.plugin_manager.response_callback)
        response = self.plugin_manager.response_callback(None, Response())
        self.assertEqual(response.data.decode("utf-8"), "<Response>Ok</Response>")
        self.assertEqual(response.headers["Content-Type"], "application/xml")
