__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "1.2.0"


class HookeeError(Exception):
    """
    Raised when a general ``hookee`` error has occurred.
    """
    pass


class HookeeConfigError(HookeeError):
    """
    Raised when there is an error initializing ``hookee` configuration.
    """
    pass


class HookeePluginValidationError(HookeeError):
    """
    Raised when a module fails to validate as a valid ``hookee`` plugin.
    """
    pass
