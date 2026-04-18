from __future__ import annotations

from collections.abc import Callable

from ascii_renderer import render_maze
from colors import CLEAR_SCREEN, COLOR_PRESETS
from maze_types import Maze
from solver import find_shortest_path


class MazeUI:
    """Very small terminal UI for the ASCII version."""

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
        names = list(COLOR_PRESETS)
        index = names.index(self.color_name)
        self.color_name = names[(index + 1) % len(names)]

    def render(self) -> str:
        return render_maze(
            self.maze,
            show_path=self.show_path,
            shortest_path=self.shortest_path,
            colors=COLOR_PRESETS[self.color_name],
        )


def run_cli(initial_maze: Maze, regenerate_callback: Callable[[], Maze]) -> None:
    """Run a simple command loop for the ASCII renderer."""
    ui = MazeUI(initial_maze)

    while True:
        print(CLEAR_SCREEN, end="")
        print(ui.render())
        print()
        print(f"Current wall color preset: {ui.color_name}")
        print("[R]egenerate  [P]ath on/off  [C]olor  [Q]uit")
        command = input("> ").strip().lower()

        if command == "q":
            return
        if command == "p":
            ui.toggle_path()
        elif command == "c":
            ui.cycle_color()
        elif command == "r":
            ui.set_maze(regenerate_callback())
