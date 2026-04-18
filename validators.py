from __future__ import annotations

from maze_types import Maze


def validate_coordinates(maze: Maze) -> None:
    """Ensure entry and exit are inside the maze."""
    for name, (x, y) in (("entry", maze.entry), ("exit", maze.exit)):
        if not (0 <= x < maze.width and 0 <= y < maze.height):
            raise ValueError(f"{name} is out of bounds: {(x, y)}")


def validate_grid_shape(maze: Maze) -> None:
    """Ensure grid dimensions match maze width and height."""
    if len(maze.grid) != maze.height:
        raise ValueError("Grid height does not match maze.height")
    for row in maze.grid:
        if len(row) != maze.width:
            raise ValueError("Grid width does not match maze.width")


def validate_neighbor_consistency(maze: Maze) -> None:
    """Ensure shared walls match between neighbouring cells."""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]
            if x + 1 < maze.width and cell.east != maze.grid[y][x + 1].west:
                raise ValueError(f"Inconsistent east/west walls at {(x, y)}")
            if y + 1 < maze.height and cell.south != maze.grid[y + 1][x].north:
                raise ValueError(f"Inconsistent south/north walls at {(x, y)}")


def validate_maze(maze: Maze) -> None:
    """Run all basic maze checks needed by Student B modules."""
    validate_grid_shape(maze)
    validate_coordinates(maze)
    validate_neighbor_consistency(maze)
