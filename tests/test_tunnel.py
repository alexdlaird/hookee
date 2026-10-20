__copyright__ = "Copyright (c) 2020-2026 Alex Laird"
__license__ = "MIT"

import os
from unittest import mock

from pyngrok.exception import PyngrokNgrokHTTPError

from hookee import HookeeManager
from hookee.conf import Config
from hookee.exception import HookeeConfigError, HookeeError
from tests.testcase import HookeeTestCase


class TestTunnel(HookeeTestCase):
    def given_traffic_policy_file(self, contents):
        path = os.path.join(self.config_dir, "policy.yml")
        with open(path, "w") as f:
            f.write(contents)
        return path

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_translates_options_to_v3(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my-hooks.ngrok.io"
        config = Config(port=8002, url="https://my-hooks.ngrok.io", basic_auth="username:password",
                        host_header="localhost:8002", pooling_enabled=True)
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        self.assertEqual(options["url"], "https://my-hooks.ngrok.io")
        self.assertTrue(options["pooling_enabled"])
        self.assertEqual(options["traffic_policy"]["on_http_request"], [{
            "actions": [
                {"type": "basic-auth", "config": {"credentials": ["username:password"]}},
                {"type": "add-headers", "config": {"headers": {"host": "localhost:8002"}}}
            ]
        }])
        self.assertNotIn("schemes", options)

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_verify_webhook_actions(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my-hooks.ngrok.io"
        config = Config(port=8009, verify_webhook="twilio:my:secret", basic_auth="username:password")
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        self.assertEqual(options["traffic_policy"]["on_http_request"], [{
            "actions": [
                {"type": "remove-headers", "config": {"headers": ["X-Hookee-Webhook-Verified"]}},
                {"type": "verify-webhook", "config": {"provider": "twilio", "secret": "my:secret", "enforce": False}},
                {"type": "add-headers",
                 "config": {"headers": {"X-Hookee-Webhook-Verified": "${actions.ngrok.verify_webhook.verified}"}}},
                {"type": "basic-auth", "config": {"credentials": ["username:password"]}}
            ]
        }])

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_verify_webhook_without_secret_passed_through(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my-hooks.ngrok.io"
        tunnel = HookeeManager(config=Config(port=8009, verify_webhook="twilio")).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        verify_webhook_action = options["traffic_policy"]["on_http_request"][0]["actions"][1]
        self.assertEqual(verify_webhook_action["config"], {"provider": "twilio", "enforce": False})

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_bare_domain_url_uses_https(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my.domain.com"
        config = Config(port=8003, url="my.domain.com")
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        self.assertEqual(options["url"], "https://my.domain.com")
        self.assertNotIn("traffic_policy", options)
        self.assertNotIn("pooling_enabled", options)

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_merges_shortcuts_with_traffic_policy_file(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my-hooks.ngrok.io"
        policy_path = self.given_traffic_policy_file(
            "on_http_request:\n"
            "  - actions:\n"
            "      - type: custom-response\n"
            "        config:\n"
            "          status_code: 418\n"
            "on_http_response:\n"
            "  - actions:\n"
            "      - type: compress-response\n")
        config = Config(port=8004, basic_auth="username:password", traffic_policy_file=policy_path)
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        self.assertNotIn("traffic_policy_file", options)
        self.assertEqual(options["traffic_policy"]["on_http_request"], [
            {"actions": [{"type": "basic-auth", "config": {"credentials": ["username:password"]}}]},
            {"actions": [{"type": "custom-response", "config": {"status_code": 418}}]}
        ])
        self.assertEqual(options["traffic_policy"]["on_http_response"],
                         [{"actions": [{"type": "compress-response"}]}])

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_passes_traffic_policy_file_through(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.return_value.public_url = "https://my-hooks.ngrok.io"
        policy_path = self.given_traffic_policy_file("- not\n- validated\n- by\n- hookee\n")
        config = Config(port=8007, traffic_policy_file=policy_path)
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        tunnel._start_tunnel()

        # THEN
        _, options = mock_ngrok.connect.call_args
        self.assertEqual(options["traffic_policy_file"], policy_path)
        self.assertNotIn("traffic_policy", options)

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_tunnel_invalid_traffic_policy_file_to_merge(self, mock_ngrok):
        # GIVEN
        policy_path = self.given_traffic_policy_file("- just\n- a list\n")
        config = Config(port=8005, basic_auth="username:password", traffic_policy_file=policy_path)
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        with self.assertRaises(HookeeConfigError) as cm:
            tunnel._start_tunnel()

        # THEN
        self.assertIn("must contain a YAML or JSON object", str(cm.exception))
        mock_ngrok.connect.assert_not_called()

    @mock.patch("hookee.tunnel.ngrok")
    def test_start_fails_instead_of_hanging_when_tunnel_errors(self, mock_ngrok):
        # GIVEN
        mock_ngrok.connect.side_effect = PyngrokNgrokHTTPError("invalid endpoint configuration", "url", 400,
                                                               "Bad Request", {}, "{}")
        config = Config(port=8006)
        tunnel = HookeeManager(config=config).tunnel

        # WHEN
        with self.assertRaises(HookeeError) as cm:
            tunnel.start()

        # THEN
        self.assertIn("The ngrok tunnel failed to start", str(cm.exception))

    def test_removed_subdomain_config_key_fails(self):
        # WHEN
        with self.assertRaises(HookeeConfigError) as cm:
            Config(subdomain="my-hooks")

        # THEN
        self.assertIn("\"subdomain\" is no longer supported", str(cm.exception))
        self.assertIn("Use \"url\" instead", str(cm.exception))

    def test_removed_hostname_config_key_fails(self):
        # WHEN
        with self.assertRaises(HookeeConfigError) as cm:
            Config(hostname="my-hooks.ngrok.io")

        # THEN
        self.assertIn("\"hostname\" is no longer supported", str(cm.exception))
        self.assertIn("Use \"url\" instead", str(cm.exception))

    def test_removed_auth_config_key_fails(self):
        # WHEN
        with self.assertRaises(HookeeConfigError) as cm:
            Config(auth="username:password")

        # THEN
        self.assertIn("\"auth\" is no longer supported", str(cm.exception))
        self.assertIn("Use \"basic_auth\" instead", str(cm.exception))

    def test_region_passed_to_pyngrok_config(self):
        # GIVEN
        config = Config(port=8008, region="eu")

        # WHEN
        tunnel = HookeeManager(config=config).tunnel

        # THEN
        self.assertEqual(tunnel.pyngrok_config.region, "eu")
