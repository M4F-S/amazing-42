from dataclasses import dataclass
from typing import Dict, List, Tuple

Coordinate = tuple[int, int]
Direction = str  # "N", "E", "S", "W"


@dataclass(frozen=True)
class Cell:
    north: bool
    east: bool
    south: bool
    west: bool
    is_42: bool = False


@dataclass
class Maze:
    width: int
    height: int
    grid: List[List[Cell]]
    entry: Coordinate
    exit: Coordinate
    seed: int | None = None
