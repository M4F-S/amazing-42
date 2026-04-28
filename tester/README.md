# tester

Strict test suite for A-Maze-ing. Covers every requirement in the
subject PDF and every checkbox on the evaluation sheet.

## Run everything

From the repo root:

```bash
python3 tester/run_all.py        # quiet
python3 tester/run_all.py -v     # verbose
```

## Run one module

```bash
python3 -m unittest tester.test_generator -v
python3 -m unittest tester.test_solver -v
python3 -m unittest tester.test_config -v
python3 -m unittest tester.test_e2e -v
python3 -m unittest tester.test_packaging -v
```

## Validate a single output file

```bash
python3 tester/output_validator.py maze.txt 20 15 0 0 19 14 --perfect
```

Exits 0 on success and prints `OK`. On failure prints every violation
to stderr and exits 1.

## What each module covers

| File                 | Coverage                                           |
|----------------------|----------------------------------------------------|
| `test_generator.py`  | Constructor (size limits, seed, defaults), `generate()` (entry/exit validation, reproducibility, idempotence), perfect-maze invariants (perimeter, coherent walls, no 3×3, V-1 edges), non-perfect (more loops, still no 3×3), the "42" stencil (visible when grid is large enough, skipped on stderr otherwise, never overwrites entry/exit, "just fits" boundary at 13×9), hex output shape and case, `export_to_file` format. |
| `test_solver.py`     | `solve(entry, exit_)` — entry == exit returns `[]`, OOB raises, path letters only N/E/S/W, path walks open walls only, path lands on exit, no-path returns `None`, repeatable. |
| `test_config.py`     | Happy paths (basic, optional SEED, lower-case, mixed-case, comments full-line + inline, blank lines, whitespace around `=`, all truthy/falsy PERFECT values). Error paths (missing each required key, line without `=`, letters for int, negative/zero/one width, bad PERFECT, malformed coordinates with 1 or 3 parts or letters or empty, OOB ENTRY/EXIT, ENTRY==EXIT, empty OUTPUT_FILE, bad SEED, file not found, empty file, only-comments). |
| `test_e2e.py`        | `python3 a_maze_ing.py`: no args → exit 1, too many → exit 1, default config produces valid output file (validated by `output_validator`), `q`/`Q`/EOF all quit cleanly, menu shown, PERFECT=True invariants, PERFECT=False invariants, too-small prints "Error … 42 …" on stderr, all eval-sheet bad-config cases exit 1 with no `Traceback`, lower-case config keys work end-to-end. |
| `test_packaging.py`  | Wheel + tarball at repo root, `pyproject.toml` and `mazegen/` source present, wheel installs in a fresh venv, import + `generate` + `solve` work after install, `python -m build` rebuilds wheel + tarball from source. |

## Adding a new test

Each module uses Python's `unittest` (no third-party deps). Drop a new
file `test_xxx.py` here and add `tester.test_xxx` to `MODULES` in
`run_all.py`.
