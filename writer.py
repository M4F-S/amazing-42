from __future__ import annotations

from pathlib import Path

from maze_types import Cell, Maze


def cell_to_int(cell: Cell) -> int:
    """Encode one cell as a 4-bit integer.

    Bit order required by the subject:
    - bit 0: North
    - bit 1: East
    - bit 2: South
    - bit 3: West
    """
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
    """Convert one cell to a single uppercase hexadecimal digit."""
    return format(cell_to_int(cell), "X")


def maze_rows_to_hex(maze: Maze) -> list[str]:
    """Convert the full maze grid to output rows."""
    return ["".join(cell_to_hex(cell) for cell in row) for row in maze.grid]


def format_coordinate(coord: tuple[int, int]) -> str:
    """Format a coordinate as x,y."""
    x, y = coord
    return f"{x},{y}"


def build_output_text(maze: Maze, shortest_path: str) -> str:
    """Build the complete maze output file content."""
    lines = maze_rows_to_hex(maze)
    lines.append("")
    lines.append(format_coordinate(maze.entry))
    lines.append(format_coordinate(maze.exit))
    lines.append(shortest_path)
    return "\n".join(lines) + "\n"


def write_output_file(maze: Maze, shortest_path: str, output_file: str) -> None:
    """Write the maze output file."""
    Path(output_file).write_text(build_output_text(maze, shortest_path), encoding="utf-8")
