"""Maze generator for the amazing-42 project.

This module implements a randomised recursive backtracker (DFS) maze
generator with optional loop creation, an embedded ``42`` stencil in the
centre of large enough mazes, and BFS shortest-path solving.

Wall encoding (per cell, 4-bit integer):

    NORTH = 1, EAST = 2, SOUTH = 4, WEST = 8

A cell whose value is 15 (``0xF``) has all four walls; 0 has none.
The grid stores one such integer per cell, so two adjacent cells always
agree on the wall between them: ``_carve`` knocks both bits down at once.
"""

from __future__ import annotations

import random
import sys
from collections import deque

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8

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

PATTERN_W: int = 9
PATTERN_H: int = 5


def _build_pattern() -> list[list[int]]:
    """Compose the 5x9 stencil of the digits ``42`` from the two glyphs."""
    pat = [[0] * PATTERN_W for _ in range(PATTERN_H)]
    for r in range(PATTERN_H):
        for c in range(4):
            pat[r][c] = _DIGIT_4[r][c]
            pat[r][5 + c] = _DIGIT_2[r][c]
    return pat


PATTERN_42: list[list[int]] = _build_pattern()


class MazeGenerator:
    """Randomised recursive backtracker with optional loops and a ``42`` stencil.

    Example:
        >>> gen = MazeGenerator(width=20, height=20, seed=42, perfect=True)
        >>> gen.generate(entry=(0, 0), exit_=(19, 19))
        >>> path = gen.solve(entry=(0, 0), exit_=(19, 19))
        >>> gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 19), path=path)
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        """Initialise the grid and parameters.

        Args:
            width: Maze width in cells (must be >= 2).
            height: Maze height in cells (must be >= 2).
            seed: PRNG seed for reproducibility. Random if ``None``.
            perfect: When ``True``, generate a perfect maze (single path
                between any two cells). When ``False``, post-process to
                add loops while preserving the no-3x3-open-area rule.

        Raises:
            ValueError: If ``width`` or ``height`` is less than 2.
        """
        if width < 2 or height < 2:
            raise ValueError(
                f"Maze must be at least 2x2, got {width}x{height}."
            )

        self.width: int = width
        self.height: int = height
        self.seed: int = (
            seed if seed is not None else random.randint(0, 2**31 - 1)
        )
        self.perfect: bool = perfect
        self.has_42: bool = False

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
        """Carve walls to build the maze.

        Args:
            entry: Start cell coordinates.
            exit_: End cell coordinates. Defaults to the bottom-right cell.

        Raises:
            ValueError: If ``entry`` or ``exit_`` falls outside the grid,
                or if they are equal.
        """
        resolved_exit = (
            exit_ if exit_ is not None else (self.width - 1, self.height - 1)
        )
        self._validate_endpoints(entry, resolved_exit)

        self.entry = entry
        self.exit_ = resolved_exit

        random.seed(self.seed)

        self._embed_42()

        for (sx, sy) in self._solid:
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
        """Find the shortest path from ``entry`` to ``exit_`` using BFS.

        Args:
            entry: Start cell coordinates.
            exit_: Goal cell coordinates.

        Returns:
            A list of single-letter direction strings (``"N"``, ``"E"``,
            ``"S"``, ``"W"``) tracing the shortest path, an empty list
            when ``entry == exit_``, or ``None`` if no path exists.

        Raises:
            ValueError: If ``entry`` or ``exit_`` falls outside the grid.
        """
        self._validate_endpoints(entry, exit_, allow_equal=True)

        if entry == exit_:
            return []

        letter: dict[tuple[int, int], str] = {
            (0, -1): "N",
            (1, 0): "E",
            (0, 1): "S",
            (-1, 0): "W",
        }

        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        queue: deque[tuple[int, int]] = deque([entry])
        seen: set[tuple[int, int]] = {entry}
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
        lines = []
        for row in self.grid:
            lines.append("".join(format(cell, "x").upper() for cell in row))
        return "\n".join(lines)

    def export_to_file(
        self,
        filename: str,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: list[str] | None,
    ) -> None:
        """Write the maze, entry/exit, and solution path to ``filename``.

        File layout (one trailing newline):

            <hex-grid>
            <blank line>
            <entry_x>,<entry_y>
            <exit_x>,<exit_y>
            <path-string>
        """
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
        """Validate endpoint coordinates against grid bounds and inequality."""
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
        """Mark the cells of the centred ``42`` stencil as forbidden for carving.

        The stencil is skipped (with an ``Error:`` notice on stderr) when
        the maze is too small to fit it with a 2-cell margin on every side.
        Entry and exit cells are never overwritten by the stencil.
        """
        min_w = PATTERN_W + 4
        min_h = PATTERN_H + 4
        if self.width < min_w or self.height < min_h:
            print(
                "Error: maze too small to embed the '42' pattern "
                f"(need at least {min_w}x{min_h}).",
                file=sys.stderr,
            )
            return

        ox = (self.width - PATTERN_W) // 2
        oy = (self.height - PATTERN_H) // 2

        for r in range(PATTERN_H):
            for c in range(PATTERN_W):
                if PATTERN_42[r][c] == 1:
                    cx, cy = ox + c, oy + r
                    if (cx, cy) != self.entry and (cx, cy) != self.exit_:
                        self._solid.add((cx, cy))

        self.has_42 = True

    def _carve(self, sx: int, sy: int) -> None:
        """Iterative randomised DFS that knocks down walls coherently.

        Skips any cell in ``self._solid`` so the ``42`` stencil stays intact.
        Each carve clears one bit on each of the two adjacent cells, so the
        wall representation is always consistent.
        """
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
                self.grid[cy][cx] &= ~my_wall
                self.grid[ny][nx] &= ~nbr_wall
                self._visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _add_loops(self) -> None:
        """Knock down a fraction of internal walls to break the perfect-maze property.

        Picks east or south at random with equal probability, refuses to
        open a wall that would create a 3x3 fully open area, and never
        opens a wall adjacent to a forbidden (``42``) cell.
        """
        target = max(1, (self.width * self.height) // 8)
        added = 0
        attempts = 0

        while added < target and attempts < target * 20:
            attempts += 1
            if random.random() < 0.5:
                if self._try_open_east():
                    added += 1
            else:
                if self._try_open_south():
                    added += 1

    def _try_open_east(self) -> bool:
        """Attempt to open one east-facing internal wall. Return ``True`` on success."""
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
        """Attempt to open one south-facing internal wall. Return ``True`` on success."""
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
        """Return ``True`` if opening the given wall would create a 3x3 open block.

        The wall is opened tentatively, every 3x3 window touching either
        side of it is checked, and then the wall is restored before
        returning. ``direction`` is ``"E"`` for east or ``"S"`` for south.
        """
        if direction == "E":
            self.grid[y][x] &= ~EAST
            self.grid[y][x + 1] &= ~WEST
            bx_min = max(0, x - 2)
            bx_max = min(self.width - 3, x + 1)
            by_min = max(0, y - 2)
            by_max = min(self.height - 3, y)
        else:  # "S"
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
        """Return ``True`` if the 3x3 block at top-left ``(x, y)`` has no internal walls."""
        for cy in range(y, y + 3):
            for cx in range(x, x + 3):
                v = self.grid[cy][cx]
                if cx < x + 2 and (v & EAST):
                    return False
                if cy < y + 2 and (v & SOUTH):
                    return False
        return True

    def _restore_solid_cells(self) -> None:
        """Defensively close every wall around a forbidden (``42``) cell.

        ``_carve`` and ``_add_loops`` already avoid opening walls into
        forbidden cells, so this is a safety net that guarantees the
        rendered ``42`` is coherent regardless of upstream changes.
        """
        for (sx, sy) in self._solid:
            self.grid[sy][sx] = 15
            for dx, dy, _, nbr_wall in DIRECTIONS:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= nbr_wall


__all__ = [
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "DIRECTIONS",
    "PATTERN_W",
    "PATTERN_H",
    "PATTERN_42",
    "MazeGenerator",
]
