"""Maze generator: DFS backtracker, BFS solver, hex export, '42' stencil."""

from __future__ import annotations

import random
import sys
from collections import deque
from dataclasses import dataclass


# Wall bits per cell. A bit set to 1 means the wall is closed.
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# (dx, dy, my-side wall, neighbour-side wall)
DIRECTIONS: list[tuple[int, int, int, int]] = [
    (0, -1, NORTH, SOUTH),
    (1, 0, EAST, WEST),
    (0, 1, SOUTH, NORTH),
    (-1, 0, WEST, EAST),
]


_DIGIT_4: list[list[int]] = [
    [1, 0, 1, 0],
    [1, 0, 1, 0],
    [1, 1, 1, 1],
    [0, 0, 1, 0],
    [0, 0, 1, 0],
]

_DIGIT_2: list[list[int]] = [
    [1, 1, 1, 0],
    [0, 0, 1, 0],
    [1, 1, 1, 0],
    [1, 0, 0, 0],
    [1, 1, 1, 0],
]

PATTERN_W = 9
PATTERN_H = 5


def _build_pattern() -> list[list[int]]:
    pat = [[0] * PATTERN_W for _ in range(PATTERN_H)]
    for r in range(PATTERN_H):
        for c in range(4):
            pat[r][c] = _DIGIT_4[r][c]
            pat[r][5 + c] = _DIGIT_2[r][c]
    return pat


PATTERN_42: list[list[int]] = _build_pattern()


@dataclass(frozen=True)
class Cell:
    """One maze cell. A wall field is True when the wall is closed."""

    north: bool
    east: bool
    south: bool
    west: bool
    is_42: bool = False


