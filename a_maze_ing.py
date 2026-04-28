from __future__ import annotations

import sys
from dataclasses import dataclass

from cli import run_cli
from maze_types import Cell, Maze, Coordinate
from solver import find_shortest_path
from validators import validate_maze
from writer import write_output_file
from mazegen.generator import MazeGenerator

@dataclass
class Config:
    width: int = 10
    height: int = 10
    entry: Coordinate = (0, 0)
    exit: Coordinate = (9, 9)
    output_file: str = "maze.txt"
    perfect: bool = True
    seed: int | None = None

def load_config(config_file: str) -> Config:
    cfg = Config()
    valid_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT", "SEED"}
    try:
        with open(config_file, "r") as f:
            for line_idx, line in enumerate(f, 1):
                clean_line = line.split("#", 1)[0].strip()
                if not clean_line:
                    continue
                if "=" not in clean_line:
                    continue
                key, val = [part.strip() for part in clean_line.split("=", 1)]
                key_upper = key.upper()
                if key_upper not in valid_keys:
                    print(f"Warning: Unknown config key '{key}' on line {line_idx}.")
                    continue
                
                if key_upper == "WIDTH":
                    cfg.width = int(val)
                elif key_upper == "HEIGHT":
                    cfg.height = int(val)
                elif key_upper == "ENTRY":
                    parts = val.split(",")
                    cfg.entry = (int(parts[0].strip()), int(parts[1].strip()))
                elif key_upper == "EXIT":
                    parts = val.split(",")
                    cfg.exit = (int(parts[0].strip()), int(parts[1].strip()))
                elif key_upper == "OUTPUT_FILE":
                    cfg.output_file = val
                elif key_upper == "PERFECT":
                    cfg.perfect = val.lower() == "true"
                elif key_upper == "SEED":
                    cfg.seed = int(val)
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)
    
    return cfg

def generate_maze(config: Config) -> Maze:
    gen = MazeGenerator(width=config.width, height=config.height, seed=config.seed, perfect=config.perfect)
    gen.generate(entry=config.entry, exit_=config.exit)
    grid = gen.to_cells()
    return Maze(width=config.width, height=config.height, grid=grid, entry=config.entry, exit=config.exit, seed=gen.seed)


def main() -> int:
    """Main entry point matching the required project command style."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    config_file = sys.argv[1]

    try:
        config = load_config(config_file)
        maze = generate_maze(config)
        validate_maze(maze, config=config)

        shortest_path = find_shortest_path(maze)
        write_output_file(maze, shortest_path, config.output_file)

        run_cli(initial_maze=maze, regenerate_callback=lambda: generate_maze(config))
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
