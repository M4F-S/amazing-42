# mazegen

Randomised recursive backtracker maze generator with an embedded
"42" stencil and a BFS shortest-path solver. Built for the 42
*A-Maze-ing* project.

## Install

```bash
pip install mazegen-1.0.1-py3-none-any.whl
```

## Usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 14))
path = gen.solve(entry=(0, 0), exit_=(19, 14))

# Subject hex format, one row per line:
print(gen.to_hex_string())

# Or the full output file (hex grid + entry + exit + path):
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 14), path=path)

# Direct grid access (4-bit ints; bits NORTH=1, EAST=2, SOUTH=4, WEST=8):
cell = gen.grid[0][0]
print(bool(cell & 2))   # east wall closed?
```

## Constructor parameters

| Name      | Type             | Default | Meaning                                  |
|-----------|------------------|---------|------------------------------------------|
| `width`   | `int`            | -       | cells, >= 2                              |
| `height`  | `int`            | -       | cells, >= 2                              |
| `seed`    | `int` or `None`  | random  | reproducible PRNG seed                   |
| `perfect` | `bool`           | `True`  | one path between any two non-`42` cells  |

## Public API

| Method                                     | Returns                |
|--------------------------------------------|------------------------|
| `generate(entry, exit_)`                   | `None` (mutates grid)  |
| `solve(entry, exit_)`                      | `list[str]` of N/E/S/W |
| `to_hex_string()`                          | `str`                  |
| `export_to_file(filename, entry, exit_, path)` | `None`             |

## Wall encoding

| bit | wall  |
|-----|-------|
| 0   | NORTH |
| 1   | EAST  |
| 2   | SOUTH |
| 3   | WEST  |

A bit set to `1` means the wall is closed.
