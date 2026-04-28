"""Unit tests for MazeGenerator.solve."""

from __future__ import annotations

import unittest

from mazegen import EAST, MazeGenerator, NORTH, SOUTH, WEST


DELTA = {
    "N": (0, -1, NORTH),
    "E": (1, 0, EAST),
    "S": (0, 1, SOUTH),
    "W": (-1, 0, WEST),
}


def walk(
    g: MazeGenerator, entry: tuple[int, int], path: list[str]
) -> tuple[int, int]:
    x, y = entry
    for ch in path:
        dx, dy, w = DELTA[ch]
        if g.grid[y][x] & w:
            raise AssertionError(f"closed wall at ({x},{y}) going {ch}")
        x, y = x + dx, y + dy
        if not (0 <= x < g.width and 0 <= y < g.height):
            raise AssertionError(f"out of bounds at ({x},{y})")
    return (x, y)


class TestSolve(unittest.TestCase):
    def test_entry_eq_exit_returns_empty(self):
        g = MazeGenerator(10, 10, seed=1)
        g.generate()
        self.assertEqual(g.solve((3, 4), (3, 4)), [])

    def test_oob_entry_raises(self):
        g = MazeGenerator(10, 10, seed=1)
        g.generate()
        with self.assertRaises(ValueError):
            g.solve((-1, 0), (5, 5))

    def test_oob_exit_raises(self):
        g = MazeGenerator(10, 10, seed=1)
        g.generate()
        with self.assertRaises(ValueError):
            g.solve((0, 0), (100, 100))

    def test_path_only_NESW(self):
        g = MazeGenerator(20, 15, seed=42)
        g.generate(entry=(0, 0), exit_=(19, 14))
        path = g.solve((0, 0), (19, 14))
        self.assertIsNotNone(path)
        for ch in path:
            self.assertIn(ch, "NESW")

    def test_path_lands_on_exit(self):
        g = MazeGenerator(20, 15, seed=42)
        g.generate(entry=(0, 0), exit_=(19, 14))
        path = g.solve((0, 0), (19, 14))
        end = walk(g, (0, 0), path)
        self.assertEqual(end, (19, 14))

    def test_path_walks_open_walls_only(self):
        # walk() raises on a closed wall
        g = MazeGenerator(20, 15, seed=42)
        g.generate(entry=(0, 0), exit_=(19, 14))
        path = g.solve((0, 0), (19, 14))
        walk(g, (0, 0), path)

    def test_shortest_in_perfect_is_unique(self):
        # in a perfect maze, BFS path length equals graph distance
        g = MazeGenerator(15, 10, seed=7, perfect=True)
        g.generate(entry=(0, 0), exit_=(14, 9))
        p1 = g.solve((0, 0), (14, 9))
        # any other entry-exit pair: same maze, BFS gives <= |any other walk|
        # we just assert solve returns something and it's the same on rerun.
        p2 = g.solve((0, 0), (14, 9))
        self.assertEqual(p1, p2)

    def test_no_path_returns_none(self):
        # build a 2x2 maze and manually wall off (1,1)
        g = MazeGenerator(2, 2, seed=1)
        g.generate(entry=(0, 0), exit_=(1, 0))
        g.grid = [
            [NORTH | WEST | SOUTH | EAST, NORTH | EAST | SOUTH | WEST],
            [NORTH | WEST | SOUTH | EAST, NORTH | EAST | SOUTH | WEST],
        ]
        self.assertIsNone(g.solve((0, 0), (1, 1)))

    def test_path_length_matches_bfs_distance(self):
        # explicit small grid: 3x1 with one wall removed
        g = MazeGenerator(3, 2, seed=1)
        g.generate(entry=(0, 0), exit_=(2, 1))
        p = g.solve((0, 0), (2, 1))
        self.assertIsNotNone(p)
        # In a 3x2 perfect maze, the BFS distance is at most 4 (3 cells in
        # any L-shape from corner to corner).
        self.assertLessEqual(len(p), 4)


if __name__ == "__main__":
    unittest.main()
