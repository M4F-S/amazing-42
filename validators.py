from maze_types import Maze


def validate_coordinates(maze: Maze) -> None:
    for name, (x, y) in [("entry", maze.entry), ("exit", maze.exit)]:
        if not (0 <= x < maze.width and 0 <= y < maze.height):
            raise ValueError(f"{name} is out of bounds")


def validate_neighbor_consistency(maze: Maze) -> None:
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]

            if x + 1 < maze.width:
                right = maze.grid[y][x + 1]
                if cell.east != right.west:
                    raise ValueError(f"Inconsistent east/west wall at {(x, y)}")

            if y + 1 < maze.height:
                below = maze.grid[y + 1][x]
                if cell.south != below.north:
                    raise ValueError(f"Inconsistent south/north wall at {(x, y)}")
