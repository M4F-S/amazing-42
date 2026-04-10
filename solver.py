from collections import deque
from typing import Dict, List, Optional

from maze_types import Coordinate, Maze

DIRS: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

OPPOSITE: dict[str, str] = {
    "N": "S",
    "E": "W",
    "S": "N",
    "W": "E",
}


def can_move(maze: Maze, x: int, y: int, direction: str) -> bool:
    cell = maze.grid[y][x]
    if direction == "N":
        return not cell.north and y > 0
    if direction == "E":
        return not cell.east and x < maze.width - 1
    if direction == "S":
        return not cell.south and y < maze.height - 1
    if direction == "W":
        return not cell.west and x > 0
    raise ValueError(f"Invalid direction: {direction}")


def get_neighbors(maze: Maze, pos: Coordinate) -> list[tuple[Coordinate, str]]:
    x, y = pos
    neighbors: list[tuple[Coordinate, str]] = []
    for direction, (dx, dy) in DIRS.items():
        if can_move(maze, x, y, direction):
            neighbors.append(((x + dx, y + dy), direction))
    return neighbors


def find_shortest_path(maze: Maze) -> str:
    start = maze.entry
    goal = maze.exit

    queue = deque([start])
    visited: set[Coordinate] = {start}
    parent: dict[Coordinate, tuple[Coordinate, str]] = {}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        for next_pos, direction in get_neighbors(maze, current):
            if next_pos not in visited:
                visited.add(next_pos)
                parent[next_pos] = (current, direction)
                queue.append(next_pos)

    if goal not in visited:
        raise ValueError("No valid path from entry to exit")

    return reconstruct_path(parent, start, goal)


def reconstruct_path(
    parent: dict[Coordinate, tuple[Coordinate, str]],
    start: Coordinate,
    goal: Coordinate,
) -> str:
    path: list[str] = []
    current = goal

    while current != start:
        previous, direction = parent[current]
        path.append(direction)
        current = previous

    path.reverse()
    return "".join(path)


def validate_path(maze: Maze, path: str) -> bool:
    x, y = maze.entry

    for direction in path:
        if not can_move(maze, x, y, direction):
            return False
        dx, dy = DIRS[direction]
        x += dx
        y += dy

    return (x, y) == maze.exit
