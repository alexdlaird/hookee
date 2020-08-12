import time

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
            print("{}\n".format("-" * 70))

            self.server.start()

            print("")

            self.tunnel.start()

            print(
                " * Ready! Send requets to {}/webhook\n\n{}\n".format(
                    self.tunnel.public_url.replace("http://", "https://"), "-" * 70))

            self.alive = True

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
