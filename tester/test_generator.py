"""Unit tests for mazegen.MazeGenerator."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr

from mazegen import (
    EAST,
    MazeGenerator,
    NORTH,
    PATTERN_H,
    PATTERN_W,
    SOUTH,
    WEST,
)


def opened_walls(g: MazeGenerator) -> int:
    n = 0
    for y in range(g.height):
        for x in range(g.width):
            v = g.grid[y][x]
            if x + 1 < g.width and not (v & EAST):
                n += 1
            if y + 1 < g.height and not (v & SOUTH):
                n += 1
    return n


def isolated_cells(g: MazeGenerator) -> int:
    n = 0
    for y in range(g.height):
        for x in range(g.width):
            if g.grid[y][x] != 15:
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
                    0 <= nx < g.width
                    and 0 <= ny < g.height
                    and not (g.grid[ny][nx] & theirs)
                ):
                    ok = True
                    break
            if not ok:
                n += 1
    return n


def has_3x3_open(g: MazeGenerator) -> bool:
    for by in range(g.height - 2):
        for bx in range(g.width - 2):
            ok = True
            for cy in range(by, by + 3):
                for cx in range(bx, bx + 3):
                    v = g.grid[cy][cx]
                    if cx < bx + 2 and v & EAST:
                        ok = False
                    if cy < by + 2 and v & SOUTH:
                        ok = False
            if ok:
                return True
    return False


def borders_closed(g: MazeGenerator) -> bool:
    for x in range(g.width):
        if not (g.grid[0][x] & NORTH):
            return False
        if not (g.grid[g.height - 1][x] & SOUTH):
            return False
    for y in range(g.height):
        if not (g.grid[y][0] & WEST):
            return False
        if not (g.grid[y][g.width - 1] & EAST):
            return False
    return True


def walls_coherent(g: MazeGenerator) -> bool:
    for y in range(g.height):
        for x in range(g.width):
            v = g.grid[y][x]
            if x + 1 < g.width:
                if bool(v & EAST) != bool(g.grid[y][x + 1] & WEST):
                    return False
            if y + 1 < g.height:
                if bool(v & SOUTH) != bool(g.grid[y + 1][x] & NORTH):
                    return False
    return True


class TestConstructor(unittest.TestCase):
    def test_minimum_2x2(self):
        g = MazeGenerator(2, 2, seed=1)
        self.assertEqual(g.width, 2)
        self.assertEqual(g.height, 2)

    def test_one_dimension_too_small_raises(self):
        with self.assertRaises(ValueError):
            MazeGenerator(1, 5)
        with self.assertRaises(ValueError):
            MazeGenerator(5, 1)
        with self.assertRaises(ValueError):
            MazeGenerator(0, 0)

    def test_negative_size_raises(self):
        with self.assertRaises(ValueError):
            MazeGenerator(-1, 5)
        with self.assertRaises(ValueError):
            MazeGenerator(5, -3)

    def test_default_exit_is_corner(self):
        g = MazeGenerator(7, 4, seed=1)
        self.assertEqual(g.exit_, (6, 3))

    def test_seed_stored(self):
        g = MazeGenerator(5, 5, seed=99)
        self.assertEqual(g.seed, 99)

    def test_random_seed_when_none(self):
        g = MazeGenerator(5, 5)
        self.assertIsInstance(g.seed, int)
        self.assertGreaterEqual(g.seed, 0)


class TestGenerate(unittest.TestCase):
    def test_generates_without_error(self):
        g = MazeGenerator(20, 15, seed=42)
        g.generate()

    def test_default_entry_exit(self):
        g = MazeGenerator(10, 10, seed=1)
        g.generate()
        self.assertEqual(g.entry, (0, 0))
        self.assertEqual(g.exit_, (9, 9))

    def test_custom_entry_exit(self):
        g = MazeGenerator(20, 15, seed=1)
        g.generate(entry=(3, 4), exit_=(15, 10))
        self.assertEqual(g.entry, (3, 4))
        self.assertEqual(g.exit_, (15, 10))

    def test_entry_eq_exit_raises(self):
        g = MazeGenerator(10, 10, seed=1)
        with self.assertRaises(ValueError):
            g.generate(entry=(5, 5), exit_=(5, 5))

    def test_entry_oob_raises(self):
        g = MazeGenerator(10, 10, seed=1)
        with self.assertRaises(ValueError):
            g.generate(entry=(-1, 0), exit_=(9, 9))
        with self.assertRaises(ValueError):
            g.generate(entry=(10, 0), exit_=(9, 9))
        with self.assertRaises(ValueError):
            g.generate(entry=(0, 100), exit_=(9, 9))

    def test_exit_oob_raises(self):
        g = MazeGenerator(10, 10, seed=1)
        with self.assertRaises(ValueError):
            g.generate(entry=(0, 0), exit_=(10, 0))

    def test_seed_reproducibility(self):
        a = MazeGenerator(20, 15, seed=42, perfect=True)
        a.generate()
        b = MazeGenerator(20, 15, seed=42, perfect=True)
        b.generate()
        self.assertEqual(a.to_hex_string(), b.to_hex_string())

    def test_different_seeds_differ(self):
        a = MazeGenerator(20, 15, seed=1, perfect=True)
        a.generate()
        b = MazeGenerator(20, 15, seed=2, perfect=True)
        b.generate()
        self.assertNotEqual(a.to_hex_string(), b.to_hex_string())

    def test_generate_twice_resets(self):
        g = MazeGenerator(20, 15, seed=42, perfect=True)
        g.generate()
        first = g.to_hex_string()
        g.generate()
        self.assertEqual(g.to_hex_string(), first)


class TestPerfectInvariants(unittest.TestCase):
    def setUp(self):
        self.g = MazeGenerator(20, 15, seed=42, perfect=True)
        self.g.generate(entry=(0, 0), exit_=(19, 14))

    def test_perimeter_closed(self):
        self.assertTrue(borders_closed(self.g))

    def test_walls_coherent(self):
        self.assertTrue(walls_coherent(self.g))

    def test_no_3x3_open(self):
        self.assertFalse(has_3x3_open(self.g))

    def test_perfect_invariant(self):
        opened = opened_walls(self.g)
        iso = isolated_cells(self.g)
        reach = self.g.width * self.g.height - iso
        self.assertEqual(opened, reach - 1)

    def test_42_visible_when_big_enough(self):
        self.assertTrue(self.g.has_42)
        self.assertGreater(isolated_cells(self.g), 0)


class TestNonPerfectInvariants(unittest.TestCase):
    def setUp(self):
        self.g = MazeGenerator(20, 15, seed=42, perfect=False)
        self.g.generate(entry=(0, 0), exit_=(19, 14))

    def test_perimeter_closed(self):
        self.assertTrue(borders_closed(self.g))

    def test_walls_coherent(self):
        self.assertTrue(walls_coherent(self.g))

    def test_no_3x3_open(self):
        self.assertFalse(has_3x3_open(self.g))

    def test_more_openings_than_perfect(self):
        perf = MazeGenerator(20, 15, seed=42, perfect=True)
        perf.generate(entry=(0, 0), exit_=(19, 14))
        self.assertGreater(opened_walls(self.g), opened_walls(perf))


class Test42Pattern(unittest.TestCase):
    def test_too_small_skipped_with_stderr(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            g = MazeGenerator(8, 8, seed=1)
            g.generate()
        self.assertFalse(g.has_42)
        self.assertIn("Error", buf.getvalue())
        self.assertIn("42", buf.getvalue())

    def test_too_small_no_message_when_writes_to_stdout(self):
        # should write to stderr, NOT stdout
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stderr(err):
            old = sys.stdout
            sys.stdout = out
            try:
                g = MazeGenerator(8, 8, seed=1)
                g.generate()
            finally:
                sys.stdout = old
        self.assertNotIn("Error", out.getvalue())
        self.assertIn("Error", err.getvalue())

    def test_just_fits(self):
        # PATTERN is 5x9 with 2-cell margin -> minimum 9x13 (W x H)
        min_w = PATTERN_W + 4
        min_h = PATTERN_H + 4
        g = MazeGenerator(min_w, min_h, seed=1)
        g.generate(entry=(0, 0), exit_=(min_w - 1, min_h - 1))
        self.assertTrue(g.has_42)

    def test_one_below_skipped(self):
        # one less than minimum on either axis
        buf = io.StringIO()
        with redirect_stderr(buf):
            g = MazeGenerator(PATTERN_W + 3, PATTERN_H + 4, seed=1)
            g.generate()
        self.assertFalse(g.has_42)

    def test_42_does_not_overwrite_entry_exit(self):
        # place entry/exit inside where stencil would land
        g = MazeGenerator(20, 15, seed=42)
        # Grid centre will overlap stencil. Exit is at (10, 7) which is in the
        # 5x9 stencil region (centred at 10 +/- 4, 7 +/- 2).
        g.generate(entry=(0, 0), exit_=(10, 7))
        self.assertNotIn(g.entry, g._solid)
        self.assertNotIn(g.exit_, g._solid)


class TestExport(unittest.TestCase):
    def test_hex_string_shape(self):
        g = MazeGenerator(20, 15, seed=42)
        g.generate()
        rows = g.to_hex_string().split("\n")
        self.assertEqual(len(rows), 15)
        for row in rows:
            self.assertEqual(len(row), 20)

    def test_hex_uppercase(self):
        g = MazeGenerator(20, 15, seed=42)
        g.generate()
        for ch in g.to_hex_string().replace("\n", ""):
            self.assertIn(ch, "0123456789ABCDEF")

    def test_export_to_file_format(self):
        import tempfile

        g = MazeGenerator(15, 10, seed=42, perfect=True)
        g.generate(entry=(0, 0), exit_=(14, 9))
        path = g.solve(entry=(0, 0), exit_=(14, 9))
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            tmp = f.name
        try:
            g.export_to_file(tmp, (0, 0), (14, 9), path)
            with open(tmp) as f:
                text = f.read()
        finally:
            import os

            os.unlink(tmp)
        self.assertTrue(text.endswith("\n"))
        lines = text.split("\n")[:-1]
        # 10 hex rows + blank + entry + exit + path = 14
        self.assertEqual(len(lines), 14)
        self.assertEqual(lines[10], "")
        self.assertEqual(lines[11], "0,0")
        self.assertEqual(lines[12], "14,9")
        self.assertTrue(all(c in "NESW" for c in lines[13]))


if __name__ == "__main__":
    unittest.main()
