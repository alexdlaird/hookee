__copyright__ = "Copyright (c) 2020-2025 Alex Laird"
__license__ = "MIT"

import threading
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml
from pyngrok import conf, ngrok
from pyngrok.conf import PyngrokConfig
from pyngrok.exception import PyngrokError
from pyngrok.process import NgrokProcess

from hookee.conf import Config
from hookee.exception import HookeeConfigError, HookeeError
from hookee.pluginmanager import PluginManager
from hookee.util import WEBHOOK_VERIFIED_HEADER, PrintUtil

if TYPE_CHECKING:
    from hookee.hookeemanager import HookeeManager


class Tunnel:
    """
    An object that manages a non-blocking ``pyngrok`` tunnel and thread.
    """

    def __init__(self, hookee_manager: "HookeeManager") -> None:
        #: Reference to the ``hookee`` Manager.
        self.hookee_manager: "HookeeManager" = hookee_manager
        self.config: Config = self.hookee_manager.config
        #: Reference to the Plugin Manager.
        self.plugin_manager: PluginManager = self.hookee_manager.plugin_manager
        #: Reference to the PrintUtil.
        self.print_util: PrintUtil = self.hookee_manager.print_util
        #: The server's port.
        self.port: int = self.config.get("port")

        #: The ``pyngrok`` config.
        self.pyngrok_config: PyngrokConfig = PyngrokConfig(auth_token=self.config.get("auth_token"),
                                                           api_key=self.config.get("api_key"),
                                                           region=self.config.get("region"))
        conf.set_default(self.pyngrok_config)

        #: The public URL of the tunnel.
        self.public_url: Optional[str] = None
        #: The ``ngrok`` process.
        self.ngrok_process: Optional[NgrokProcess] = None
        self._thread: Optional[threading.Thread] = None
        self._start_error: Optional[Exception] = None

    def _loop(self) -> None:
        thread = None

        try:
            self._start_tunnel()

            thread = threading.current_thread()
            thread.alive = True
            while thread.alive:
                time.sleep(1)
        except (PyngrokError, HookeeError) as e:
            # pyngrok already logged its errors to the console for us
            self._start_error = e

        if thread:
            thread.alive = False

        self.stop()

    def start(self) -> None:
        """
        If one is not already running, start a tunnel in a new thread.
        """
        if self._thread is None:
            self.print_util.print_open_header("Opening Tunnel")

            self._start_error = None
            thread = threading.Thread(target=self._loop, daemon=True)
            self._thread = thread
            thread.start()

            while self.public_url is None and thread.is_alive():
                time.sleep(1)

            if self.public_url is None:
                self.hookee_manager.fail(f"The ngrok tunnel failed to start: {self._start_error}")

            self.print_close_header()

    def _start_tunnel(self) -> None:
        options = {}
        name = self.config.get("tunnel_name")
        url = self.config.get("url")
        if name:
            options["name"] = name
        if url:
            options["url"] = url if "://" in url else f"https://{url}"
        if self.config.get("pooling_enabled"):
            options["pooling_enabled"] = True

        traffic_policy = self._build_traffic_policy()
        if traffic_policy:
            options["traffic_policy"] = traffic_policy
        elif self.config.get("traffic_policy_file"):
            options["traffic_policy_file"] = self.config.get("traffic_policy_file")

        self.public_url = ngrok.connect(str(self.port), **options).public_url
        self.ngrok_process = ngrok.get_ngrok_process()

    def _build_traffic_policy(self) -> Dict[str, Any]:
        actions = []
        verify_webhook = self.config.get("verify_webhook")
        basic_auth = self.config.get("basic_auth")
        host_header = self.config.get("host_header")
        if verify_webhook:
            actions += self._build_verify_webhook_actions(verify_webhook)
        if basic_auth:
            credentials = basic_auth if isinstance(basic_auth, list) else [basic_auth]
            actions.append({"type": "basic-auth", "config": {"credentials": credentials}})
        if host_header:
            actions.append({"type": "add-headers", "config": {"headers": {"host": host_header}}})

        if not actions:
            return {}

        # ngrok doesn't accept both a policy file and an inline policy, so these rules go first in one policy
        traffic_policy = self._load_traffic_policy_file()
        on_http_request = traffic_policy.get("on_http_request") or []
        traffic_policy["on_http_request"] = [{"actions": actions}] + on_http_request

        return traffic_policy

    def _build_verify_webhook_actions(self, verify_webhook: str) -> List[Dict[str, Any]]:
        provider, _, secret = verify_webhook.partition(":")
        verify_config = {"provider": provider, "enforce": False}
        if secret:
            verify_config["secret"] = secret

        # ngrok appends to existing headers, so a caller's own copy is removed before the result is added
        return [
            {"type": "remove-headers", "config": {"headers": [WEBHOOK_VERIFIED_HEADER]}},
            {"type": "verify-webhook", "config": verify_config},
            {"type": "add-headers",
             "config": {"headers": {WEBHOOK_VERIFIED_HEADER: "${actions.ngrok.verify_webhook.verified}"}}},
        ]

    def _load_traffic_policy_file(self) -> Dict[str, Any]:
        traffic_policy_file = self.config.get("traffic_policy_file")
        if not traffic_policy_file:
            return {}

        try:
            with open(traffic_policy_file) as f:
                traffic_policy = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError) as e:
            raise HookeeConfigError(f"Unable to read the Traffic Policy file {traffic_policy_file}: {e}")

        if not isinstance(traffic_policy, dict):
            raise HookeeConfigError(f"The Traffic Policy file {traffic_policy_file} must contain a YAML or JSON "
                                    f"object.")

        return traffic_policy

    def stop(self) -> None:
        """
        If running, kill the tunnel and cleanup its thread.
        """
        if self._thread:
            ngrok.kill()

            self.public_url = None
            self.ngrok_process = None
            self._thread = None

    def print_close_header(self) -> None:
        self.print_util.print_basic(
            f" * Tunnel: {self.public_url} -> http://127.0.0.1:{self.port}",
            print_when_logging=True)
        self.print_util.print_close_header()
