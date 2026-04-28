"""Standalone validator for the subject's maze.txt output format.

Usage:
    python3 tester/output_validator.py maze.txt WIDTH HEIGHT \\
        ENTRY_X ENTRY_Y EXIT_X EXIT_Y [--perfect]

Exits 0 on success, prints all violations and exits 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8


def validate(
    path: str,
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    perfect: bool,
) -> list[str]:
    errors: list[str] = []
    try:
        with open(path) as f:
            text = f.read()
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    if not text.endswith("\n"):
        errors.append("file does not end with \\n")

    raw_lines = text.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]

    expected_min_lines = height + 4
    if len(raw_lines) < expected_min_lines:
        errors.append(
            f"expected at least {expected_min_lines} lines, "
            f"got {len(raw_lines)}"
        )
        return errors

    hex_rows = raw_lines[:height]
    blank = raw_lines[height]
    entry_line = raw_lines[height + 1]
    exit_line = raw_lines[height + 2]
    path_line = raw_lines[height + 3]

    for i, row in enumerate(hex_rows):
        if len(row) != width:
            errors.append(
                f"row {i}: expected {width} chars, got {len(row)}"
            )
        for ch in row:
            if ch not in "0123456789ABCDEFabcdef":
                errors.append(f"row {i}: non-hex character {ch!r}")
                break

    if blank != "":
        errors.append(f"line {height}: expected blank line, got {blank!r}")

    expected_entry = f"{entry[0]},{entry[1]}"
    if entry_line != expected_entry:
        errors.append(
            f"entry line: expected {expected_entry!r}, got {entry_line!r}"
        )
    expected_exit = f"{exit_[0]},{exit_[1]}"
    if exit_line != expected_exit:
        errors.append(
            f"exit line: expected {expected_exit!r}, got {exit_line!r}"
        )

    for ch in path_line:
        if ch not in "NESW":
            errors.append(
                f"path line contains illegal char {ch!r} (only N/E/S/W)"
            )
            break

    if errors:
        return errors

    grid = [[int(c, 16) for c in row] for row in hex_rows]

    # walk the path
    delta = {
        "N": (0, -1, NORTH),
        "E": (1, 0, EAST),
        "S": (0, 1, SOUTH),
        "W": (-1, 0, WEST),
    }
    x, y = entry
    for i, ch in enumerate(path_line):
        dx, dy, wall = delta[ch]
        if grid[y][x] & wall:
            errors.append(
                f"path step {i} ({ch}): closed wall at ({x},{y})"
            )
            break
        x, y = x + dx, y + dy
        if not (0 <= x < width and 0 <= y < height):
            errors.append(f"path step {i}: went out of bounds")
            break
    if (x, y) != exit_ and not errors:
        errors.append(f"path ends at ({x},{y}), not exit {exit_}")

    # coherent walls
    for y in range(height):
        for x in range(width):
            v = grid[y][x]
            if x + 1 < width:
                if bool(v & EAST) != bool(grid[y][x + 1] & WEST):
                    errors.append(f"E/W mismatch at ({x},{y})")
            if y + 1 < height:
                if bool(v & SOUTH) != bool(grid[y + 1][x] & NORTH):
                    errors.append(f"S/N mismatch at ({x},{y})")

    # perimeter closed
    for x in range(width):
        if not grid[0][x] & NORTH:
            errors.append(f"open top border at x={x}")
        if not grid[height - 1][x] & SOUTH:
            errors.append(f"open bottom border at x={x}")
    for y in range(height):
        if not grid[y][0] & WEST:
            errors.append(f"open left border at y={y}")
        if not grid[y][width - 1] & EAST:
            errors.append(f"open right border at y={y}")

    # no 3x3 fully open
    for by in range(height - 2):
        for bx in range(width - 2):
            all_open = True
            for cy in range(by, by + 3):
                for cx in range(bx, bx + 3):
                    v = grid[cy][cx]
                    if cx < bx + 2 and v & EAST:
                        all_open = False
                    if cy < by + 2 and v & SOUTH:
                        all_open = False
            if all_open:
                errors.append(f"3x3 fully open area at ({bx},{by})")

    # perfect maze invariant
    if perfect:
        opened = 0
        for y in range(height):
            for x in range(width):
                v = grid[y][x]
                if x + 1 < width and not (v & EAST):
                    opened += 1
                if y + 1 < height and not (v & SOUTH):
                    opened += 1
        isolated = 0
        for y in range(height):
            for x in range(width):
                if grid[y][x] != 15:
                    continue
                ok = False
                for dx, dy, _, theirs in [
                    (0, -1, NORTH, SOUTH),
                    (1, 0, EAST, WEST),
                    (0, 1, SOUTH, NORTH),
                    (-1, 0, WEST, EAST),
                ]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and not (grid[ny][nx] & theirs)
                    ):
                        ok = True
                        break
                if not ok:
                    isolated += 1
        reach = width * height - isolated
        if opened != reach - 1:
            errors.append(
                f"not a perfect maze: opened={opened}, "
                f"expected reach-1={reach - 1}"
            )

    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("width", type=int)
    p.add_argument("height", type=int)
    p.add_argument("entry_x", type=int)
    p.add_argument("entry_y", type=int)
    p.add_argument("exit_x", type=int)
    p.add_argument("exit_y", type=int)
    p.add_argument("--perfect", action="store_true")
    args = p.parse_args()

    errs = validate(
        args.path,
        args.width,
        args.height,
        (args.entry_x, args.entry_y),
        (args.exit_x, args.exit_y),
        args.perfect,
    )
    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
