import os
import shutil
from unittest import mock

from hookee.cli import hookee

from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.9"


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

    def test_available_plugins_config(self):
        # GIVEN
        custom_plugin_path = os.path.join(self.plugins_dir, "custom_plugin.py")
        shutil.copy(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "hookee", "plugins", "request_body.py"),
            custom_plugin_path)

        # WHEN
        result = self.runner.invoke(hookee, ["available-plugins"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "['blueprint_default', 'custom_plugin', 'request_body', 'request_files', 'request_headers', "
            "'request_query_params', 'request_url_info', 'response_echo', 'response_info']",
            result.output)

    def test_enabled_plugins_config(self):
        # GIVEN
        self.config.remove("plugins", "request_files")
        self.config.remove("plugins", "request_query_params")

        # WHEN
        result = self.runner.invoke(hookee, ["enabled-plugins"])

        # THEN
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "['blueprint_default', 'request_body', 'request_headers', 'request_url_info', 'response_echo', "
            "'response_info']",
            result.output)

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
        self.assertIn("can't disable", result.output)

    @mock.patch("hookee.climanager.CliManager.start")
    def test_start(self, mock_cli_start):
        # WHEN
        self.runner.invoke(hookee, ["start"])

        # THEN
        mock_cli_start.assert_called_once()

    @mock.patch("hookee.climanager.CliManager.start")
    def test_no_command_calls_start(self, mock_cli_start):
        # WHEN
        self.runner.invoke(hookee)

        # THEN
        mock_cli_start.assert_called_once()
