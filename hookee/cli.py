#!/usr/bin/env python

__copyright__ = "Copyright (c) 2020-2025 Alex Laird"
__license__ = "MIT"

import platform
import signal
from types import FrameType
from typing import Any, NoReturn, Optional, Union

import click

from hookee import HookeeManager, __version__, pluginmanager


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="[server] The local port for the webserver and ngrok tunnel.")
@click.option('--default-route', type=str, help="[server] The URI regex to map to the default webhook.")
@click.option('--no-tunnel', is_flag=True, default=False, help="Do not open an ngrok tunnel.")
@click.option("--response", type=str,
              help="[server] Data to set for the response, overriding all body data from plugins and "
                   "`--response-script`.")
@click.option("--response-file", type=click.Path(exists=True, dir_okay=False),
              help="[server] A file whose contents to set for the response, overriding all body data from plugins and "
                   "`--response-script`. Its \"Content-Type\" is guessed from its extension, unless `--content-type` "
                   "is given.")
@click.option("--content-type", type=str,
              help="[server] The \"Content-Type\" header to set when response body data is given with `--response` or "
                   "`--response-file`.")
@click.option("--status-code", type=int, help="[server] The status code to set for the response.")
@click.option("--response-header", "response_headers", multiple=True,
              help="[server] A \"Name: value\" header to set on the response. Can be given multiple times.")
@click.option("--delay", type=float, help="[server] Seconds to wait before sending the response.")
@click.option("--response-route",
              help="[server] A regex for the \"METHOD /path\" of requests to apply the response options to, like "
                   "\"^GET /planner/\". If not given, they apply to all requests.")
@click.option("--forward-to",
              help="[server] The base URL of your app, like \"http://localhost:8000\", to forward every request to, "
                   "with its path and query string. Your app's response is sent back to the caller.")
@click.option("--save-dir", type=click.Path(file_okay=False),
              help="[server] A directory to save each request, and the response sent for it, to as a JSON file.")
@click.option("--show-sensitive-headers", is_flag=True, default=False,
              help="[server] Show and save headers that carry credentials, like \"Authorization\" and "
                   "\"Cookie\", instead of masking them.")
@click.option("--request-script", type=click.Path(exists=True),
              help="[server] A Python script whose `run(request)` method will be called by the default `/webhook` "
                   "after all request plugins have run.")
@click.option("--response-script", type=click.Path(exists=True),
              help="[server] A Python script whose `run(request, response)` method will be called by the default "
                   "`/webhook` after all response plugins have run.")
@click.option("--tunnel-name", help="[tunnel] The name to use for the ngrok tunnel.")
@click.option("--url", help="[tunnel] The URL (or domain) to use for the ngrok endpoint.")
@click.option("--region",
              help="[tunnel] The region to start the ngrok agent in. If not given, ngrok chooses the lowest latency "
                   "region.")
@click.option("--basic-auth", help="[tunnel] The \"username:password\" basic auth to require on the ngrok endpoint.")
@click.option("--host-header", help="[tunnel] The \"Host\" header value to use for ngrok endpoints.")
@click.option("--verify-webhook",
              help="[tunnel] A \"provider:secret\" to verify webhook signatures with ngrok. Requests are never "
                   "blocked, but each shows whether it was verified.")
@click.option("--traffic-policy-file", type=click.Path(exists=True),
              help="[tunnel] A YAML or JSON ngrok Traffic Policy file to apply to the ngrok endpoint.")
@click.option("--pooling-enabled", is_flag=True, default=False,
              help="[tunnel] Allow multiple hookee instances to share the same ngrok endpoint URL.")
@click.option("--auth-token", help="[tunnel] A valid ngrok auth token.")
@click.option("--api-key", help="[tunnel] A valid ngrok API key.")
@click.option("--plugins-dir", type=click.Path(exists=True), help="The directory to scan for custom hookee plugins.")
@click.option("--plugins", multiple=True, help="A list of hookee plugins to use.")
@click.option('--version', is_flag=True, default=False, help="Display version information.")
def hookee(ctx: click.Context, **kwargs: Any) -> None:
    """
    hookee is a utility that provides command line webhooks, on demand! Bind port to intercept requests,
    dump request data to the console, process requests and responses, customize response data, and configure hookee and
    its routes further in any number of ways through custom plugins.

    hookee can be started by using `hookee start` or simply hookee.

    If options are given, they override the default values derived from the config file.

    hookee documentation can be found at https://hookee.readthedocs.io.
    """
    if kwargs["version"]:
        click.echo(f"hookee/{__version__} Python/{platform.python_version()}")
        ctx.exit(0)

    ctx.ensure_object(dict)
    for key, value in kwargs.items():
        if value:
            ctx.obj[key] = value

    hookee_manager = HookeeManager(load_plugins=ctx.invoked_subcommand not in [enable_plugin.name,
                                                                               disable_plugin.name,
                                                                               available_plugins.name,
                                                                               enabled_plugins.name])
    ctx.obj["hookee_manager"] = hookee_manager

    if ctx.invoked_subcommand is None:
        _run_until_stopped(hookee_manager)


