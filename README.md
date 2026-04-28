*This project has been created as part of the 42 curriculum by mfathy, klavashc.*

## Description
**A-maze-ing** is a highly customizable Python-based maze generator and solver. It produces perfect or imperfect mazes, safely embeds a rigid "42" stencil in the center (when the grid allows), and visualizes the generated labyrinth and its shortest path using a lightweight ASCII terminal UI.

## Instructions
This project requires Python 3. You can set it up and run it using the provided Makefile:
```bash
make install
make run
```
You can also run the program manually:
```bash
python3 a_maze_ing.py config.txt
```

## Config File Format
The program is driven by a key-value format `config.txt`. Comments can be added using `#`.

```ini
# Maze dimensions
WIDTH=20
HEIGHT=15

# Start and end coordinates (X,Y)
ENTRY=0,0
EXIT=19,14

# Output file for the maze string
OUTPUT_FILE=maze.txt

# Generation parameters
PERFECT=True
SEED=42
```

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

The maze generator is decoupled from the UI and solving layers and shipped as a standalone, pip-installable Python wheel named `mazegen`. The wheel (`mazegen-1.0.1-py3-none-any.whl`) and its source tarball are checked in at the repo root, and `pyproject.toml` lets a grader rebuild them from source with `python -m build`.

**Installation**:
```bash
pip install mazegen-1.0.1-py3-none-any.whl
```

**Usage**:
```python
from mazegen import MazeGenerator

# Initialize 20x20 perfect maze
gen = MazeGenerator(width=20, height=20, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 19))

# Export purely structural `Cell` data
grid_cells = gen.to_cells()

# Solve for the shortest path
path = gen.solve(entry=(0, 0), exit_=(19, 19))
print("Shortest Path:", path)

# Or export string format directly to file
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 19), path=path)
```

The same source also lives at the repo root under `maze_generator.py`
as a thin re-export shim, so existing imports of the form
`from maze_generator import MazeGenerator` keep working unchanged.

## Team & Process

* **Roles**:
  * **Student A (mfathy)**: `mazegen` package — DFS backtracker, BFS solver, the `42` stencil, no-3x3-open-area enforcement, hex export, packaging (wheel + sdist).
  * **Student B (klavashc)**: Configuration parser, project orchestration in `a_maze_ing.py`, structural validators, file writer, ASCII renderer, interactive CLI, end-to-end test.
* **Planning**: We agreed up front on a shared data contract (the `Cell` dataclass, now living inside `mazegen` and re-exported from `maze_types.py`). That contract decoupled the generator from the UI/IO layers and let us work in parallel without merge conflicts.
* **What worked**: Splitting the package boundary on day one. The wheel built and installed cleanly, and the partner's modules consumed `gen.to_cells()` from the start.
* **What we'd improve**: Earlier integration testing — a couple of indentation issues in the validator/solver only surfaced when we wired everything together, not during unit work.

## Resources

* [Maze Generation Algorithms (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* [Jamis Buck — Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
* [Think Labyrinth — algorithm reference](http://www.astrolog.org/labyrnth/algrithm.htm)
* [Python Packaging User Guide](https://packaging.python.org/en/latest/) — used to build the `mazegen` wheel.

### How AI was used

We used Claude and Perplexity as review and audit assistants:

* Cross-checking subject requirements against the codebase and flagging gaps (missing wheel artefacts, README sections, unused imports, missing input validation).
* Code-review passes on the generator and the partner modules — catching indentation bugs, an east-only loop bias, and a quadratic memory pattern in BFS.
* Drafting the structure (not the content) of this README and of the package's docstrings.

All algorithmic choices, the bitmask wall encoding, the `42` stencil layout, the package structure, and the actual implementation were written and reviewed by us. AI-suggested code was hand-verified before commit; nothing landed unread.