from __future__ import annotations

from colors import ColorScheme, RESET
from maze_types import Maze


def path_positions(maze: Maze, path: str) -> set[tuple[int, int]]:
    """Return all cells visited by the path, including entry and exit."""
    positions: set[tuple[int, int]] = {maze.entry}
    x, y = maze.entry

    for step in path:
        if step == "N":
            y -= 1
        elif step == "E":
            x += 1
        elif step == "S":
            y += 1
        elif step == "W":
            x -= 1
        positions.add((x, y))

    return positions


def render_maze(
    maze: Maze,
    show_path: bool = False,
    shortest_path: str | None = None,
    colors: ColorScheme | None = None,
) -> str:
    """Render the maze using simple portable ASCII characters."""
    palette = colors or ColorScheme()
    path_cells: set[tuple[int, int]] = set()

    if show_path and shortest_path is not None:
        path_cells = path_positions(maze, shortest_path)

    lines: list[str] = []

    top_line = "+"
    for x in range(maze.width):
        cell = maze.grid[0][x]
        top_line += ("---" if cell.north else "   ") + "+"
    lines.append(palette.wall + top_line + RESET)

    for y in range(maze.height):
        middle = ""
        bottom = "+"

        for x in range(maze.width):
            cell = maze.grid[y][x]

            middle += palette.wall + ("|" if cell.west else " ") + RESET

            char = " "
            if (x, y) == maze.entry:
                char = palette.entry + "E" + RESET
            elif (x, y) == maze.exit:
                char = palette.exit + "X" + RESET
            elif cell.is_42:
                char = palette.closed_42 + "#" + RESET
            elif (x, y) in path_cells:
                char = palette.path + "." + RESET

            middle += f" {char} "
            bottom += (palette.wall + "---" + RESET if cell.south else "   ") + palette.wall + "+" + RESET

        right_wall = maze.grid[y][maze.width - 1].east
        middle += palette.wall + ("|" if right_wall else " ") + RESET

        lines.append(middle)
        lines.append(bottom)

    return "\n".join(lines)
