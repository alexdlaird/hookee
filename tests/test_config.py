__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"

from unittest import mock

from hookee.conf import Config
from hookee.exception import HookeeConfigError
from tests.testcase import HookeeTestCase


class TestConfig(HookeeTestCase):
    def test_write_updates_file(self):
        # GIVEN
        with open(self.config.config_path) as f:
            contents = f.read()
        self.assertNotIn("test123", contents)

        # WHEN
        self.config._update_config_objects("auth_token", "test123")
        with open(self.config.config_path) as f:
            updated_contents = f.read()

        # THEN
        self.assertNotEqual(contents, updated_contents)
        self.assertIn("test123", updated_contents)

    @mock.patch("hookee.conf.Config._write_config_objects_to_file")
    def test_config_set(self, mock_write_config_objects_to_file):
        # WHEN
        self.config.set("auth_token", "test123")

        # THEN
        self.assertEqual(self.config.get("auth_token"), "test123")
        self.assertTrue(mock_write_config_objects_to_file.called)

    @mock.patch("hookee.conf.Config._write_config_objects_to_file")
    def test_config_append(self, mock_write_config_objects_to_file):
        # GIVEN
        self.assertNotIn("foo_bar", self.config.get("plugins"))

        # WHEN
        self.config.append("plugins", "foo_bar")

        # THEN
        self.assertIn("foo_bar", self.config.get("plugins"))
        self.assertTrue(mock_write_config_objects_to_file.called)

    @mock.patch("hookee.conf.Config._write_config_objects_to_file")
    def test_config_remove(self, mock_write_config_objects_to_file):
        # GIVEN
        self.assertIn("request_headers", self.config.get("plugins"))

        # WHEN
        self.config.remove("plugins", "request_headers")

        # THEN
        self.assertNotIn("request_headers", self.config.get("plugins"))
        self.assertTrue(mock_write_config_objects_to_file.called)

    def test_config_append_already_present(self):
        # GIVEN
        plugins_before = list(Config().get("plugins"))

        # WHEN
        appended = self.config.append("plugins", "request_headers")

        # THEN
        self.assertFalse(appended)
        self.assertEqual(plugins_before, list(Config().get("plugins")))

    def test_config_remove_all_occurrences(self):
        # GIVEN
        self.config.set("plugins", ["blueprint_default", "request_headers", "request_headers"])

        # WHEN
        removed = self.config.remove("plugins", "request_headers")

        # THEN
        self.assertTrue(removed)
        self.assertEqual(["blueprint_default"], list(Config().get("plugins")))

    def test_config_remove_not_present(self):
        # GIVEN
        plugins_before = list(Config().get("plugins"))

        # WHEN
        removed = self.config.remove("plugins", "foo_bar")

        # THEN
        self.assertFalse(removed)
        self.assertEqual(plugins_before, list(Config().get("plugins")))

    def test_config_write_does_not_persist_overrides(self):
        # GIVEN
        config = Config(port=9999)

        # WHEN
        config.set("auth_token", "test123")

        # THEN
        self.assertEqual(9999, config.get("port"))
        self.assertEqual(8000, Config().get("port"))
        self.assertEqual("test123", Config().get("auth_token"))

    def test_config_remove_with_override_uses_persisted_list(self):
        # GIVEN
        plugins_before = list(Config().get("plugins"))
        config = Config(plugins=["blueprint_default", "request_headers"])

        # WHEN
        removed = config.remove("plugins", "request_body")

        # THEN
        self.assertTrue(removed)
        self.assertEqual(["blueprint_default", "request_headers"], list(config.get("plugins")))
        self.assertEqual([p for p in plugins_before if p != "request_body"], list(Config().get("plugins")))

    def test_config_with_invalid_value_raises_hookee_config_error(self):
        # GIVEN
        with open(self.config.config_path, "a") as f:
            f.write("\nno_tunnel: maybe\n")

        # WHEN
        with self.assertRaises(HookeeConfigError) as cm:
            Config()

        # THEN
        self.assertIn("no_tunnel", str(cm.exception))