@hookee.command()
@click.pass_context
def start(ctx: click.Context) -> None:
    """
    Start hookee.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    _run_until_stopped(hookee_manager)


@hookee.command(
    short_help="Update the default value for a config. Any passable arg to hookee can also be given here to set its "
               "default in the config so it doesn't need to be passed to the hookee each time."
)
@click.pass_context
@click.argument("key")
@click.argument("value")
def update_config(ctx: click.Context, key: str, value: str) -> None:
    """
    Update the default value for a config. Any passable arg to hookee can also be given here to set its
    default in the config so it doesn't need to be passed to the hookee each time.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    if key == "plugins":
        ctx.fail("Enable and disable plugins through the `enable-plugin` and `disable-plugin` commands.")
    if "-" in key:
        key = key.replace("-", "_")

    config_value: Union[str, int] = int(value) if value.isdigit() else value

    try:
        hookee_manager.config.set(key, config_value)

        hookee_manager.print_util.print_config_update(
            f"The default value for \"{key}\" has been updated in the config.")
    except KeyError:
        ctx.fail(f"No such key exists in the config: {key}")


@hookee.command()
@click.pass_context
@click.argument("plugin")
def enable_plugin(ctx: click.Context, plugin: str) -> None:
    """
    Enable the given plugin by default.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.plugin_manager.get_plugin(plugin)

    hookee_manager.config.append("plugins", plugin)

    hookee_manager.print_util.print_config_update(f"Plugin \"{plugin}\" has been enabled.")


@hookee.command()
@click.pass_context
@click.argument("plugin")
def disable_plugin(ctx: click.Context, plugin: str) -> None:
    """
    Disable the given plugin by default.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    if plugin in pluginmanager.REQUIRED_PLUGINS:
        ctx.fail(f"Can't disable the plugin \"{plugin}\".")

    hookee_manager.config.remove("plugins", plugin)

    hookee_manager.print_util.print_config_update(f"Plugin \"{plugin}\" is disabled.")


@hookee.command()
@click.pass_context
def available_plugins(ctx: click.Context) -> None:
    """
    List all available plugins.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    plugins = hookee_manager.plugin_manager.available_plugins()

    hookee_manager.print_util.print_open_header("Available Plugins")

    for plugin_name in plugins:
        hookee_manager.print_util.print_basic(f" * {plugin_name}")

        try:
            plugin = hookee_manager.plugin_manager.get_plugin(plugin_name)
            if plugin.description:
                hookee_manager.print_util.print_basic(f"   Description: {plugin.description}")
        except Exception as e:
            hookee_manager.print_util.print_basic(f"   Error: {e}")

    hookee_manager.print_util.print_close_header()
    hookee_manager.print_util.print_basic()


@hookee.command()
@click.pass_context
def enabled_plugins(ctx: click.Context) -> None:
    """
    List all enabled plugins.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    plugins = hookee_manager.plugin_manager.enabled_plugins()

    hookee_manager.print_util.print_open_header("Enabled Plugins (Order of Execution)")

    for plugin_name in plugins:
        hookee_manager.print_util.print_basic(f" * {plugin_name}")

        try:
            plugin = hookee_manager.plugin_manager.get_plugin(plugin_name)
            if plugin.description:
                hookee_manager.print_util.print_basic(f"   Description: {plugin.description}")
        except Exception as e:
            hookee_manager.print_util.print_basic(f"   Error: {e}")

    hookee_manager.print_util.print_close_header()
    hookee_manager.print_util.print_basic()


@hookee.command()
@click.pass_context
@click.argument("token")
def authtoken(ctx: click.Context, token: str) -> None:
    """
    Save the auth token to the config.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.config.set("auth_token", token)

    hookee_manager.print_util.print_config_update("The auth token has been set in the config.")


@hookee.command()
@click.pass_context
@click.argument("key")
def apikey(ctx: click.Context, key: str) -> None:
    """
    Save the API key to the config.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.config.set("api_key", key)

    hookee_manager.print_util.print_config_update("The API key has been set in the config.")


def _run_until_stopped(hookee_manager: HookeeManager) -> None:
    signal.signal(signal.SIGTERM, _raise_keyboard_interrupt)

    hookee_manager.run()


def _raise_keyboard_interrupt(signum: int, frame: Optional[FrameType]) -> NoReturn:
    raise KeyboardInterrupt


if __name__ == "__main__":
    hookee(obj={})
