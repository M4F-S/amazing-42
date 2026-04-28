"""Maze generator: randomised recursive backtracker with a '42' stencil."""

import random
import sys
from collections import deque

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

# (dx, dy, my_wall_bit, neighbour_wall_bit)
DIRS = [
    (0, -1, NORTH, SOUTH),
    (1, 0, EAST, WEST),
    (0, 1, SOUTH, NORTH),
    (-1, 0, WEST, EAST),
]
LETTER = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

_FOUR = [
    [1, 0, 1, 0],
    [1, 0, 1, 0],
    [1, 1, 1, 1],
    [0, 0, 1, 0],
    [0, 0, 1, 0],
]
_TWO = [
    [1, 1, 1, 0],
    [0, 0, 1, 0],
    [1, 1, 1, 0],
    [1, 0, 0, 0],
    [1, 1, 1, 0],
]
PATTERN_W, PATTERN_H = 9, 5
PATTERN = [
    [_FOUR[r][c] if c < 4 else _TWO[r][c - 5] if c > 4 else 0
     for c in range(PATTERN_W)]
    for r in range(PATTERN_H)
]


class MazeGenerator:
    """Build a maze with DFS, embed a '42' stencil, BFS for shortest path."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError(f"maze too small: {width}x{height}")
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 2**31 - 1)
        self.perfect = perfect
        self.has_42 = False
        self.entry: tuple[int, int] = (0, 0)
        self.exit_: tuple[int, int] = (width - 1, height - 1)
        self.grid: list[list[int]] = [
            [15] * width for _ in range(height)
        ]
        self._solid: set[tuple[int, int]] = set()

    def generate(
        self,
        entry: tuple[int, int] = (0, 0),
        exit_: tuple[int, int] | None = None,
    ) -> None:
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)
        self._check_endpoints(entry, exit_)
        self.entry, self.exit_ = entry, exit_

        # reset (so generate() can be called repeatedly)
        self.grid = [[15] * self.width for _ in range(self.height)]
        self._solid.clear()
        self.has_42 = False

        random.seed(self.seed)
        self._embed_42()

        visited = [[False] * self.width for _ in range(self.height)]
        for x, y in self._solid:
            visited[y][x] = True
        self._carve(entry[0], entry[1], visited)

        if not self.perfect:
            self._add_loops()
        self._seal_42()

    def solve(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> list[str] | None:
        self._check_endpoints(entry, exit_, allow_equal=True)
        if entry == exit_:
            return []

        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        seen = {entry}
        q: deque[tuple[int, int]] = deque([entry])
        while q:
            x, y = q.popleft()
            if (x, y) == exit_:
                break
            for dx, dy, wall, _ in DIRS:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if (nx, ny) in seen or self.grid[y][x] & wall:
                    continue
                seen.add((nx, ny))
                parent[(nx, ny)] = ((x, y), LETTER[(dx, dy)])
                q.append((nx, ny))
        else:
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
        return "\n".join(
            "".join(format(c, "x").upper() for c in row) for row in self.grid
        )

    def export_to_file(
        self,
        filename: str,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: list[str] | None,
    ) -> None:
        body = "".join(path) if path else ""
        with open(filename, "w") as f:
            f.write(self.to_hex_string())
            f.write(f"\n\n{entry[0]},{entry[1]}\n")
            f.write(f"{exit_[0]},{exit_[1]}\n{body}\n")

    # ----- helpers -----

    def _check_endpoints(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        allow_equal: bool = False,
    ) -> None:
        for label, (x, y) in (("entry", entry), ("exit", exit_)):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(
                    f"{label} {(x, y)} outside "
                    f"{self.width}x{self.height} grid"
                )
        if not allow_equal and entry == exit_:
            raise ValueError(f"entry and exit must differ ({entry})")

    def _embed_42(self) -> None:
        min_w, min_h = PATTERN_W + 4, PATTERN_H + 4
        if self.width < min_w or self.height < min_h:
            print(
                f"Error: maze too small to embed '42' "
                f"(need at least {min_w}x{min_h}).",
                file=sys.stderr,
            )
            return
        ox = (self.width - PATTERN_W) // 2
        oy = (self.height - PATTERN_H) // 2
        for r in range(PATTERN_H):
            for c in range(PATTERN_W):
                if not PATTERN[r][c]:
                    continue
                p = (ox + c, oy + r)
                if p != self.entry and p != self.exit_:
                    self._solid.add(p)
        self.has_42 = True

    def _carve(
        self, sx: int, sy: int, visited: list[list[bool]]
    ) -> None:
        visited[sy][sx] = True
        stack = [(sx, sy)]
        while stack:
            x, y = stack[-1]
            cands = []
            for dx, dy, mine, theirs in DIRS:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if visited[ny][nx] or (nx, ny) in self._solid:
                    continue
                cands.append((nx, ny, mine, theirs))
            if not cands:
                stack.pop()
                continue
            nx, ny, mine, theirs = random.choice(cands)
            self.grid[y][x] &= ~mine
            self.grid[ny][nx] &= ~theirs
            visited[ny][nx] = True
            stack.append((nx, ny))

    def _add_loops(self) -> None:
        target = max(1, self.width * self.height // 8)
        added = tries = 0
        while added < target and tries < target * 20:
            tries += 1
            if random.random() < 0.5:
                if self._open_east():
                    added += 1
            else:
                if self._open_south():
                    added += 1

    def _open_east(self) -> bool:
        if self.width < 2:
            return False
        x = random.randint(0, self.width - 2)
        y = random.randint(0, self.height - 1)
        if (x, y) in self._solid or (x + 1, y) in self._solid:
            return False
        if not self.grid[y][x] & EAST:
            return False
        if self._would_open_3x3(x, y, "E"):
            return False
        self.grid[y][x] &= ~EAST
        self.grid[y][x + 1] &= ~WEST
        return True

    def _open_south(self) -> bool:
        if self.height < 2:
            return False
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 2)
        if (x, y) in self._solid or (x, y + 1) in self._solid:
            return False
        if not self.grid[y][x] & SOUTH:
            return False
        if self._would_open_3x3(x, y, "S"):
            return False
        self.grid[y][x] &= ~SOUTH
        self.grid[y + 1][x] &= ~NORTH
        return True

    def _would_open_3x3(self, x: int, y: int, direction: str) -> bool:
        if direction == "E":
            self.grid[y][x] &= ~EAST
            self.grid[y][x + 1] &= ~WEST
            xs = range(max(0, x - 2), min(self.width - 3, x + 1) + 1)
            ys = range(max(0, y - 2), min(self.height - 3, y) + 1)
        else:
            self.grid[y][x] &= ~SOUTH
            self.grid[y + 1][x] &= ~NORTH
            xs = range(max(0, x - 2), min(self.width - 3, x) + 1)
            ys = range(max(0, y - 2), min(self.height - 3, y + 1) + 1)
        bad = any(self._all_open(bx, by) for by in ys for bx in xs)
        if direction == "E":
            self.grid[y][x] |= EAST
            self.grid[y][x + 1] |= WEST
        else:
            self.grid[y][x] |= SOUTH
            self.grid[y + 1][x] |= NORTH
        return bad

    def _all_open(self, x: int, y: int) -> bool:
        for cy in range(y, y + 3):
            for cx in range(x, x + 3):
                v = self.grid[cy][cx]
                if cx < x + 2 and v & EAST:
                    return False
                if cy < y + 2 and v & SOUTH:
                    return False
        return True

    def _seal_42(self) -> None:
        for x, y in self._solid:
            self.grid[y][x] = 15
            for dx, dy, _, theirs in DIRS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= theirs
