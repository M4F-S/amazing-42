from pathlib import Path

from maze_types import Cell, Maze


def cell_to_int(cell: Cell) -> int:
    value = 0
    if cell.north:
        value |= 1
    if cell.east:
        value |= 2
    if cell.south:
        value |= 4
    if cell.west:
        value |= 8
    return value


def cell_to_hex(cell: Cell) -> str:
    return format(cell_to_int(cell), "X")


def maze_rows_to_hex(maze: Maze) -> list[str]:
    rows: list[str] = []
    for row in maze.grid:
        rows.append("".join(cell_to_hex(cell) for cell in row))
    return rows


def format_coordinate(coord: tuple[int, int]) -> str:
    x, y = coord
    return f"{x},{y}"


def build_output_text(maze: Maze, shortest_path: str) -> str:
    lines = maze_rows_to_hex(maze)
    lines.append("")
    lines.append(format_coordinate(maze.entry))
    lines.append(format_coordinate(maze.exit))
    lines.append(shortest_path)
    return "\n".join(lines) + "\n"


def write_output_file(maze: Maze, shortest_path: str, output_file: str) -> None:
    content = build_output_text(maze, shortest_path)
    Path(output_file).write_text(content, encoding="utf-8")
