import click

from hookee.manager import Manager

from future.utils import iteritems

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.6"


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--port", type=int, help="The port for the local webserver.")
@click.option("--plugins_dir", help="The directory to scan for custom `hookee` plugins.")
@click.option("--plugins", multiple=True, help="A list of `hookee` plugins to enable.")
@click.option("--auth_token", help="The `ngrok` auth token use.")
def hookee(ctx, **kwargs):
    """
    If options are given, they override the default values derived from the config file.
    """
    ctx.ensure_object(dict)
    for key, value in iteritems(kwargs):
        if value:
            ctx.obj[key] = value

    manager = Manager(ctx)

    if ctx.invoked_subcommand is None:
        manager.start()
    else:
        ctx.obj["manager"] = manager


@hookee.command()
@click.pass_context
def start(ctx):
    """
    Start `hookee`.
    """
    manager = ctx.obj["manager"]

    manager.start()


@hookee.command()
@click.pass_context
@click.argument("plugins_dig")
def set_plugins_dir(ctx, plugins_dir):
    """
    Set the default directory to be scanned for plugins.
    """
    manager = ctx.obj["manager"]

    manager.config.set("plugins_dir", plugins_dir)

    manager.print_util.print_config_update("Plugins dir has been updated.")


@hookee.command()
@click.pass_context
@click.argument("plugin")
def enable_plugin(ctx, plugin):
    """
    Enable the given plugin by default.
    """
    manager = ctx.obj["manager"]

    manager.validate_plugin(plugin)

    manager.config.append("plugins", plugin)

    manager.print_util.print_config_update("Plugin \"{}\" has been enabled.".format(plugin))


@hookee.command()
@click.pass_context
@click.argument("plugin")
def disable_plugin(ctx, plugin):
    """
    Disable the given plugin by default.
    """
    manager = ctx.obj["manager"]

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
    manager = ctx.obj["manager"]

    manager.config.set("auth_token", auth_token)

    manager.print_util.print_config_update("Default auth token has been set.")


if __name__ == "__main__":
    hookee(obj={})