class MazeGenerator:
    """DFS backtracker with optional loops and a '42' stencil."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError(
                f"Maze must be at least 2x2, got {width}x{height}."
            )

        self.width = width
        self.height = height
        self.seed = (
            seed if seed is not None else random.randint(0, 2**31 - 1)
        )
        self.perfect = perfect
        self.has_42 = False

        # Start with every wall closed (15 = N|E|S|W).
        self.grid: list[list[int]] = [[15] * width for _ in range(height)]
        self._visited: list[list[bool]] = [
            [False] * width for _ in range(height)
        ]
        self._solid: set[tuple[int, int]] = set()

        self.entry: tuple[int, int] = (0, 0)
        self.exit_: tuple[int, int] = (width - 1, height - 1)

    def generate(
        self,
        entry: tuple[int, int] = (0, 0),
        exit_: tuple[int, int] | None = None,
    ) -> None:
        """Carve walls in place to build the maze."""
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)
        self._validate_endpoints(entry, exit_)

        self.entry = entry
        self.exit_ = exit_

        random.seed(self.seed)
        self._embed_42()

        # Pre-mark stencil cells as visited so the carver skips them.
        for sx, sy in self._solid:
            self._visited[sy][sx] = True

        self._carve(entry[0], entry[1])

        if not self.perfect:
            self._add_loops()

        self._restore_solid_cells()

    def solve(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> list[str] | None:
        """Shortest path as N/E/S/W letters, [] if same, None if none."""
        self._validate_endpoints(entry, exit_, allow_equal=True)
        if entry == exit_:
            return []

        letter = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}
        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        queue: deque[tuple[int, int]] = deque([entry])
        seen = {entry}
        found = False

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == exit_:
                found = True
                break
            for dx, dy, wall, _ in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in seen
                    and not (self.grid[cy][cx] & wall)
                ):
                    seen.add((nx, ny))
                    parent[(nx, ny)] = ((cx, cy), letter[(dx, dy)])
                    queue.append((nx, ny))

        if not found:
            return None

        # Walk parent pointers back from the goal to rebuild the path.
        path: list[str] = []
        cur = exit_
        while cur != entry:
            prev, step = parent[cur]
            path.append(step)
            cur = prev
        path.reverse()
        return path

    def to_hex_string(self) -> str:
        """Render the grid as one row per line of uppercase hex digits."""
        return "\n".join(
            "".join(format(c, "x").upper() for c in row) for row in self.grid
        )

    def to_cells(self) -> list[list[Cell]]:
        """Convert the bitmask grid to a 2D list of Cell objects."""
        out: list[list[Cell]] = []
        for y in range(self.height):
            row: list[Cell] = []
            for x in range(self.width):
                v = self.grid[y][x]
                row.append(
                    Cell(
                        north=bool(v & NORTH),
                        east=bool(v & EAST),
                        south=bool(v & SOUTH),
                        west=bool(v & WEST),
                        is_42=(x, y) in self._solid,
                    )
                )
            out.append(row)
        return out

    def export_to_file(
        self,
        filename: str,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: list[str] | None,
    ) -> None:
        """Write subject-format output (grid, blank, entry, exit, path)."""
        path_str = "".join(path) if path else ""
        content = (
            f"{self.to_hex_string()}\n"
            f"\n"
            f"{entry[0]},{entry[1]}\n"
            f"{exit_[0]},{exit_[1]}\n"
            f"{path_str}\n"
        )
        with open(filename, "w") as fh:
            fh.write(content)

    def _validate_endpoints(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        allow_equal: bool = False,
    ) -> None:
        for label, (x, y) in (("entry", entry), ("exit", exit_)):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(
                    f"{label} {(x, y)} is outside the maze "
                    f"(grid is {self.width}x{self.height})."
                )
        if not allow_equal and entry == exit_:
            raise ValueError(
                f"entry and exit must differ; both are {entry}."
            )

    def _embed_42(self) -> None:
        # Stencil needs a 2-cell margin on every side to look right.
        min_w = PATTERN_W + 4
        min_h = PATTERN_H + 4
        if self.width < min_w or self.height < min_h:
            print(
                f"Error: maze too small to embed the '42' pattern "
                f"(need at least {min_w}x{min_h}).",
                file=sys.stderr,
            )
            return

        ox = (self.width - PATTERN_W) // 2
        oy = (self.height - PATTERN_H) // 2
        for r in range(PATTERN_H):
            for c in range(PATTERN_W):
                if PATTERN_42[r][c]:
                    cx, cy = ox + c, oy + r
                    if (cx, cy) != self.entry and (cx, cy) != self.exit_:
                        self._solid.add((cx, cy))
        self.has_42 = True

    def _carve(self, sx: int, sy: int) -> None:
        # Iterative DFS to avoid Python's recursion limit on large mazes.
        self._visited[sy][sx] = True
        stack: list[tuple[int, int]] = [(sx, sy)]

        while stack:
            cx, cy = stack[-1]
            candidates: list[tuple[int, int, int, int]] = []
            for dx, dy, my_wall, nbr_wall in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not self._visited[ny][nx]
                    and (nx, ny) not in self._solid
                ):
                    candidates.append((nx, ny, my_wall, nbr_wall))

            if candidates:
                nx, ny, my_wall, nbr_wall = random.choice(candidates)
                # Knock both bits down so the two sides agree.
                self.grid[cy][cx] &= ~my_wall
                self.grid[ny][nx] &= ~nbr_wall
                self._visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _add_loops(self) -> None:
        # Open ~1/8 of the internal walls without creating any 3x3 open block.
        target = max(1, (self.width * self.height) // 8)
        added = 0
        attempts = 0
        while added < target and attempts < target * 20:
            attempts += 1
            if random.random() < 0.5:
                if self._try_open_east():
                    added += 1
            elif self._try_open_south():
                added += 1

    def _try_open_east(self) -> bool:
        if self.width < 2:
            return False
        x = random.randint(0, self.width - 2)
        y = random.randint(0, self.height - 1)
        if (x, y) in self._solid or (x + 1, y) in self._solid:
            return False
        if not (self.grid[y][x] & EAST):
            return False
        if self._makes_3x3(x, y, "E"):
            return False
        self.grid[y][x] &= ~EAST
        self.grid[y][x + 1] &= ~WEST
        return True

    def _try_open_south(self) -> bool:
        if self.height < 2:
            return False
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 2)
        if (x, y) in self._solid or (x, y + 1) in self._solid:
            return False
        if not (self.grid[y][x] & SOUTH):
            return False
        if self._makes_3x3(x, y, "S"):
            return False
        self.grid[y][x] &= ~SOUTH
        self.grid[y + 1][x] &= ~NORTH
        return True

    def _makes_3x3(self, x: int, y: int, direction: str) -> bool:
        # Open the wall tentatively, scan the 3x3 windows that touch it,
        # then put the wall back.
        if direction == "E":
            self.grid[y][x] &= ~EAST
            self.grid[y][x + 1] &= ~WEST
            bx_min = max(0, x - 2)
            bx_max = min(self.width - 3, x + 1)
            by_min = max(0, y - 2)
            by_max = min(self.height - 3, y)
        else:
            self.grid[y][x] &= ~SOUTH
            self.grid[y + 1][x] &= ~NORTH
            bx_min = max(0, x - 2)
            bx_max = min(self.width - 3, x)
            by_min = max(0, y - 2)
            by_max = min(self.height - 3, y + 1)

        found = False
        for bx in range(bx_min, bx_max + 1):
            for by in range(by_min, by_max + 1):
                if self._all_open_3x3(bx, by):
                    found = True
                    break
            if found:
                break

        if direction == "E":
            self.grid[y][x] |= EAST
            self.grid[y][x + 1] |= WEST
        else:
            self.grid[y][x] |= SOUTH
            self.grid[y + 1][x] |= NORTH
        return found

    def _all_open_3x3(self, x: int, y: int) -> bool:
        for cy in range(y, y + 3):
            for cx in range(x, x + 3):
                v = self.grid[cy][cx]
                if cx < x + 2 and (v & EAST):
                    return False
                if cy < y + 2 and (v & SOUTH):
                    return False
        return True

    def _restore_solid_cells(self) -> None:
        # Defensive: re-close every wall around a stencil cell after carving.
        for sx, sy in self._solid:
            self.grid[sy][sx] = 15
            for dx, dy, _, nbr_wall in DIRECTIONS:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= nbr_wall


__all__ = [
    "Cell",
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
