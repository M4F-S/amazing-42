*This project has been created as part of the 42 curriculum by mfathy, klavashc.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and solver written in Python. It reads a
plain-text configuration file, generates a randomised maze (perfect or
with loops), embeds a "42" stencil in the centre when the grid is
large enough, computes the shortest path with BFS, writes the result
to disk in the subject's hexadecimal format, and renders the maze in
the terminal with an interactive menu.

The maze-generation logic is shipped as a standalone, pip-installable
package called `mazegen` so it can be reused in other projects.

## Instructions

Requires Python 3.10 or later.

```bash
make install        # set up a venv and install build deps
make run            # run with the default config.txt
make lint           # flake8 + mypy
make clean
```

Or run directly:

```bash
python3 a_maze_ing.py config.txt
```

While the maze is on screen the menu accepts:

| key | action            |
|-----|-------------------|
| `1` | regenerate maze   |
| `2` | toggle path       |
| `3` | cycle wall colour |
| `4` | quit              |

## Configuration file

One `KEY=VALUE` per line. Lines starting with `#` (and anything after
`#` on a line) are ignored. Keys are case-insensitive.

| key           | type       | example          | meaning                           |
|---------------|------------|------------------|-----------------------------------|
| `WIDTH`       | int >= 2   | `WIDTH=20`       | maze width in cells               |
| `HEIGHT`      | int >= 2   | `HEIGHT=15`      | maze height in cells              |
| `ENTRY`       | `x,y`      | `ENTRY=0,0`      | entry cell                        |
| `EXIT`        | `x,y`      | `EXIT=19,14`     | exit cell (must differ from ENTRY)|
| `OUTPUT_FILE` | string     | `OUTPUT_FILE=maze.txt` | output filename             |
| `PERFECT`     | bool       | `PERFECT=True`   | one path between any two cells    |
| `SEED`        | int (opt.) | `SEED=42`        | reproducibility seed              |

A bad value (missing key, malformed line, letters in place of numbers,
non-boolean PERFECT, malformed coordinates) is reported on stderr and
the program exits with status 1 instead of crashing.

## Algorithm

We use the **randomised recursive backtracker** (depth-first search
with random neighbour selection):

1. Mark the entry cell as visited; push it on a stack.
2. From the top of the stack, pick a random unvisited neighbour, knock
   down the wall between the two cells, mark the neighbour visited,
   push it.
3. If no unvisited neighbour exists, pop and try again.
4. Stop when the stack is empty.

This produces a *perfect* maze (a spanning tree of the cell grid):
every cell is reachable, and there is exactly one path between any two
cells, so `PERFECT=True` is satisfied without a separate connectivity
pass.

When `PERFECT=False`, a second pass knocks down roughly
`width * height / 8` extra internal walls. Each candidate is rejected
unless it (a) does not touch the "42" stencil and (b) would not create
a 3×3 fully open area. East- and south-facing candidates are picked
with equal probability so the result has no directional bias.

### Why this algorithm

* It produces a perfect maze by construction, with no post-processing.
* It runs in `O(width * height)` time and stack memory.
* Compared to Prim/Kruskal it produces longer winding corridors, which
  look closer to the maze examples in the subject.

### The "42" stencil

A 5×9 mask of the digits "4" and "2" is reserved before carving. Those
cells are added to a forbidden set and pre-marked visited, so the DFS
routes around them. The loop pass also refuses any wall touching a
forbidden cell, and a final sealing pass closes their neighbours'
walls defensively. If the maze is smaller than 13×9 (5+4 by 9+4) the
stencil is skipped and `Error: maze too small to embed '42' …` is
printed on stderr.

### Shortest path

`MazeGenerator.solve` runs BFS from `entry` and reconstructs the path
to `exit_` using parent pointers. It returns a list of single-letter
direction strings (`N`, `E`, `S`, `W`), an empty list if entry equals
exit, or `None` when no path exists.

### Output file format

```
<HEIGHT lines of WIDTH uppercase hex digits>
<empty line>
<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path string, e.g. EESSEEN…>
```

Each cell's hex digit packs four wall bits (closed = 1):
`NORTH = 1`, `EAST = 2`, `SOUTH = 4`, `WEST = 8`.

## Reusable module

The generator is the package `mazegen`, shipped as
`mazegen-1.0.1-py3-none-any.whl` and `mazegen-1.0.1.tar.gz` at the
repo root. Both `pyproject.toml` and the `mazegen/` source tree are
committed, so a grader can rebuild the wheel from source:

```bash
python3 -m venv .venv
.venv/bin/pip install build
.venv/bin/python -m build
```

Install in another project:

```bash
pip install mazegen-1.0.1-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, seed=42, perfect=True)
gen.generate(entry=(0, 0), exit_=(19, 14))
path = gen.solve(entry=(0, 0), exit_=(19, 14))   # ['E', 'E', 'S', ...]
print(gen.to_hex_string())
gen.export_to_file("maze.txt", entry=(0, 0), exit_=(19, 14), path=path)
```

The grid is exposed as `gen.grid[y][x]` (4-bit ints). See
`mazegen/README.md` for the full API.

## Team and process

**Roles**

* **mfathy** — the `mazegen` package: DFS generator, BFS solver, "42"
  stencil, hex export, packaging (wheel + sdist), `pyproject.toml`.
* **klavashc** — `a_maze_ing.py`, config parser, ASCII renderer,
  interactive loop, error handling, Makefile.

**Planning and how it evolved**

We split the work along the package boundary on day one: one of us
owned the reusable generator, the other owned everything that calls
it. That meant we could work in parallel without merge conflicts. The
original plan kept a separate `Cell` dataclass between the two halves;
during integration we collapsed that to direct bitmask access on
`gen.grid`, which deleted ~150 lines of glue code and removed two
indentation bugs we had introduced.

**What worked**

* Locking the wall encoding (4-bit int per cell, `N=1 E=2 S=4 W=8`) on
  day one made integration trivial — both sides spoke the same format.
* Building the wheel early caught a packaging issue (`maze_types`
  cross-import) before it became a defence problem.

**What we'd improve**

* Earlier end-to-end runs. We were each green on our own but the first
  full `python3 a_maze_ing.py config.txt` only happened on day three,
  and that's when we found a couple of indentation issues in the
  validator and solver.
* More automated tests — we relied on manual smoke runs.

**Tools**

* `flake8` + `mypy` for lint and types (via `make lint`).
* `python -m build` for the wheel.
* `git` and GitHub for collaboration.
* AI assistants (Claude, Perplexity) — see Resources.

## Resources

* [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* Jamis Buck — *Mazes for Programmers*, especially the chapter on
  recursive backtracking.
* [Think Labyrinth! — algorithm reference](http://www.astrolog.org/labyrnth/algrithm.htm)
* [Python Packaging User Guide](https://packaging.python.org/) — used
  to build the wheel.

### How AI was used

We used Claude and Perplexity as code-review and audit assistants:

* Cross-checking the subject PDF against the codebase to spot missing
  artefacts (no README sections, missing wheel, unused imports).
* Reviewing the generator and the partner modules — catching
  indentation bugs, an east-only loop bias in `_add_loops`, and a
  quadratic memory pattern in BFS that we replaced with parent
  pointers.
* Drafting the *structure* of this README (sections and ordering).

All algorithmic decisions, the bitmask wall encoding, the "42"
stencil, the package structure and the actual implementation of
`MazeGenerator` were written and reviewed by us. AI suggestions that
landed in the repo were hand-verified before commit.
