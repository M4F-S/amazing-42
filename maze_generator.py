import random
from collections import deque
from typing import Optional

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
    pat = [[0] * PATTERN_W for _ in range(PATTERN_H)]
    for r in range(PATTERN_H):
        for c in range(4):
            pat[r][c] = _DIGIT_4[r][c]
            pat[r][5 + c] = _DIGIT_2[r][c]
    return pat


PATTERN_42: list[list[int]] = _build_pattern()


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError(f"Maze must be at least 2×2, got {width}×{height}.")

        self.width: int = width
        self.height: int = height
        self.seed: int = seed if seed is not None else random.randint(0, 2**31 - 1)
        self.perfect: bool = perfect
        self.has_42: bool = False

        self.grid: list[list[int]] = [[15] * width for _ in range(height)]
        self._visited: list[list[bool]] = [[False] * width for _ in range(height)]
        self._solid: set[tuple[int, int]] = set()

        self.entry: tuple[int, int] = (0, 0)
        self.exit_: tuple[int, int] = (width - 1, height - 1)

    def generate(
        self,
        entry: tuple[int, int] = (0, 0),
        exit_: tuple[int, int] | None = None,
    ) -> None:
        self.entry = entry
        self.exit_ = exit_ if exit_ is not None else (self.width - 1, self.height - 1)

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
        if entry == exit_:
            return []

        letter: dict[tuple[int, int], str] = {
            (0, -1): "N",
            (1, 0): "E",
            (0, 1): "S",
            (-1, 0): "W",
        }

        queue: deque[tuple[tuple[int, int], list[str]]] = deque([(entry, [])])
        seen: set[tuple[int, int]] = {entry}

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == exit_:
                return path

            for dx, dy, wall, _ in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in seen
                    and not (self.grid[cy][cx] & wall)
                ):
                    seen.add((nx, ny))
                    queue.append(((nx, ny), path + [letter[(dx, dy)]]))

        return None

    def to_hex_string(self) -> str:
        lines = []
        for row in self.grid:
            lines.append("".join(hex(cell)[2:].upper() for cell in row))
        return "\n".join(lines)

    def export_to_file(
        self,
        filename: str,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: list[str] | None,
    ) -> None:
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

    def _embed_42(self) -> None:
        min_w = PATTERN_W + 4
        min_h = PATTERN_H + 4
        if self.width < min_w or self.height < min_h:
            print(
                "Info: maze too small to embed the '42' pattern "
                f"(need at least {min_w}×{min_h})."
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
        target = max(1, (self.width * self.height) // 8)
        added = 0
        attempts = 0

        while added < target and attempts < target * 20:
            attempts += 1
            x = random.randint(0, self.width - 2)
            y = random.randint(0, self.height - 1)

            if (x, y) in self._solid or (x + 1, y) in self._solid:
                continue
            if (self.grid[y][x] & EAST) and not self._makes_3x3(x, y):
                self.grid[y][x] &= ~EAST
                self.grid[y][x + 1] &= ~WEST
                added += 1

    def _makes_3x3(self, x: int, y: int) -> bool:
        self.grid[y][x] &= ~EAST
        self.grid[y][x + 1] &= ~WEST

        found = False
        for bx in range(max(0, x - 2), min(self.width - 3, x) + 1):
            for by in range(max(0, y - 2), min(self.height - 3, y) + 1):
                if self._all_open_3x3(bx, by):
                    found = True
                    break
            if found:
                break

        self.grid[y][x] |= EAST
        self.grid[y][x + 1] |= WEST
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
        for (sx, sy) in self._solid:
            self.grid[sy][sx] = 15
            for dx, dy, _, nbr_wall in DIRECTIONS:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= nbr_wall
