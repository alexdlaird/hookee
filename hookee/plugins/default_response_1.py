__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "0.0.2"


def call(request, response):
    print(response.status_code)
    print(response.headers)
    print(response.data)

    return response
