#!/usr/bin/env python3
"""Run every test module in this folder and print a coloured summary.

Usage:
    python3 tester/run_all.py [-v]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_module(name: str, verbose: bool) -> tuple[bool, float, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{REPO}{os.pathsep}{HERE}"
    cmd = [sys.executable, "-m", "unittest"]
    if verbose:
        cmd.append("-v")
    cmd.append(name)
    t0 = time.time()
    r = subprocess.run(
        cmd,
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
    )
    dt = time.time() - t0
    out = r.stdout + "\n" + r.stderr
    return r.returncode == 0, dt, out


MODULES = [
    "tester.test_generator",
    "tester.test_solver",
    "tester.test_config",
    "tester.test_e2e",
    "tester.test_packaging",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    # ensure tester/ is a package by virtue of being a folder; we run via
    # `python -m unittest tester.test_xxx` so all imports go through the repo
    # root. Make sure mazegen/, config.py, renderer.py are reachable.
    print(f"{BOLD}A-Maze-ing strict tester{RESET}")
    print(f"repo: {REPO}\n")

    results = []
    for mod in MODULES:
        print(f"{BOLD}»{RESET} running {mod} ... ", end="", flush=True)
        ok, dt, out = run_module(mod, args.verbose)
        results.append((mod, ok, dt, out))
        marker = f"{GREEN}OK{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"{marker} ({dt:.2f}s)")
        if not ok or args.verbose:
            print(out)

    total = sum(dt for _, _, dt, _ in results)
    failed = [m for m, ok, *_ in results if not ok]

    print()
    print(f"{BOLD}{'-' * 50}{RESET}")
    if failed:
        print(f"{RED}{BOLD}FAILED{RESET}: {', '.join(failed)} "
              f"(total {total:.2f}s)")
        return 1
    print(
        f"{GREEN}{BOLD}ALL TESTS PASSED{RESET} "
        f"({len(results)} modules, {total:.2f}s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
