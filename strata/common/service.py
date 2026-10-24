"""Starting an app from the environment, and refusing to start degraded.

The consumer's ``build()`` raises, and this turns the raise into a message
on stderr and exit status 2. See ``docs/adr/0019``.
"""

import os
import sys
from collections.abc import Callable
from typing import Any

from .errors import SchemaOutOfDate

#: Where a service listens; the port defaults to each consumer's own. docs/adr/0019
HOST_ENV = "STRATA_SERVE_HOST"
PORT_ENV = "STRATA_SERVE_PORT"


def serve(build: Callable[[], Any], *, prog: str, port: int, error: type[Exception]) -> None:
    """Build the app, then serve it until stopped.

    ``error`` is what ``build`` raises when a setting it cannot start without is absent; a store
    behind the code is refused the same way. See ``docs/adr/0018``.
    """
    import uvicorn  # pyright: ignore[reportMissingImports]  (the service extra)

    try:
        app = build()
    except (error, SchemaOutOfDate) as e:
        print(f"{prog}: {e}", file=sys.stderr)
        raise SystemExit(2) from None

    uvicorn.run(
        app,
        host=os.environ.get(HOST_ENV, "0.0.0.0"),
        port=int(os.environ.get(PORT_ENV, str(port))),
    )


__all__ = ["HOST_ENV", "PORT_ENV", "serve"]
