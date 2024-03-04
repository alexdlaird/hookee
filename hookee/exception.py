__copyright__ = "Copyright (c) 2020-2024 Alex Laird"
__license__ = "MIT"


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
