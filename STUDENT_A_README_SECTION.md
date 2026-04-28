<!--
Snippet for Student B to paste into the main README.md at the repo
root. Two paragraphs on the algorithm + 42 pattern, plus a "What's
reusable" section pointing at the mazegen wheel. Adjust headings to
match the surrounding README.
-->

## Algorithm

We use the **randomised recursive backtracker** (DFS), the algorithm
the subject mentions by name. From the entry cell the carver picks a
random unvisited neighbour, knocks down the wall between the two
cells, and recurses; when no unvisited neighbour exists it backtracks
via an explicit stack. This guarantees a *perfect* maze: every cell is
reachable, and there is exactly one path between any two cells.

When `PERFECT=False`, a post-processing pass knocks down roughly
`width * height / 8` additional internal walls. Each candidate is
accepted only if (a) it does not touch the `42` pattern and (b) it
would not create a 3x3 fully open area. East-facing and south-facing
walls are tried with equal probability, so the resulting maze has no
directional bias.

The maze is stored as one 4-bit integer per cell (`NORTH=1`, `EAST=2`,
`SOUTH=4`, `WEST=8`). Every wall change is applied to both adjacent
cells at once, so neighbouring walls are guaranteed consistent. The
perimeter borders stay closed by construction — the carver never
considers an out-of-bounds neighbour, so the outer walls are never
opened.

## The `42` pattern

The `42` stencil is a 5x9 mask centred in the grid. Before carving,
the cells of the stencil are added to a `_solid` set and pre-marked as
visited; the DFS therefore routes *around* them rather than through
them. The loop-creation pass also refuses to open any wall adjacent to
a stencil cell, and a final `_restore_solid_cells` step defensively
re-closes the walls around every stencil cell. The stencil is silently
skipped (with an `Error:` notice on stderr) when the maze is smaller
than `13x9`, which is the minimum required for a 2-cell margin on
every side.

## Shortest-path solving

`MazeGenerator.solve(entry, exit_)` runs **breadth-first search** over
the carved grid — the right tool for an unweighted graph and the
shortest path. It uses parent pointers and reconstructs the path at
the end, so memory stays linear in the grid size. The solver returns a
list of `"N"`/`"E"`/`"S"`/`"W"` direction letters, an empty list when
entry equals exit, or `None` when no path exists (possible only if a
non-perfect maze plus the `42` stencil walls off the exit).

## What's reusable, and how

The maze generator ships as a standalone, pip-installable package
named `mazegen`. The wheel (`mazegen-1.0.0-py3-none-any.whl`) is
checked in at the repo root.

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=20, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 19))
path = gen.solve(entry=(0, 0), exit_=(19, 19))
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 19), path=path)
```

The same source also lives at the repo root under `maze_generator.py`
as a thin re-export shim, so existing imports of the form
`from maze_generator import MazeGenerator` keep working unchanged.
