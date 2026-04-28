# mazegen

Reusable maze generator: randomised DFS backtracker, BFS solver, optional
loops, and an embedded "42" stencil. Built for the 42 *amazing* project.
Pure stdlib, no third-party dependencies.

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

print(gen.to_hex_string())
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 14), path=path)
```

## Constructor parameters

| name | type | default | meaning |
|---|---|---|---|
| `width` | `int` | required | width in cells, >= 2 |
| `height` | `int` | required | height in cells, >= 2 |
| `seed` | `int \| None` | random | reproducible PRNG seed |
| `perfect` | `bool` | `True` | exactly one path between any two cells |

## Accessing the structure

After `generate()`, the maze is exposed as `gen.grid` — a `list[list[int]]`
of 4-bit wall masks (`NORTH=1`, `EAST=2`, `SOUTH=4`, `WEST=8`; bit set =
wall closed). For named-attribute access:

```python
cells = gen.to_cells()       # list[list[Cell]]
cells[0][0].north            # True if the wall is closed
cells[0][0].is_42            # True if the cell belongs to the '42' stencil
```

Other public attributes: `gen.entry`, `gen.exit_`, `gen.seed`, `gen.has_42`.

## Solving

```python
path = gen.solve(entry=(0, 0), exit_=(19, 14))
# ['E', 'S', 'E', ...] — shortest path letters
# []                   — entry == exit_
# None                 — no path exists
```

## Output file

`export_to_file()` writes the subject-mandated layout: hex grid one row per
line, blank line, `entry_x,entry_y`, `exit_x,exit_y`, the path string,
trailing newline.

## Reproducibility

Same `(seed, width, height, perfect, entry, exit_)` always produces the
same maze. The seed actually used is stored on `gen.seed` (handy when you
called the constructor with `seed=None`).
