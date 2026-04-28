from __future__ import annotations

from maze_types import Maze


def validate_coordinates(maze: Maze) -> None:
    """Ensure entry and exit are inside the maze."""
    for name, (x, y) in (("entry", maze.entry), ("exit", maze.exit)):
        if not (0 <= x < maze.width and 0 <= y < maze.height):
            raise ValueError(f"{name} is out of bounds: {(x, y)}")


def validate_grid_shape(maze: Maze) -> None:
    """Ensure grid dimensions match maze width and height."""
    if len(maze.grid) != maze.height:
        raise ValueError("Grid height does not match maze.height")
    for row in maze.grid:
        if len(row) != maze.width:
            raise ValueError("Grid width does not match maze.width")


def validate_neighbor_consistency(maze: Maze) -> None:
    """Ensure shared walls match between neighbouring cells."""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]
            if x + 1 < maze.width and cell.east != maze.grid[y][x + 1].west:
                raise ValueError(f"Inconsistent east/west walls at {(x, y)}")
            if y + 1 < maze.height and cell.south != maze.grid[y + 1][x].north:
                raise ValueError(f"Inconsistent south/north walls at {(x, y)}")


def validate_perimeter(maze: Maze) -> None:
    """Ensure perimeter walls are closed, except for entry and exit if they lie on the boundary."""
    for x in range(maze.width):
        cell_top = maze.grid[0][x]
        cell_bot = maze.grid[maze.height - 1][x]
        if (x, 0) != maze.entry and (x, 0) != maze.exit and not cell_top.north:
            raise ValueError(f"Open perimeter top wall at {(x, 0)}")
        if (x, maze.height - 1) != maze.entry and (x, maze.height - 1) != maze.exit and not cell_bot.south:
            raise ValueError(f"Open perimeter bottom wall at {(x, maze.height - 1)}")
    
    for y in range(maze.height):
        cell_left = maze.grid[y][0]
        cell_right = maze.grid[y][maze.width - 1]
        if (0, y) != maze.entry and (0, y) != maze.exit and not cell_left.west:
            raise ValueError(f"Open perimeter left wall at {(0, y)}")
        if (maze.width - 1, y) != maze.entry and (maze.width - 1, y) != maze.exit and not cell_right.east:
            raise ValueError(f"Open perimeter right wall at {(maze.width - 1, y)}")

def validate_3x3_fully_open(maze: Maze) -> None:
    """Ensure there are no 3x3 fully open areas in the maze."""
    for y in range(maze.height - 2):
        for x in range(maze.width - 2):
            all_open = True
            for cy in range(y, y + 3):
                for cx in range(x, x + 3):
                    cell = maze.grid[cy][cx]
                    if cx < x + 2 and cell.east:
                        all_open = False
                    if cy < y + 2 and cell.south:
                        all_open = False
            if all_open:
                raise ValueError(f"Found a 3x3 fully open area at {(x, y)}")

def validate_connectivity(maze: Maze) -> None:
    """Ensure there is a path from the entry to the exit using BFS."""
    from collections import deque
    queue = deque([maze.entry])
    visited = {maze.entry}
    from solver import DIRS

    found = False
    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == maze.exit:
            found = True
            break
        
        cell = maze.grid[cy][cx]
        neighbors = []
        if not cell.north and cy > 0: neighbors.append((cx, cy - 1))
        if not cell.east and cx < maze.width - 1: neighbors.append((cx + 1, cy))
        if not cell.south and cy < maze.height - 1: neighbors.append((cx, cy + 1))
        if not cell.west and cx > 0: neighbors.append((cx - 1, cy))

        for nx, ny in neighbors:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
    
    if not found:
        raise ValueError("Maze is not fully connected from entry to exit")

def validate_perfect_maze(maze: Maze) -> None:
    """When PERFECT=True, count of opened walls must equal (width*height) - 1. (perfect-maze invariant)"""
    open_walls_count = 0

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.grid[y][x]
            if x + 1 < maze.width and not cell.east:
                open_walls_count += 1
            if y + 1 < maze.height and not cell.south:
                open_walls_count += 1
                
    expected_open_walls = (maze.width * maze.height) - 1
    
    # Exclude cells that belong to the solid 42 stencil.
    solid_cells = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.grid[y][x].is_42:
                solid_cells += 1
    
    # Adjust spanning tree invariant for removed vertexes from the solid block.
    # Vertices count is V = (W * H) - solid_cells.
    # In a spanning tree, Edges E = V - 1, so expected edges = (W * H) - solid_cells - 1.
    expected_open_walls = (maze.width * maze.height) - solid_cells - 1

    if open_walls_count != expected_open_walls:
        raise ValueError(f"Perfect maze invariant failed. Opened walls: {open_walls_count}, Expected {(maze.width * maze.height) - 1} adjusted to {expected_open_walls}.")

def validate_maze(maze: Maze, config=None) -> None:
    """Run all basic maze checks needed by Student B modules."""
    validate_grid_shape(maze)
    validate_coordinates(maze)
    validate_neighbor_consistency(maze)
    validate_perimeter(maze)
    validate_3x3_fully_open(maze)
    validate_connectivity(maze)
    if config and getattr(config, 'perfect', False):
        validate_perfect_maze(maze)
