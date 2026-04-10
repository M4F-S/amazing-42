import sys

from cli import run_cli
from solver import find_shortest_path
from validators import validate_coordinates, validate_neighbor_consistency
from writer import write_output_file

#from config_parser import load_config
#from maze_generator import generate_maze


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    config_file = sys.argv[1]

    try:
        config = load_config(config_file)
        maze = generate_maze(config)

        validate_coordinates(maze)
        validate_neighbor_consistency(maze)

        shortest_path = find_shortest_path(maze)
        write_output_file(maze, shortest_path, config.output_file)

        run_cli(
            initial_maze=maze,
            regenerate_callback=lambda: generate_maze(config),
        )

    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
