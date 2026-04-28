"""End-to-end subprocess tests of a_maze_ing.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def run(
    cfg_path: str,
    *,
    stdin: str = "q\n",
    timeout: int = 15,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(REPO / "a_maze_ing.py"), cfg_path],
        cwd=str(REPO),
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def write_cfg(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write(content)
    f.close()
    return f.name


GOOD = (
    "WIDTH=20\n"
    "HEIGHT=15\n"
    "ENTRY=0,0\n"
    "EXIT=19,14\n"
    "OUTPUT_FILE={out}\n"
    "PERFECT=True\n"
    "SEED=42\n"
)


class TestArgs(unittest.TestCase):
    def test_no_args_exits_1(self):
        r = subprocess.run(
            [PYTHON, str(REPO / "a_maze_ing.py")],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn("usage", r.stderr.lower())

    def test_too_many_args_exits_1(self):
        r = subprocess.run(
            [PYTHON, str(REPO / "a_maze_ing.py"), "a", "b"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 1)


class TestHappyRun(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkstemp(suffix=".txt")[1]
        os.unlink(self.out)
        self.cfg = write_cfg(GOOD.format(out=self.out))

    def tearDown(self):
        for p in (self.cfg, self.out):
            if os.path.exists(p):
                os.unlink(p)

    def test_runs_clean(self):
        r = run(self.cfg)
        self.assertEqual(r.returncode, 0, msg=r.stderr)

    def test_produces_output_file(self):
        run(self.cfg)
        self.assertTrue(os.path.exists(self.out))

    def test_output_format(self):
        run(self.cfg)
        from output_validator import validate

        errs = validate(self.out, 20, 15, (0, 0), (19, 14), perfect=True)
        self.assertEqual(errs, [])

    def test_q_uppercase_quits(self):
        r = run(self.cfg, stdin="Q\n")
        self.assertEqual(r.returncode, 0)

    def test_eof_quits(self):
        r = run(self.cfg, stdin="")
        self.assertEqual(r.returncode, 0)

    def test_menu_shown(self):
        r = run(self.cfg)
        self.assertIn("Regenerate", r.stdout)
        self.assertIn("Toggle path", r.stdout)
        self.assertIn("Quit", r.stdout)


class TestNonPerfect(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkstemp(suffix=".txt")[1]
        os.unlink(self.out)
        self.cfg = write_cfg(
            GOOD.format(out=self.out).replace("PERFECT=True", "PERFECT=False")
        )

    def tearDown(self):
        for p in (self.cfg, self.out):
            if os.path.exists(p):
                os.unlink(p)

    def test_runs_clean(self):
        r = run(self.cfg)
        self.assertEqual(r.returncode, 0, msg=r.stderr)

    def test_output_format(self):
        run(self.cfg)
        from output_validator import validate

        errs = validate(self.out, 20, 15, (0, 0), (19, 14), perfect=False)
        self.assertEqual(errs, [])


class TestTooSmall(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkstemp(suffix=".txt")[1]
        os.unlink(self.out)
        self.cfg = write_cfg(
            "WIDTH=8\nHEIGHT=8\nENTRY=0,0\nEXIT=7,7\n"
            f"OUTPUT_FILE={self.out}\nPERFECT=True\nSEED=1\n"
        )

    def tearDown(self):
        for p in (self.cfg, self.out):
            if os.path.exists(p):
                os.unlink(p)

    def test_runs_clean(self):
        r = run(self.cfg)
        self.assertEqual(r.returncode, 0, msg=r.stderr)

    def test_stderr_says_42_too_small(self):
        r = run(self.cfg)
        self.assertIn("Error", r.stderr)
        self.assertIn("42", r.stderr)

    def test_output_still_valid(self):
        run(self.cfg)
        from output_validator import validate

        errs = validate(self.out, 8, 8, (0, 0), (7, 7), perfect=True)
        self.assertEqual(errs, [])


class TestErrorConfigs(unittest.TestCase):
    """Every bad config in the eval sheet must produce exit 1, no crash."""

    def _run_with_cfg(self, content: str) -> subprocess.CompletedProcess:
        cfg = write_cfg(content)
        try:
            return run(cfg, stdin="")
        finally:
            os.unlink(cfg)

    def test_missing_required_key(self):
        for missing in (
            "WIDTH=20\n",
            "HEIGHT=15\n",
            "ENTRY=0,0\n",
            "EXIT=19,14\n",
            "OUTPUT_FILE=maze.txt\n",
            "PERFECT=True\n",
        ):
            base = (
                "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
                "OUTPUT_FILE=maze.txt\nPERFECT=True\n"
            )
            r = self._run_with_cfg(base.replace(missing, ""))
            self.assertEqual(
                r.returncode, 1,
                msg=f"missing {missing!r}: {r.stderr}",
            )
            self.assertIn("Error", r.stderr)

    def test_no_equals(self):
        r = self._run_with_cfg(
            "WIDTH=20\nHEIGHT 15\nENTRY=0,0\nEXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\nPERFECT=True\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_letters_for_int(self):
        r = self._run_with_cfg(
            "WIDTH=ten\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\nPERFECT=True\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_bad_bool(self):
        r = self._run_with_cfg(
            "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\nPERFECT=maybe\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_bad_tuple(self):
        r = self._run_with_cfg(
            "WIDTH=20\nHEIGHT=15\nENTRY=0\nEXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\nPERFECT=True\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_entry_eq_exit(self):
        r = self._run_with_cfg(
            "WIDTH=10\nHEIGHT=10\nENTRY=5,5\nEXIT=5,5\n"
            "OUTPUT_FILE=m.txt\nPERFECT=True\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_oob(self):
        r = self._run_with_cfg(
            "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=99,99\n"
            "OUTPUT_FILE=m.txt\nPERFECT=True\n"
        )
        self.assertEqual(r.returncode, 1)

    def test_file_not_found(self):
        r = run("/tmp/__nope__.txt", stdin="")
        self.assertEqual(r.returncode, 1)

    def test_no_crash_marker_in_stderr(self):
        # ensure no "Traceback" leaks through any error path
        for bad in (
            "WIDTH=ten\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
            "OUTPUT_FILE=m.txt\nPERFECT=True\n",
            "",
            "# only comments\n",
        ):
            r = self._run_with_cfg(bad)
            self.assertNotIn("Traceback", r.stderr, msg=f"crash on: {bad!r}")


class TestLowerCase(unittest.TestCase):
    def test_lowercase_keys_work(self):
        out = tempfile.mkstemp(suffix=".txt")[1]
        os.unlink(out)
        cfg = write_cfg(
            f"width=20\nheight=15\nentry=0,0\nexit=19,14\n"
            f"output_file={out}\nperfect=true\nseed=42\n"
        )
        try:
            r = run(cfg)
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertTrue(os.path.exists(out))
        finally:
            for p in (cfg, out):
                if os.path.exists(p):
                    os.unlink(p)


if __name__ == "__main__":
    unittest.main()
