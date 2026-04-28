#!/usr/bin/env python3
"""Entry point: python3 a_maze_ing.py config.txt"""

from __future__ import annotations

import sys

import config as cfg_module
import renderer
from mazegen import MazeGenerator


def build(cfg: cfg_module.Config) -> MazeGenerator:
    gen = MazeGenerator(
        cfg.width, cfg.height, seed=cfg.seed, perfect=cfg.perfect,
    )
    gen.generate(entry=cfg.entry, exit_=cfg.exit_)
    return gen


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        cfg = cfg_module.load(argv[1])
    except cfg_module.ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        gen = build(cfg)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    path = gen.solve(cfg.entry, cfg.exit_)

    try:
        gen.export_to_file(cfg.output_file, cfg.entry, cfg.exit_, path)
    except OSError as e:
        print(f"Error: cannot write {cfg.output_file!r}: {e}", file=sys.stderr)
        return 1

    def regenerate() -> MazeGenerator:
        # new seed each time so the user sees a different maze
        new_cfg = cfg_module.Config(
            cfg.width, cfg.height, cfg.entry, cfg.exit_,
            cfg.output_file, cfg.perfect, seed=None,
        )
        new_gen = build(new_cfg)
        new_path = new_gen.solve(cfg.entry, cfg.exit_)
        new_gen.export_to_file(cfg.output_file, cfg.entry, cfg.exit_, new_path)
        return new_gen

    try:
        renderer.run(gen, cfg.entry, cfg.exit_, regenerate)
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
