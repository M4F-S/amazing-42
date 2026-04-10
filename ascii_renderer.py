from maze_types import Maze
from colors import ColorScheme, RESET


def path_positions(maze: Maze, path: str) -> set[tuple[int, int]]:
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
    colors = colors or ColorScheme()
    path_cells = set()

    if show_path and shortest_path is not None:
        path_cells = path_positions(maze, shortest_path)

    lines: list[str] = []

    top_line = "+"
    for x in range(maze.width):
        cell = maze.grid[0][x]
        top_line += ("---" if cell.north else "   ") + "+"
    lines.append(colors.wall + top_line + RESET)

    for y in range(maze.height):
        middle = ""
        bottom = "+"

        for x in range(maze.width):
            cell = maze.grid[y][x]

            if cell.west:
                middle += colors.wall + "|" + RESET
            else:
                middle += " "

            char = " "
            if (x, y) == maze.entry:
                char = colors.entry + "E" + RESET
            elif (x, y) == maze.exit:
                char = colors.exit + "X" + RESET
            elif cell.is_42:
                char = colors.closed_42 + "#" + RESET
            elif (x, y) in path_cells:
                char = colors.path + "." + RESET

            middle += f" {char} "

            bottom += (colors.wall + "---" + RESET if cell.south else "   ") + (colors.wall + "+" + RESET)

        east_wall = maze.grid[y][maze.width - 1].east
        middle += colors.wall + ("|" if east_wall else " ") + RESET

        lines.append(middle)
        lines.append(bottom)

    return "\n".join(lines)
