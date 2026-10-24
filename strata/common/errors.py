"""The errors every strata command and service has to recognise.

Dependency-free, so a command line or a service bootstrap can catch them without importing
the module that raises them. See ``docs/adr/0018`` and ``docs/adr/0030``.
"""


class Refused(Exception):
    """A reason the command stopped, for the user rather than a traceback."""


class SchemaOutOfDate(Exception):
    """A database whose schema is not the one this code was written against."""


__all__ = ["Refused", "SchemaOutOfDate"]
