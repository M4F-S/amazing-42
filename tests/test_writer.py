from maze_types import Cell, Maze
from writer import build_output_text, cell_to_hex


def test_cell_to_hex() -> None:
    cell = Cell(north=True, east=True, south=False, west=False)
    assert cell_to_hex(cell) == "3"


def test_build_output_text() -> None:
    maze = Maze(
        width=1,
        height=1,
        grid=[[Cell(True, True, True, True)]],
        entry=(0, 0),
        exit=(0, 0),
    )
    text = build_output_text(maze, "")
    assert text == "F\n\n0,0\n0,0\n\n"
