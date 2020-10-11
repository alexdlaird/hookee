import os
from types import ModuleType

from flask import Response
from hookee.exception import HookeePluginValidationError

from hookee.pluginmanager import PluginManager, Plugin, VALID_PLUGIN_TYPES, BLUEPRINT_PLUGIN

from hookee import HookeeManager
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.2.4"


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

    def test_build_from_module_no_plugin_type(self):
        # GIVEN
        plugin = self.plugin_manager.source.load_plugin("no_plugin_type")

        # WHEN
        with self.assertRaises(HookeePluginValidationError) as cm:
            Plugin.build_from_module(plugin)

        # THEN
        self.assertIn("does not conform to the plugin spec", str(cm.exception))

    def test_build_from_module_no_run(self):
        # GIVEN
        plugin = self.plugin_manager.source.load_plugin("no_run")

        # WHEN
        with self.assertRaises(HookeePluginValidationError) as cm:
            Plugin.build_from_module(plugin)

        # THEN
        self.assertIn("must implement `run", str(cm.exception))

    def test_build_from_module_wrong_args(self):
        # GIVEN
        plugin = self.plugin_manager.source.load_plugin("wrong_args")

        # WHEN
        with self.assertRaises(HookeePluginValidationError) as cm:
            Plugin.build_from_module(plugin)

        # THEN
        self.assertIn("`run(request)` must be defined", str(cm.exception))

    def test_build_from_module_no_blueprint(self):
        # GIVEN
        plugin = self.plugin_manager.source.load_plugin("no_blueprint")

        # WHEN
        with self.assertRaises(HookeePluginValidationError) as cm:
            Plugin.build_from_module(plugin)

        # THEN
        self.assertIn("must define `blueprint", str(cm.exception))

    def test_response_callback(self):
        # GIVEN
        def response_callback(request, response):
            response.data = "<Response>Ok</Response>"
            response.headers["Content-Type"] = "application/xml"
            return response

        self.assertEqual(0, len(self.plugin_manager.loaded_plugins))
        self.hookee_manager.config.response_callback = response_callback

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
        custom_plugin_path = os.path.join(self.plugins_dir, "custom_plugin.py")
        custom_request_plugin_path = os.path.join(self.plugins_dir, "custom_request_plugin.py")
        custom_response_plugin_path = os.path.join(self.plugins_dir, "custom_response_plugin.py")

        self.hookee_manager.config.append("plugins", "custom_plugin")
        self.hookee_manager.config.set("request_script", custom_request_plugin_path)
        self.hookee_manager.config.set("response_script", custom_response_plugin_path)
        self.hookee_manager.config.set("response", "<Response>Ok</Response>")
        self.hookee_manager.config.set("content_type", "application/xml")

        # WHEN
        self.plugin_manager.load_plugins()

        # THEN
        self.assertEqual(11, len(self.plugin_manager.loaded_plugins))
        request_script_found = False
        response_script_found = False
        for plugin in self.plugin_manager.loaded_plugins:
            self.assertTrue(isinstance(plugin, Plugin))
            self.assertIn(plugin.plugin_type, VALID_PLUGIN_TYPES)
            self.assertTrue(hasattr(plugin.module, "plugin_type"))
            self.assertIn(plugin.module.plugin_type, VALID_PLUGIN_TYPES)
            self.assertTrue(hasattr(plugin.module, "setup"))
            if plugin.plugin_type != BLUEPRINT_PLUGIN:
                self.assertTrue(hasattr(plugin.module, "run"))

            if plugin.name == "custom_request_plugin":
                request_script_found = True
            elif plugin.name == "custom_response_plugin":
                response_script_found = True
        self.assertTrue(request_script_found)
        self.assertTrue(response_script_found)
        # The last plugin should always be the response_script that we added
        self.assertEqual(self.plugin_manager.loaded_plugins[-1].name, "custom_response_plugin")
        self.assertIsNotNone(self.plugin_manager.response_callback)
        response = self.plugin_manager.response_callback(None, Response())
        self.assertEqual(response.data.decode("utf-8"), "<Response>Ok</Response>")
        self.assertEqual(response.headers["Content-Type"], "application/xml")
