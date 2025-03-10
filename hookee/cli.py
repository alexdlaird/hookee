#!/usr/bin/env python

__copyright__ = "Copyright (c) 2020-2025 Alex Laird"
__license__ = "MIT"

import click
import platform

from hookee import HookeeManager, __version__, pluginmanager


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="[server] The local port for the webserver and ngrok tunnel.")
@click.option('--default-route', type=str, help="[server] The URI regex to map to the default webhook.")
@click.option('--no-tunnel', is_flag=True, default=False, help="Do not open an ngrok tunnel.")
@click.option("--response", type=str,
              help="[server] Data to set for the response, overriding all body data from plugins and "
                   "`--response-script`.")
@click.option("--content-type", type=str,
              help="[server] The \"Content-Type\" header to set when response body data is given with `--response`")
@click.option("--request-script", type=click.Path(exists=True),
              help="[server] A Python script whose `run(request)` method will be called by the default `/webhook` "
                   "after all request plugins have run.")
@click.option("--response-script", type=click.Path(exists=True),
              help="[server] A Python script whose `run(request, response)` method will be called by the default "
                   "`/webhook` after all response plugins have run.")
@click.option("--tunnel-name", help="[tunnel] The name to use for the ngrok tunnel.")
@click.option("--subdomain", help="[tunnel] The subdomain to use for ngrok endpoints.")
@click.option("--region", type=click.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"]),
              help="The region to use for ngrok endpoints.")
@click.option("--hostname", help="[tunnel] The domain to use for ngrok endpoints.")
@click.option("--auth", help="[tunnel] The basic auth to use for ngrok endpoints.")
@click.option("--host-header", help="[tunnel] The \"Host\" header value to use for ngrok endpoints.")
@click.option("--auth-token", help="[tunnel] A valid ngrok auth token.")
@click.option("--api-key", help="[tunnel] A valid ngrok API key.")
@click.option("--plugins-dir", type=click.Path(exists=True), help="The directory to scan for custom hookee plugins.")
@click.option("--plugins", multiple=True, help="A list of hookee plugins to use.")
@click.option('--version', is_flag=True, default=False, help="Display version information.")
def hookee(ctx, **kwargs):
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

    if kwargs.get("subdomain") and kwargs.get("hostname"):
        ctx.fail("Can't give both --subdomain and --hostname.")

    hookee_manager = HookeeManager(load_plugins=ctx.invoked_subcommand not in [enable_plugin.name,
                                                                               disable_plugin.name,
                                                                               available_plugins.name,
                                                                               enabled_plugins.name])
    ctx.obj["hookee_manager"] = hookee_manager

    if ctx.invoked_subcommand is None:
        hookee_manager.run()


@hookee.command()
@click.pass_context
def start(ctx):
    """
    Start hookee.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.run()


@hookee.command(
    short_help="Update the default value for a config. Any passable arg to hookee can also be given here to set its "
               "default in the config so it doesn't need to be passed to the hookee each time."
)
@click.pass_context
@click.argument("key")
@click.argument("value")
def update_config(ctx, key, value):
    """
    Update the default value for a config. Any passable arg to hookee can also be given here to set its
    default in the config so it doesn't need to be passed to the hookee each time.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    if key == "plugins":
        ctx.fail("Enable and disable plugins through the `enable-plugin` and `disable-plugin` commands.")
    if "-" in key:
        key = key.replace("-", "_")

    if value.isdigit():
        value = int(value)

    try:
        hookee_manager.config.set(key, value)

        hookee_manager.print_util.print_config_update(
            f"The default value for \"{key}\" has been updated in the config.")
    except KeyError:
        ctx.fail(f"No such key exists in the config: {key}")


@hookee.command()
@click.pass_context
@click.argument("plugin")
def enable_plugin(ctx, plugin):
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
def disable_plugin(ctx, plugin):
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
def available_plugins(ctx):
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
def enabled_plugins(ctx):
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
def authtoken(ctx, token):
    """
    Save the auth token to the config.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.config.set("auth_token", token)

    hookee_manager.print_util.print_config_update("The auth token has been set in the config.")


@hookee.command()
@click.pass_context
@click.argument("key")
def apikey(ctx, key):
    """
    Save the API key to the config.
    """
    hookee_manager = ctx.obj["hookee_manager"]

    hookee_manager.config.set("api_key", key)

    hookee_manager.print_util.print_config_update("The API key has been set in the config.")


if __name__ == "__main__":
    hookee(obj={})
