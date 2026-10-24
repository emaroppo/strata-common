"""Resolving a name through an entry-point group, for sample types, preparers and models.

Takes the entries rather than the group, so a consumer keeps the one seam its tests patch.
See ``docs/adr/0033``.
"""

from collections.abc import Collection, Iterable
from importlib.metadata import EntryPoint
from pathlib import Path
from typing import Any


def available(entries: Iterable[EntryPoint]) -> dict[str, str]:
    """Registered names, and what each resolves to. See ``docs/adr/0034``."""
    return {entry.name: entry.value for entry in entries}


def find(
    entries: Iterable[EntryPoint],
    name: str,
    *,
    what: str,
    error: type[Exception],
    reserved: Collection[str] = (),
    hint: str = "",
) -> EntryPoint:
    """The one entry ``name`` refers to, not yet loaded.

    ``what`` names the kind of thing for the message and ``hint`` is appended when nothing
    matches; a name in ``reserved`` belongs to the owning package, and a plugin registering it is
    refused. See ``docs/adr/0033``.
    """
    entries = list(entries)
    matches = [entry for entry in entries if entry.name == name]
    if not matches:
        known = ", ".join(sorted(available(entries))) or "none"
        raise error(f"No {what} named {name!r}. Installed here: {known}.{hint}")
    if len(matches) > 1:
        owners = ", ".join(_owner(entry) for entry in matches)
        detail = (
            f"{name!r} is built in and cannot be replaced"
            if name in reserved
            else f"{name!r} is registered more than once"
        )
        raise error(f"{detail} (from: {owners}).")
    return matches[0]


def load(entry: EntryPoint, base: type, *, error: type[Exception]) -> type:
    """What the entry names, checked to be a subclass of ``base``.

    An import failure propagates as it is; a caller with something to add wraps it.
    """
    loaded = entry.load()
    if not (isinstance(loaded, type) and issubclass(loaded, base)):
        raise error(f"{entry.name!r} resolves to {loaded!r}, which is not a {base.__name__}.")
    return loaded


def _owner(entry: EntryPoint) -> str:
    return getattr(getattr(entry, "dist", None), "name", "?")


def anchor(ref: str, root: Path | None = None) -> str:
    """``ref`` with a ``file.py:Class`` target made absolute against ``root``.

    A registry name or a ``pkg.mod:Class`` path comes back as it is. See ``docs/adr/0005``.
    """
    if ":" not in ref:
        return ref
    target, name = ref.rsplit(":", 1)
    if not target.endswith(".py"):
        return ref
    path = Path(target)
    if not path.is_absolute() and root is not None:
        path = Path(root) / path
    return f"{path.resolve()}:{name}"


def anchor_all(value: Any, root: Path | None = None) -> Any:
    """``value`` with every ``file.py:Class`` string in it anchored, through dicts and lists."""
    if isinstance(value, dict):
        return {k: anchor_all(v, root) for k, v in value.items()}
    if isinstance(value, list):
        return [anchor_all(v, root) for v in value]
    if isinstance(value, str) and ".py:" in value:
        return anchor(value, root)
    return value


__all__ = ["anchor", "anchor_all", "available", "find", "load"]
