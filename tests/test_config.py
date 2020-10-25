from unittest import mock

from tests.testcase import HookeeTestCase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.0.0"


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
