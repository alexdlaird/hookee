from datetime import datetime

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.2"


def call(request):
    now = datetime.now()
    print("{} - {} \"{} {}\"".format(request.host, now.strftime("%d/%m/%Y %H:%M:%S"), request.method, request.base_url))
