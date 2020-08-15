import time

import click

from hookee import conf
from hookee.server import Server
from hookee.tunnel import Tunnel


class Manager:
    __instance = None

    @staticmethod
    def get_instance(port):
        if Manager.__instance is None:
            Manager(port)
        return Manager.__instance

    def __init__(self, port):
        if Manager.__instance is not None:
            raise Exception("The Manager is already instantiated, use get_instance().")
        else:
            Manager.__instance = self

            self.port = port

            self.tunnel = Tunnel(self.port)
            self.server = Server(self.port)

            self.alive = False

    def start(self):
        if not self.alive:
            self.server.start()

            self.tunnel.start()

            self.alive = True

            self._banner()

    def wait_for_signal(self):
        try:
            while self.alive:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def stop(self):
        if self.alive:
            self.server.stop()
            self.tunnel._thread.alive = False

            # Wait for the other threads to teardown
            while self.server._thread and self.tunnel._thread:
                time.sleep(1)

            self.alive = False

    def _banner(self):
        # TODO: refactor all these reused dynamic title widths to helper function
        title = "Endpoints Ready for Requests"
        width = int((conf.CONSOLE_WIDTH - len(title)) / 2)

        click.echo("")
        click.secho("{}{}{}".format("-" * width, title, "-" * width), fg="blue", bold=True)
        click.echo("")

        rules = list(filter(lambda r: r.rule not in ["/shutdown", "/static/<path:filename>", "/status"],
                            self.server.app.url_map.iter_rules()))
        for rule in rules:
            click.secho("--> {}{} - {}".format(self.tunnel.public_url, rule.rule, sorted(list(rule.methods))),
                        fg="blue",
                        bold=True)

        click.echo("")
        click.secho("-" * conf.CONSOLE_WIDTH, fg="blue", bold=True)
        click.echo("\n")
