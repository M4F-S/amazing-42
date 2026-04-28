"""Backwards-compatible shim that re-exports the ``mazegen`` package API.

The implementation lives in ``mazegen/generator.py``. Existing imports
of the form ``from maze_generator import MazeGenerator`` continue to
work, while the same code is also installable as the standalone
``mazegen`` wheel (see ``pyproject.toml``).
"""

from mazegen.generator import (  # noqa: F401
    DIRECTIONS,
    EAST,
    MazeGenerator,
    NORTH,
    PATTERN_42,
    PATTERN_H,
    PATTERN_W,
    SOUTH,
    WEST,
)

__all__ = [
    "DIRECTIONS",
    "EAST",
    "MazeGenerator",
    "NORTH",
    "PATTERN_42",
    "PATTERN_H",
    "PATTERN_W",
    "SOUTH",
    "WEST",
]
