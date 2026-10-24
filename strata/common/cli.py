"""The command line's shared pieces: rendering a record, and stopping on a refusal.

Standard library only. A command builds a request, calls an operation and
renders the record it returns, or prints the record whole as JSON on
stdout and nothing else; a refusal is one line on stderr and exit status
1, and anything not named is a crash and stays one. Every strata command
reaches these through here, so they all read the same way. See
``docs/adr/0030``.
"""

import dataclasses
import json
import sys
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from typing import Any

from .errors import Refused, SchemaOutOfDate

#: What every command refuses on, whatever else it names: a refusal of its
#: own, and a store behind the code (docs/adr/0018).
ALWAYS: tuple[type[Exception], ...] = (Refused, SchemaOutOfDate)


def jsonable(record: Any) -> Any:
    """A record as JSON will take it: pydantic models and dataclasses as dicts."""
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    if dataclasses.is_dataclass(record) and not isinstance(record, type):
        return dataclasses.asdict(record)
    if isinstance(record, list | tuple):
        return [jsonable(item) for item in record]
    if isinstance(record, dict):
        return {str(k): jsonable(v) for k, v in record.items()}
    return record


def print_json(record: Any) -> None:
    """The record whole, on stdout, for a program; nothing else goes there."""
    print(json.dumps(jsonable(record), indent=2, sort_keys=True, default=str))


def emit(record: Any, render: Callable[[Any], Iterable[str]], *, as_json: bool) -> None:
    """Render the record for a person, or print it whole for a program."""
    if as_json:
        print_json(record)
        return
    for line in render(record):
        print(line)


def refuse(error: BaseException) -> int:
    """Say why on stderr, and the status a refusal exits with."""
    print(str(error), file=sys.stderr)
    return 1


def run(command: Callable[[], int | None], *errors: type[Exception]) -> int:
    """Run a command's body: its status, or 1 and one line on stderr for a refusal.

    For a ``main`` that returns its status. ``errors`` are the refusals the
    command knows; :data:`ALWAYS` is added.
    """
    try:
        return command() or 0
    except (*ALWAYS, *errors) as e:
        return refuse(e)


@contextmanager
def exit_on(*errors: type[Exception]):
    """Report a refusal and stop. For a command body that cannot return a status.

    Raises :class:`SystemExit` with status 1, which a typer app and a plain
    script both turn into the process's exit status.
    """
    try:
        yield
    except (*ALWAYS, *errors) as e:
        raise SystemExit(refuse(e)) from None


__all__ = ["ALWAYS", "emit", "exit_on", "jsonable", "print_json", "refuse", "run"]
