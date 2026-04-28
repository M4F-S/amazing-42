"""Wheel build + fresh-venv install tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class TestArtefactsPresent(unittest.TestCase):
    def test_wheel_at_root(self):
        wheels = list(REPO.glob("mazegen-*.whl"))
        self.assertEqual(
            len(wheels), 1, f"expected 1 wheel at root, got {wheels}"
        )

    def test_tarball_at_root(self):
        tars = list(REPO.glob("mazegen-*.tar.gz"))
        self.assertEqual(
            len(tars), 1, f"expected 1 tarball at root, got {tars}"
        )

    def test_pyproject_present(self):
        self.assertTrue((REPO / "pyproject.toml").exists())

    def test_mazegen_source_present(self):
        self.assertTrue((REPO / "mazegen" / "__init__.py").exists())
        self.assertTrue((REPO / "mazegen" / "generator.py").exists())


class TestWheelInstallable(unittest.TestCase):
    """Build a wheel from source, install in a clean venv, import + run."""

    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="mazegen-pkg-")
        cls.venv = os.path.join(cls.workdir, "venv")
        subprocess.run(
            [sys.executable, "-m", "venv", cls.venv], check=True
        )
        bin_dir = "Scripts" if os.name == "nt" else "bin"
        cls.pip = os.path.join(cls.venv, bin_dir, "pip")
        cls.python = os.path.join(cls.venv, bin_dir, "python")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def test_install_existing_wheel(self):
        wheel = next(REPO.glob("mazegen-*.whl"))
        r = subprocess.run(
            [self.pip, "install", "--quiet", str(wheel)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)

    def test_import_after_install(self):
        r = subprocess.run(
            [
                self.python,
                "-c",
                "from mazegen import MazeGenerator; "
                "g = MazeGenerator(10, 10, seed=1); g.generate(); "
                "print(g.solve((0,0),(9,9)))",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertTrue(r.stdout.strip().startswith("["))

    def test_rebuild_from_source(self):
        # build into an isolated tmp dir, verify wheel is produced
        build_dir = tempfile.mkdtemp(prefix="mazegen-build-")
        try:
            r = subprocess.run(
                [self.pip, "install", "--quiet", "build"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0)
            r = subprocess.run(
                [
                    self.python, "-m", "build",
                    "--outdir", build_dir,
                    str(REPO),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            wheels = list(Path(build_dir).glob("mazegen-*.whl"))
            tars = list(Path(build_dir).glob("mazegen-*.tar.gz"))
            self.assertEqual(len(wheels), 1)
            self.assertEqual(len(tars), 1)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
