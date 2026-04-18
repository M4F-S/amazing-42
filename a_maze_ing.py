from __future__ import annotations

import sys
from dataclasses import dataclass

from cli import run_cli
from maze_types import Cell, Maze
from solver import find_shortest_path
from validators import validate_maze
from writer import write_output_file


@dataclass
class Config:
    output_file: str = "maze.txt"


def load_config(_config_file: str) -> Config:
    """Placeholder config loader.

    Replace this with Student A's real parser.
    """
    return Config()


def generate_maze(_config: Config) -> Maze:
    """Placeholder maze generator.

    Replace this with Student A's real generator.
    The sample maze below gives Student B a working integration target.
    """
    grid = [
        [Cell(True, False, True, True), Cell(True, True, False, False)],
        [Cell(True, True, True, True, is_42=True), Cell(False, True, True, True)],
    ]
    return Maze(width=2, height=2, grid=grid, entry=(0, 0), exit=(1, 0))


def main() -> int:
    """Main entry point matching the required project command style."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    config_file = sys.argv[1]

    try:
        config = load_config(config_file)
        maze = generate_maze(config)
        validate_maze(maze)

        shortest_path = find_shortest_path(maze)
        write_output_file(maze, shortest_path, config.output_file)

        run_cli(initial_maze=maze, regenerate_callback=lambda: generate_maze(config))
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
