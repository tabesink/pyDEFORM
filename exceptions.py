"""
 User-defined exceptions
"""


class Error(Exception):
    """Base class for other exceptions"""
    pass


class MissingDEFREPORT(Error):
    """Raised when the input value is too large"""
    pass
