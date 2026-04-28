"""mazegen - reusable maze generator for the amazing-42 project.

Public API:

    from mazegen import MazeGenerator

    gen = MazeGenerator(width=20, height=20, seed=42, perfect=True)
    gen.generate(entry=(0, 0), exit_=(19, 19))
    path = gen.solve(entry=(0, 0), exit_=(19, 19))
    print(gen.to_hex_string())

The wall-bit constants (``NORTH``, ``EAST``, ``SOUTH``, ``WEST``) and
the pattern constants are also re-exported for callers that want to
inspect the grid directly.
"""

from mazegen.generator import (
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

__version__ = "1.0.0"

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
    "__version__",
]
