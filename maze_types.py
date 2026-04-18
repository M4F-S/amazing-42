from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

Coordinate: TypeAlias = tuple[int, int]
Direction: TypeAlias = str


@dataclass(frozen=True)
class Cell:
    """One maze cell.

    A wall value of True means the wall is closed.
    A wall value of False means the wall is open.
    """

    north: bool
    east: bool
    south: bool
    west: bool
    is_42: bool = False


@dataclass
class Maze:
    """Maze structure shared between generation and display code."""

    width: int
    height: int
    grid: list[list[Cell]]
    entry: Coordinate
    exit: Coordinate
    seed: int | None = None
