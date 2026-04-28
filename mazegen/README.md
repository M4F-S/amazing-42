# mazegen

Randomised recursive backtracker maze generator with optional loops, an
embedded `42` stencil in the centre of large enough mazes, and BFS
shortest-path solving. Built for the 42 *amazing* project.

## Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Quick start

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=20, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 19))
path = gen.solve(entry=(0, 0), exit_=(19, 19))

print(gen.to_hex_string())
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 19), path=path)
```

## Wall encoding

Each cell is a 4-bit integer:

| bit | direction | value |
|-----|-----------|-------|
| 0   | NORTH     | 1     |
| 1   | EAST      | 2     |
| 2   | SOUTH     | 4     |
| 3   | WEST      | 8     |

A cell of `15` (`0xF`) has all four walls; `0` has none. Wall changes
are always applied to both adjacent cells, so the grid is internally
consistent.

## Algorithm

`MazeGenerator.generate()` runs an iterative randomised depth-first
search from the entry cell. At each step it picks a random unvisited
neighbour and knocks down the wall between the two cells. When no
unvisited neighbour exists, it backtracks via an explicit stack. This
produces a *perfect* maze (a single path between any two cells).

If `perfect=False`, a post-processing pass (`_add_loops`) knocks down
roughly `width * height / 8` additional internal walls, picking east
or south at random with equal probability, while refusing any opening
that would create a 3x3 fully open area.

## The `42` pattern

Before carving, `_embed_42` writes a 5x9 stencil of the digits "4" and
"2" into a `_solid` set centred in the grid. Cells in `_solid` are
pre-marked as visited so the carver routes around them, and `_add_loops`
explicitly skips any wall adjacent to a forbidden cell. After
generation, `_restore_solid_cells` defensively re-closes the walls
around every stencil cell so the output is guaranteed coherent.

If the maze is too small to fit the stencil with a 2-cell margin on
every side, the stencil is skipped and an `Error:` notice is printed
to stderr. Entry and exit cells are never overwritten by the stencil.

## Solving

`MazeGenerator.solve(entry, exit_)` runs BFS over the carved grid and
returns the shortest path as a list of single-letter direction strings
(`"N"`, `"E"`, `"S"`, `"W"`). It uses parent pointers and reconstructs
the path at the end, so memory is `O(width * height)` rather than
quadratic. Returns `None` when no path exists, or `[]` when entry
equals exit.

## Reproducibility

Pass `seed=<int>` to make generation deterministic. The same seed,
width, height, and entry/exit always produce the same maze.
