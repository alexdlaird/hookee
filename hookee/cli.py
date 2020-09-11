import platform

import click

from hookee import pluginmanager
from hookee.climanager import CliManager

from future.utils import iteritems

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.0.1"


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="The local port for the webserver and ngrok tunnel.")
@click.option("--subdomain", help="The subdomain to use for ngrok endpoints.")
@click.option("--region", type=click.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"]),
              help="The region to use for ngrok endpoints.")
@click.option("--hostname", help="The hostname to use for ngrok endpoints.")
@click.option("--auth", help="The basic auth to use for ngrok endpoints.")
@click.option("--host_header", help="The \"Host\" header value to use for ngrok endpoints.")
@click.option("--response", type=str,
              help="Data to set for the response, overriding all body data from plugins and `--response-script`.")
@click.option("--content-type", type=str,
              help="The \"Content-Type\" header to set when response body data is given with `--response`")
@click.option("--request-script", type=click.Path(exists=True),
              help="A Python script whose `run(request)` method will be called by the default `/webhook` after all request plugins have run.")
@click.option("--response-script", type=click.Path(exists=True),
              help="A Python script whose `run(request, response)` method will be called by the default `/webhook` after all response plugins have run.")
@click.option("--auth-token", help="A valid ngrok auth token.")
@click.option("--plugins-dir", type=click.Path(exists=True), help="The directory to scan for custom hookee plugins.")
@click.option("--plugins", multiple=True, help="A list of hookee plugins to use.")
@click.option('--version', is_flag=True, default=False, help="Display version information.")
def hookee(ctx, **kwargs):
    """
    hookee is a utility that provides command line webhooks, on demand! Dump useful request data to the
    console, process requests and responses, customize response data, and configure hookee and its routes
    further in any number of ways through custom plugins.

    hookee can be started by using `hookee start` or simply hookee.

    If options are given, they override the default values derived from the config file.

    hookee documentation can be found at https://hookee.readthedocs.io.
    """
    if kwargs["version"]:
        ctx.exit("hookee/{} Python/{}".format(__version__, platform.python_version()))

    ctx.ensure_object(dict)
    for key, value in iteritems(kwargs):
        if value:
            ctx.obj[key] = value

    if kwargs.get("subdomain") and kwargs.get("hostname"):
        ctx.fail("Can't give both --subdomain and --hostname.")

    cli_manager = CliManager(ctx, load_plugins=ctx.invoked_subcommand not in ["enable-plugin", "disable-plugin",
                                                                              "available-plugins", "enabled-plugins"])
    ctx.obj["cli_manager"] = cli_manager

    if ctx.invoked_subcommand is None:
        cli_manager.start()


@hookee.command()
@click.pass_context
def start(ctx):
    """
    Start hookee.
    """
    cli_manager = ctx.obj["cli_manager"]

    cli_manager.start()


@hookee.command(
    short_help="Update the default value for a config. Any passable arg to hookee can also be given here to set its default in the config so it doesn't need to be passed to the hookee each time."
)
@click.pass_context
@click.argument("key")
@click.argument("value")
def update_config(ctx, key, value):
    """
    Update the default value for a config. Any passable arg to hookee can also be given here to set its
    default in the config so it doesn't need to be passed to the hookee each time.
    """
    cli_manager = ctx.obj["cli_manager"]

    if key == "plugins":
        ctx.fail("Enable and disable plugins through the `enable-plugin` and `disable-plugin` commands.")
    if "-" in key:
        key = key.replace("-", "_")

    if value.isdigit():
        value = int(value)

    try:
        cli_manager.config.set(key, value)

        cli_manager.print_util.print_config_update(
            "The default value for \"{}\" has been updated in the config.".format(key))
    except KeyError:
        ctx.fail("No such key exists in the config: {}".format(key))


@hookee.command()
@click.pass_context
@click.argument("plugin")
def enable_plugin(ctx, plugin):
    """
    Enable the given plugin by default.
    """
    cli_manager = ctx.obj["cli_manager"]

    cli_manager.plugin_manager.get_plugin(plugin)

    cli_manager.config.append("plugins", plugin)

    cli_manager.print_util.print_config_update("Plugin \"{}\" has been enabled.".format(plugin))


@hookee.command()
@click.pass_context
@click.argument("plugin")
def disable_plugin(ctx, plugin):
    """
    Disable the given plugin by default.
    """
    cli_manager = ctx.obj["cli_manager"]

    if plugin in pluginmanager.REQUIRED_PLUGINS:
        ctx.fail("Can't disable the plugin \"{}\".".format(plugin))

    cli_manager.config.remove("plugins", plugin)

    cli_manager.print_util.print_config_update("Plugin \"{}\" is disabled.".format(plugin))


@hookee.command()
@click.pass_context
def available_plugins(ctx):
    """
    List all available plugins.
    """
    cli_manager = ctx.obj["cli_manager"]

    plugins = cli_manager.plugin_manager.available_plugins()

    click.secho("\nAvailable Plugins: {}\n".format(plugins),
                fg="green")


@hookee.command()
@click.pass_context
def enabled_plugins(ctx):
    """
    List all enabled plugins.
    """
    cli_manager = ctx.obj["cli_manager"]

    plugins = cli_manager.plugin_manager.enabled_plugins()

    click.secho("\nEnabled Plugins: {}\n".format(plugins), fg="green")


if __name__ == "__main__":
    hookee(obj={})
