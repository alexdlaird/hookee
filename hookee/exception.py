__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.0.1"


class HookeeError(Exception):
    """
    Raised when a general ``hookee`` error has occurred.
    """
    pass


class HookeePluginValidationError(HookeeError):
    """
    Raised when a module fails to validate as a valid ``hookee`` plugin.
    """
    pass
