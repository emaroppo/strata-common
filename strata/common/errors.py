"""The errors every strata command and service has to recognise.

Dependency-free, so a command line or a service bootstrap can catch them
without importing the module that raises them. :class:`SchemaOutOfDate` is
raised by :mod:`strata.common.migrations`, which needs alembic;
:class:`Refused` is what a command raises when it stops for a reason the
user reads rather than a traceback. See ``docs/adr/0018`` and
``docs/adr/0030``.
"""


class Refused(Exception):
    """A reason the command stopped, for the user rather than a traceback."""


class SchemaOutOfDate(Exception):
    """A database whose schema is not the one this code was written against."""


__all__ = ["Refused", "SchemaOutOfDate"]
