from ascii_renderer import render_maze
from maze_types import Cell, Maze


def test_render_contains_structure() -> None:
    maze = Maze(
        width=1,
        height=1,
        grid=[[Cell(True, True, True, True)]],
        entry=(0, 0),
        exit=(0, 0),
    )
    rendered = render_maze(maze)
    assert "+---+" in rendered
