import click

from hookee.climanager import CliManager

from future.utils import iteritems

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.8"


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="The port for the local webserver.")
@click.option("--plugins-dir", type=click.Path(exists=True), help="The directory to scan for custom `hookee` plugins.")
@click.option("--plugins", multiple=True, help="A list of `hookee` plugins to use.")
@click.option("--auth-token", help="The `ngrok` auth token use.")
@click.option("--region", type=click.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"]),
              help="The `ngrok` region to use.")
@click.option("--subdomain", help="The `ngrok` subdomain token use.")
@click.option("--auth", help="The `ngrok` auth token use for endpoints.")
@click.option("--request-script", type=click.Path(exists=True),
              help="A Python script whose `run(request)` method will be called by the default `/webhook` after all request plugins have run.")
@click.option("--response-script", type=click.Path(exists=True),
              help="A Python script whose `run(request, response)` method will be called by the default `/webhook` after all response plugins have run.")
@click.option("--response", type=str,
              help="Data to set for the response, will override all body data from plugins and `--response_script`.")
@click.option("--content-type", type=str,
              help="The \"Content-Type\" header to set when response body data is given with `--response` (defaults to \"text/plain\")")
def hookee(ctx, **kwargs):
    """
    If options are given, they override the default values derived from the config file.

    `hookee` documentation can be found at https://hookee.readthedocs.io.
    """
    ctx.ensure_object(dict)
    for key, value in iteritems(kwargs):
        if value:
            ctx.obj[key] = value

    manager = CliManager(ctx, load_plugins=ctx.invoked_subcommand not in ["enable-plugin", "disable-plugin"])
    ctx.obj["cli_manager"] = manager

    if ctx.invoked_subcommand is None:
        manager.start()


@hookee.command()
@click.pass_context
def start(ctx):
    """
    Start `hookee`.
    """
    manager = ctx.obj["cli_manager"]

    manager.start()


@hookee.command()
@click.pass_context
@click.argument("key")
@click.argument("value")
def update_config(ctx, key, value):
    """
    Update the default value for a config.
    """
    manager = ctx.obj["cli_manager"]

    try:
        manager.config_data.set(key, value)

        manager.print_util.print_config_update(
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

    loaded_plugin = cli_manager.plugin_manager.source.load_plugin(plugin)

    cli_manager.plugin_manager.validate_plugin(loaded_plugin)

    cli_manager.config_data.append("plugins", plugin)

    cli_manager.print_util.print_config_update("Plugin \"{}\" has been enabled.".format(plugin))


@hookee.command()
@click.pass_context
@click.argument("plugin")
def disable_plugin(ctx, plugin):
    """
    Disable the given plugin by default.
    """
    manager = ctx.obj["cli_manager"]

    if plugin in manager.plugin_manager.REQUIRED_PLUGINS:
        ctx.fail("Sorry, you can't disable the plugin {}.".format(plugin))

    manager.config_data.remove("plugins", plugin)

    manager.print_util.print_config_update("Plugin \"{}\" has been disabled.".format(plugin))


@hookee.command()
@click.pass_context
def list_plugins(ctx):
    """
    List all available plugins.
    """
    cli_manager = ctx.obj["cli_manager"]

    plugins = sorted(cli_manager.plugin_manager.source.list_plugins())

    click.secho("\nAvailable Plugins: {}\n".format(plugins),
                fg="green")


@hookee.command()
@click.pass_context
def enabled_plugins(ctx):
    """
    List all enabled plugins.
    """
    cli_manager = ctx.obj["cli_manager"]

    plugins = sorted(cli_manager.config_data.get("plugins"))

    click.secho("\nEnabled Plugins: {}\n".format(plugins), fg="green")


if __name__ == "__main__":
    hookee(obj={})
