"""Opening an engine the way every strata database wants it opened.

SQLite gets WAL and ``synchronous=NORMAL`` for the bulk write, and
``foreign_keys=ON`` so the schema's cascades hold there as they do on
Postgres; on any other dialect this is ``create_engine`` and nothing more.
See ``docs/adr/0021``.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


def engine(url: str) -> Engine:
    """An engine on ``url``, with SQLite tuned for writes and concurrent reads."""
    made = create_engine(url)
    if made.dialect.name == "sqlite":

        @event.listens_for(made, "connect")
        def _pragmas(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            # Off by default in SQLite, so every ON DELETE CASCADE in the
            # tables was inert there and orphaned rows on a delete.
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return made


__all__ = ["engine"]
