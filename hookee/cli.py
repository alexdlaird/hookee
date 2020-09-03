from types import ModuleType

import click

from hookee.climanager import CliManager

from future.utils import iteritems

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.7"


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="The port for the local webserver.")
@click.option("--plugins_dir", type=click.Path(exists=True), help="The directory to scan for custom `hookee` plugins.")
@click.option("--plugins", multiple=True, help="A list of `hookee` plugins to use.")
@click.option("--auth_token", help="The `ngrok` auth token use.")
@click.option("--region", type=click.Choice(["us", "eu", "ap", "au", "sa", "jp", "in"]),
              help="The `ngrok` region to use.")
@click.option("--subdomain", help="The `ngrok` subdomain token use.")
@click.option("--auth", help="The `ngrok` auth token use for endpoints.")
@click.option("--last_request", type=click.Path(exists=True),
              help="A Python script, where last_request.run(request) will be called after all plugins have processed a request to the default `/webhook`.")
@click.option("--last_response", type=click.Path(exists=True),
              help="A Python script, where last_response.run(request, response) will be called after all plugins have generated the default `/webhook`'s response.")
def hookee(ctx, **kwargs):
    """
    If options are given, they override the default values derived from the config file.
    """
    ctx.ensure_object(dict)
    for key, value in iteritems(kwargs):
        if value:
            ctx.obj[key] = value

    manager = CliManager(ctx)
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
@click.argument("plugins_dig")
def set_plugins_dir(ctx, plugins_dir):
    """
    Set the default directory to use for `hookee` plugins.
    """
    manager = ctx.obj["cli_manager"]

    manager.config.set("plugins_dir", plugins_dir)

    manager.print_util.print_config_update("Plugins dir has been updated.")


@hookee.command()
@click.pass_context
@click.argument("plugin")
def enable_plugin(ctx, plugin):
    """
    Enable the given plugin by default.
    """
    cli_manager = ctx.obj["cli_manager"]

    cli_manager.validate_plugin(cli_manager.source.load_plugin(plugin))

    cli_manager.config.append("plugins", plugin)

    cli_manager.print_util.print_config_update("Plugin \"{}\" has been enabled.".format(plugin))


@hookee.command()
@click.pass_context
@click.argument("plugin")
def disable_plugin(ctx, plugin):
    """
    Disable the given plugin by default.
    """
    manager = ctx.obj["cli_manager"]

    # TODO: because the manager is initialized in the main group, plugins are validated prior to this execute, but
    #   if trying to disable a plugin that is no longer valid, this will always fail

    manager.config.remove("plugins", plugin)

    manager.print_util.print_config_update("Plugin \"{}\" has been disabled.".format(plugin))


@hookee.command()
@click.pass_context
@click.argument("auth_token")
def set_auth_token(ctx, auth_token):
    """
    Set the default `ngrok` auth token.
    """
    manager = ctx.obj["cli_manager"]

    manager.config.set("auth_token", auth_token)

    manager.print_util.print_config_update("Default auth token has been set.")


if __name__ == "__main__":
    hookee(obj={})
