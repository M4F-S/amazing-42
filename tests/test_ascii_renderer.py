from maze_types import Cell, Maze
from ascii_renderer import render_maze


def test_render_contains_entry_and_exit():
    grid = [[Cell(True, True, True, True)]]
    maze = Maze(width=1, height=1, grid=grid, entry=(0, 0), exit=(0, 0))
    output = render_maze(maze)
    assert "+" in output
