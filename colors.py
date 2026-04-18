from __future__ import annotations

from dataclasses import dataclass

RESET = "\033[0m"
CLEAR_SCREEN = "\033[2J\033[H"


@dataclass(frozen=True)
class ColorScheme:
    wall: str = "\033[37m"
    path: str = "\033[32m"
    entry: str = "\033[34m"
    exit: str = "\033[31m"
    closed_42: str = "\033[35m"
    empty: str = "\033[0m"


COLOR_PRESETS: dict[str, ColorScheme] = {
    "default": ColorScheme(),
    "cyan": ColorScheme(wall="\033[36m"),
    "yellow": ColorScheme(wall="\033[33m"),
    "green": ColorScheme(wall="\033[32m"),
}
