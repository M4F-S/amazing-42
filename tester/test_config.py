"""Tests for the config parser in config.py."""

from __future__ import annotations

import os
import tempfile
import unittest

import config as cfg_mod


class _Fixture:
    """Holds a temp config file. Use as context manager."""

    def __init__(self, content: str) -> None:
        self.content = content

    def __enter__(self) -> str:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        )
        f.write(self.content)
        f.close()
        self.path = f.name
        return self.path

    def __exit__(self, *_a: object) -> None:
        os.unlink(self.path)


GOOD = (
    "WIDTH=20\n"
    "HEIGHT=15\n"
    "ENTRY=0,0\n"
    "EXIT=19,14\n"
    "OUTPUT_FILE=maze.txt\n"
    "PERFECT=True\n"
)


class TestHappyPaths(unittest.TestCase):
    def test_loads_basic(self):
        with _Fixture(GOOD) as p:
            cfg = cfg_mod.load(p)
        self.assertEqual(cfg.width, 20)
        self.assertEqual(cfg.height, 15)
        self.assertEqual(cfg.entry, (0, 0))
        self.assertEqual(cfg.exit_, (19, 14))
        self.assertEqual(cfg.output_file, "maze.txt")
        self.assertTrue(cfg.perfect)
        self.assertIsNone(cfg.seed)

    def test_optional_seed(self):
        with _Fixture(GOOD + "SEED=42\n") as p:
            cfg = cfg_mod.load(p)
        self.assertEqual(cfg.seed, 42)

    def test_lower_case_keys(self):
        content = (
            "width=20\n"
            "height=15\n"
            "entry=0,0\n"
            "exit=19,14\n"
            "output_file=m.txt\n"
            "perfect=true\n"
        )
        with _Fixture(content) as p:
            cfg = cfg_mod.load(p)
        self.assertEqual(cfg.width, 20)
        self.assertTrue(cfg.perfect)

    def test_mixed_case_keys(self):
        content = (
            "Width=20\n"
            "HeiGhT=15\n"
            "ENTRY=0,0\n"
            "exit=19,14\n"
            "OUTPUT_File=m.txt\n"
            "perfect=False\n"
        )
        with _Fixture(content) as p:
            cfg = cfg_mod.load(p)
        self.assertFalse(cfg.perfect)

    def test_full_line_comments_ignored(self):
        content = (
            "# this is a comment\n"
            "# another\n"
            + GOOD
            + "# trailing\n"
        )
        with _Fixture(content) as p:
            cfg_mod.load(p)

    def test_inline_comments_ignored(self):
        content = (
            "WIDTH=20  # comment after value\n"
            "HEIGHT=15\n"
            "ENTRY=0,0  #another\n"
            "EXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        with _Fixture(content) as p:
            cfg = cfg_mod.load(p)
        self.assertEqual(cfg.width, 20)

    def test_blank_lines_ignored(self):
        content = "\n\n" + GOOD + "\n\n"
        with _Fixture(content) as p:
            cfg_mod.load(p)

    def test_whitespace_around_equals(self):
        content = (
            "WIDTH = 20\n"
            "HEIGHT =15\n"
            "ENTRY= 0,0\n"
            "EXIT=19,14\n"
            "OUTPUT_FILE = maze.txt\n"
            "PERFECT=True\n"
        )
        with _Fixture(content) as p:
            cfg = cfg_mod.load(p)
        self.assertEqual(cfg.width, 20)
        self.assertEqual(cfg.entry, (0, 0))

    def test_truthy_perfect_values(self):
        for val in ("True", "true", "TRUE", "1", "yes"):
            with _Fixture(GOOD.replace("PERFECT=True", f"PERFECT={val}")) as p:
                self.assertTrue(cfg_mod.load(p).perfect, f"value {val!r}")

    def test_falsy_perfect_values(self):
        for val in ("False", "false", "FALSE", "0", "no"):
            with _Fixture(GOOD.replace("PERFECT=True", f"PERFECT={val}")) as p:
                self.assertFalse(cfg_mod.load(p).perfect, f"value {val!r}")


class TestErrorPaths(unittest.TestCase):
    def assertConfigErr(self, content: str) -> None:
        with _Fixture(content) as p:
            with self.assertRaises(cfg_mod.ConfigError):
                cfg_mod.load(p)

    def test_missing_width(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20\n", ""))

    def test_missing_height(self):
        self.assertConfigErr(GOOD.replace("HEIGHT=15\n", ""))

    def test_missing_entry(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0\n", ""))

    def test_missing_exit(self):
        self.assertConfigErr(GOOD.replace("EXIT=19,14\n", ""))

    def test_missing_output_file(self):
        self.assertConfigErr(GOOD.replace("OUTPUT_FILE=maze.txt\n", ""))

    def test_missing_perfect(self):
        self.assertConfigErr(GOOD.replace("PERFECT=True\n", ""))

    def test_line_without_equals(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20", "WIDTH 20"))

    def test_letters_for_int(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20", "WIDTH=ten"))

    def test_negative_width(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20", "WIDTH=-5"))

    def test_zero_width(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20", "WIDTH=0"))

    def test_one_width(self):
        self.assertConfigErr(GOOD.replace("WIDTH=20", "WIDTH=1"))

    def test_negative_height(self):
        self.assertConfigErr(GOOD.replace("HEIGHT=15", "HEIGHT=-3"))

    def test_bad_perfect(self):
        self.assertConfigErr(GOOD.replace("PERFECT=True", "PERFECT=maybe"))

    def test_bad_tuple_one_part(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=0"))

    def test_bad_tuple_three_parts(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=0,0,0"))

    def test_bad_tuple_letters(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=a,b"))

    def test_bad_tuple_empty(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY="))

    def test_entry_oob(self):
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=99,0"))
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=0,99"))
        self.assertConfigErr(GOOD.replace("ENTRY=0,0", "ENTRY=-1,0"))

    def test_exit_oob(self):
        self.assertConfigErr(GOOD.replace("EXIT=19,14", "EXIT=99,99"))

    def test_entry_eq_exit(self):
        self.assertConfigErr(GOOD.replace("EXIT=19,14", "EXIT=0,0"))

    def test_empty_output_file(self):
        self.assertConfigErr(
            GOOD.replace("OUTPUT_FILE=maze.txt", "OUTPUT_FILE=")
        )

    def test_seed_letters(self):
        self.assertConfigErr(GOOD + "SEED=abc\n")

    def test_file_not_found(self):
        with self.assertRaises(cfg_mod.ConfigError):
            cfg_mod.load("/tmp/__definitely_does_not_exist__.txt")

    def test_empty_file(self):
        # missing every required key
        self.assertConfigErr("")

    def test_only_comments(self):
        self.assertConfigErr("# only\n# comments\n# here\n")


if __name__ == "__main__":
    unittest.main()
