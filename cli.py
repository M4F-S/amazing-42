from maze_types import Maze
from colors import COLOR_PRESETS, ColorScheme
from ascii_renderer import render_maze
from solver import find_shortest_path


class MazeUI:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.show_path = False
        self.color_name = "default"
        self.shortest_path = find_shortest_path(maze)

    def set_maze(self, maze: Maze) -> None:
        self.maze = maze
        self.shortest_path = find_shortest_path(maze)

    def toggle_path(self) -> None:
        self.show_path = not self.show_path

    def cycle_color(self) -> None:
        names = list(COLOR_PRESETS.keys())
        current_index = names.index(self.color_name)
        self.color_name = names[(current_index + 1) % len(names)]

    def render(self) -> str:
        colors = COLOR_PRESETS[self.color_name]
        return render_maze(
            self.maze,
            show_path=self.show_path,
            shortest_path=self.shortest_path,
            colors=colors,
        )


def run_cli(initial_maze: Maze, regenerate_callback) -> None:
    ui = MazeUI(initial_maze)

    while True:
        print("\033[2J\033[H", end="")
        print(ui.render())
        print()
        print("[R]egenerate  [P]ath on/off  [C]olor  [Q]uit")

        command = input("> ").strip().lower()

        if command == "q":
            break
        if command == "p":
            ui.toggle_path()
        elif command == "c":
            ui.cycle_color()
        elif command == "r":
            new_maze = regenerate_callback()
            ui.set_maze(new_maze)
