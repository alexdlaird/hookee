from pyngrok import ngrok
from pyngrok.conf import PyngrokConfig

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.1"


def start_tunnel(port):
    public_url = ngrok.connect(port, pyngrok_config=PyngrokConfig(monitor_thread=False))
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))
    print(" * send requests to \"{}/webhook\" for inspection".format(public_url))
