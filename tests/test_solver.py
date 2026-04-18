from maze_types import Cell, Maze
from solver import find_shortest_path, validate_path


def test_find_shortest_path_simple() -> None:
    grid = [
        [Cell(True, False, True, True), Cell(True, True, False, False)],
        [Cell(True, True, True, True), Cell(False, True, True, True)],
    ]
    maze = Maze(width=2, height=2, grid=grid, entry=(0, 0), exit=(1, 0))
    path = find_shortest_path(maze)
    assert path == "E"
    assert validate_path(maze, path)
