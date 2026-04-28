from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from mazegen import Cell

Coordinate: TypeAlias = tuple[int, int]
Direction: TypeAlias = str


@dataclass
class Maze:
    """Maze structure shared between generation and display code."""

    width: int
    height: int
    grid: list[list[Cell]]
    entry: Coordinate
    exit: Coordinate
    seed: int | None = None


__all__ = ["Cell", "Coordinate", "Direction", "Maze"]
