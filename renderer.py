"""ASCII renderer + interactive menu for the maze."""

from __future__ import annotations

from typing import Callable

from mazegen import EAST, NORTH, SOUTH, WEST, MazeGenerator

WALL_COLOURS = [
    ("default", "\033[0m"),
    ("cyan", "\033[36m"),
    ("green", "\033[32m"),
    ("yellow", "\033[33m"),
    ("magenta", "\033[35m"),
    ("red", "\033[31m"),
]
RESET = "\033[0m"
ENTRY_TAG = "\033[32mE\033[0m"  # green
EXIT_TAG = "\033[31mX\033[0m"   # red
PATH_TAG = "\033[34m·\033[0m"  # blue middle-dot
SOLID_TAG = "\033[37;1m#\033[0m"  # bright white


def render(
    gen: MazeGenerator,
    path: list[str] | None,
    show_path: bool,
    colour_idx: int,
) -> str:
    """Return a printable ASCII representation of the maze."""
    grid = gen.grid
    w, h = gen.width, gen.height
    _, esc = WALL_COLOURS[colour_idx % len(WALL_COLOURS)]

    path_cells = _path_cells(gen, path) if (show_path and path) else set()

    # Build a 2*h+1 by 2*w+1 character grid.
    out: list[list[str]] = [
        [" "] * (2 * w + 1) for _ in range(2 * h + 1)
    ]

    # Outer corners + interior corners
    for y in range(h + 1):
        for x in range(w + 1):
            out[2 * y][2 * x] = "+"

    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            if cell & NORTH:
                out[2 * y][2 * x + 1] = "-"
            if cell & SOUTH:
                out[2 * y + 2][2 * x + 1] = "-"
            if cell & WEST:
                out[2 * y + 1][2 * x] = "|"
            if cell & EAST:
                out[2 * y + 1][2 * x + 2] = "|"

            inner = " "
            if (x, y) == gen.entry:
                inner = ENTRY_TAG
            elif (x, y) == gen.exit_:
                inner = EXIT_TAG
            elif cell == 15 and (x, y) in gen._solid:
                inner = SOLID_TAG
            elif (x, y) in path_cells:
                inner = PATH_TAG
            out[2 * y + 1][2 * x + 1] = inner

    lines = []
    for row in out:
        line = "".join(row)
        # colour only the wall characters (- | +)
        coloured = ""
        for ch in line:
            if ch in "-|+":
                coloured += f"{esc}{ch}{RESET}"
            else:
                coloured += ch
        lines.append(coloured)
    return "\n".join(lines)


def _path_cells(
    gen: MazeGenerator, path: list[str]
) -> set[tuple[int, int]]:
    cells = {gen.entry}
    x, y = gen.entry
    moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for step in path:
        dx, dy = moves[step]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


MENU = (
    "\n"
    "[1] Regenerate   "
    "[2] Toggle path   "
    "[3] Change colour   "
    "[4] Quit\n"
    "> "
)


def run(
    gen: MazeGenerator,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    on_regenerate: Callable[[], MazeGenerator],
) -> None:
    """Display the maze and handle the interactive menu loop."""
    show_path = True
    colour_idx = 0
    path = gen.solve(entry, exit_)

    while True:
        print(render(gen, path, show_path, colour_idx))
        try:
            choice = input(MENU).strip().lower()
        except EOFError:
            print()
            return
        if choice in ("4", "q", "quit"):
            return
        if choice in ("1", "r"):
            gen = on_regenerate()
            path = gen.solve(entry, exit_)
            continue
        if choice in ("2", "p"):
            show_path = not show_path
            continue
        if choice in ("3", "c"):
            colour_idx = (colour_idx + 1) % len(WALL_COLOURS)
            continue
        print("unknown choice")
