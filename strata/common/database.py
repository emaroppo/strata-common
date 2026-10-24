"""Opening an engine the way every strata database wants it opened.

SQLite gets WAL, ``synchronous=NORMAL`` and ``foreign_keys=ON``; any other dialect gets
``create_engine`` and nothing more. See ``docs/adr/0021``.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


def engine(url: str, *, foreign_keys: bool = True) -> Engine:
    """An engine on ``url``, with SQLite tuned for writes and concurrent reads.

    ``foreign_keys`` is off for a store whose schema declares a reference it cannot enforce, as
    the run store's parent may live elsewhere. See ``docs/adr/0005``.
    """
    made = create_engine(url)
    if made.dialect.name == "sqlite":

        @event.listens_for(made, "connect")
        def _pragmas(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            if foreign_keys:
                # Off by default in SQLite, which leaves every ON DELETE CASCADE inert.
                cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return made


__all__ = ["engine"]
