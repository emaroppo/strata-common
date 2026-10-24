"""What two strata packages need and neither owns.

Each module is importable on its own: :mod:`migrations` runs an alembic chain from a wheel,
:mod:`database` opens an engine tuned for SQLite, :mod:`service` starts an app from the
environment, :mod:`plugins` resolves a name through an entry-point group, :mod:`canonical` is
the JSON form that gets hashed, :mod:`contract` the payload every hasher pins, :mod:`cli` what
every command line shares, :mod:`stages` what a stage declares, and :mod:`errors` what every
command and service recognises. See ``docs/adr/0017``.
"""

#: Every module here is importable on its own. docs/adr/0015
PUBLIC_MODULES = frozenset(
    {
        "canonical",
        "cli",
        "contract",
        "database",
        "errors",
        "migrations",
        "plugins",
        "service",
        "stages",
    }
)
