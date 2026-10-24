"""What a stage declares about itself: a name, a version, and the kinds it consumes and produces.

The kinds are opaque strings here; what they name is each package's business. See
``docs/adr/0046`` and ``docs/adr/0037``.
"""

from collections.abc import Callable
from typing import Any, NamedTuple


class Stage(NamedTuple):
    """One named, versioned operation, and the kinds it links."""

    name: str
    #: Bumped when a change moves the result; recorded beside the spec hash. docs/adr/0037
    version: str
    #: What must have been produced before it runs; empty for a stage starting from the catalog.
    consumes: tuple[str, ...]
    #: What it produces, for the next stage to consume.
    produces: str
    run: Callable[..., Any]


__all__ = ["Stage"]
