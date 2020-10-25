import os
from unittest import mock

from hookee.cli import hookee
from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.0.0"


class TestCli(HookeeTestCase):
    def test_update_config(self):
        # WHEN
        result = self.runner.invoke(hookee, ["update-config", "port", "1000"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn("\"port\" has been updated", result.output)

    def test_update_invalid_config(self):
        # WHEN
        result = self.runner.invoke(hookee, ["update-config", "foo", "bar"])

        # THEN
        self.assertEqual(result.exit_code, 2)
        self.assertIn("No such key", result.output)

    def test_available_plugins(self):
        # WHEN
        result = self.runner.invoke(hookee, ["available-plugins"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" * blueprint_default", result.output)
        self.assertIn(" * custom_plugin", result.output)
        self.assertIn(" * request_body", result.output)
        self.assertIn(" * request_files", result.output)
        self.assertIn(" * request_headers", result.output)
        self.assertIn(" * request_query_params", result.output)
        self.assertIn(" * request_url_info", result.output)
        self.assertIn(" * response_echo", result.output)
        self.assertIn(" * response_info", result.output)

    def test_enabled_plugins(self):
        # GIVEN
        self.config.remove("plugins", "request_files")
        self.config.remove("plugins", "request_query_params")

        # WHEN
        result = self.runner.invoke(hookee, ["enabled-plugins"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" * blueprint_default", result.output)
        self.assertIn(" * request_url_info", result.output)
        self.assertIn(" * request_headers", result.output)
        self.assertIn(" * request_body", result.output)
        self.assertIn(" * response_echo", result.output)
        self.assertIn(" * response_info", result.output)

    def test_enable_plugin(self):
        # WHEN
        result = self.runner.invoke(hookee, ["enable-plugin", "request_body"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn("\"request_body\" has been enabled", result.output)

    def test_enable_plugin_invalid(self):
        # WHEN
        result = self.runner.invoke(hookee, ["enable-plugin", "fake_plugin"])

        # THEN
        self.assertEqual(result.exit_code, 2)
        self.assertIn("\"fake_plugin\" could not be found", result.output)

    def test_disable_plugin(self):
        # WHEN
        result = self.runner.invoke(hookee, ["disable-plugin", "request_body"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn("\"request_body\" is disabled", result.output)

    def test_disable_required_plugin(self):
        # WHEN
        result = self.runner.invoke(hookee, ["disable-plugin", "blueprint_default"])

        # THEN
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Can't disable", result.output)

    @mock.patch("hookee.hookeemanager.HookeeManager.run")
    def test_start(self, mock_hookee_run):
        # WHEN
        result = self.runner.invoke(hookee, ["start"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_hookee_run.called)

    @mock.patch("hookee.hookeemanager.HookeeManager.run")
    def test_no_command_calls_start(self, mock_hookee_run):
        # WHEN
        result = self.runner.invoke(hookee)

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_hookee_run.called)

    @mock.patch("hookee.hookeemanager.HookeeManager.run")
    def test_start_with_script_import(self, mock_hookee_run):
        # GIVEN
        builtin_plugin_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins",
                                           "request_body.py")

        # WHEN
        result = self.runner.invoke(hookee, ["--response-script", builtin_plugin_path])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_hookee_run.called)

    def test_start_with_invalid_script_import(self):
        # WHEN
        result = self.runner.invoke(hookee, ["--response-script", "no_such_file.py"])

        # THEN
        self.assertEqual(result.exit_code, 2)
        self.assertIn("'no_such_file.py' does not exist", result.output)

    @mock.patch("confuse.Configuration.set_args")
    @mock.patch("hookee.hookeemanager.HookeeManager.run")
    def test_start_arg_passed_to_config(self, mock_hookee_run, mock_set_args):
        # GIVEn
        response = "\"<Response>Ok</Response>\""

        # WHEN
        result = self.runner.invoke(hookee, ["--response", response])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(mock_hookee_run.called)
        self.assertTrue(mock_set_args.called)
        call_args, call_kwargs = mock_set_args.call_args
        self.assertIn("response", call_args[0])
        self.assertEqual(call_args[0]["response"], response)
