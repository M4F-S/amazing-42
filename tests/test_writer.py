from maze_types import Cell
from writer import cell_to_hex


def test_cell_to_hex():
    cell = Cell(north=True, east=True, south=False, west=False)
    assert cell_to_hex(cell) == "3"
