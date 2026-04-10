
import sys
import os
from typing import Optional


# ---- Custom Exceptions ----

class MazeError(Exception):
    """Base exception for all maze-related errors."""
    pass


class ConfigError(MazeError):
    """Raised when the configuration file has missing or invalid values."""
    pass


class MazeSizeError(MazeError):
    """Raised when the maze dimensions are too small or invalid."""
    pass


class MazeFileError(MazeError):
    """Raised when there is a problem reading or writing maze files."""
    pass


# ---- Error display helper ----

def print_error(msg: str) -> None:
    """
    Print a formatted error message to stderr.

    Args:
        msg: The error message to display.
    """
    print(f"[ERROR] {msg}", file=sys.stderr)


# ---- Config validation ----

def validate_config(config: dict) -> None:
    """

    Checks that all required keys are present and that their values make
    sense (e.g. width and height must be positive integers, entry and exit
    must be within bounds and different, etc.).

    Args:
        config: Dictionary of key-value pairs from the config file.

    Raises:
        ConfigError: If any required key is missing or its value is invalid.
        MazeSizeError: If maze dimensions are too small to generate a valid maze.
    """
    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUTFILE", "PERFECT"]

    for key in required_keys:
        if key not in config:
            raise ConfigError(f"Missing required config key: '{key}'")

    # Width / Height must be positive integers
    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
    except ValueError:
        raise ConfigError("WIDTH and HEIGHT must be integers.")

    if width <= 0 or height <= 0:
        raise ConfigError("WIDTH and HEIGHT must be positive integers.")

    # Minimum size check (need at least a 3x3 to do anything useful)
    # actually the subject doesnt say minimum but if its 1x1 nothing works
    if width < 3 or height < 3:
        raise MazeSizeError(
            f"Maze is too small ({width}x{height}). Minimum size is 3x3."
        )

    # Parse entry and exit coordinates
    entry = _parse_coords(config["ENTRY"], "ENTRY")
    exit_ = _parse_coords(config["EXIT"], "EXIT")

    # Make sure they are inside the maze
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError(
            f"ENTRY coordinates {entry} are out of maze bounds ({width}x{height})."
        )
    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        raise ConfigError(
            f"EXIT coordinates {exit_} are out of maze bounds ({width}x{height})."
        )

    # Entry and exit must be different
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells.")

    # PERFECT must be a boolean-like string
    perfect_val = config["PERFECT"].strip().lower()
    if perfect_val not in ("true", "false"):
        raise ConfigError("PERFECT must be 'True' or 'False'.")

    # OUTPUTFILE must not be empty
    if not config["OUTPUTFILE"].strip():
        raise ConfigError("OUTPUTFILE must not be empty.")


def _parse_coords(value: str, key_name: str) -> tuple[int, int]:
    """
    Parse a coordinate string like '0,0' into a tuple of two ints.

    Args:
        value: The raw string value (e.g. '5,3').
        key_name: The config key name, used in error messages.

    Returns:
        A tuple (x, y) of integers.

    Raises:
        ConfigError: If the format is wrong or values are not integers.
    """
    try:
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError
        x = int(parts[0].strip())
        y = int(parts[1].strip())
        return (x, y)
    except ValueError:
        raise ConfigError(
            f"Invalid coordinates for {key_name}: '{value}'. "
            f"Expected format: x,y (e.g. 0,0)."
        )


# ---- File helpers ----

def check_output_path(filepath: str) -> None:
    """
    Check that the output file path is writable.

    This doesnt create the file, just verifies that the parent directory
    exists and we have permission to write there.

    Args:
        filepath: The path to the output file.

    Raises:
        MazeFileError: If the directory does not exist or is not writable.
    """
    parent = os.path.dirname(os.path.abspath(filepath))
    if not os.path.isdir(parent):
        raise MazeFileError(
            f"Output directory does not exist: '{parent}'"
        )
    if not os.access(parent, os.W_OK):
        raise MazeFileError(
            f"No write permission for output directory: '{parent}'"
        )


def load_config_file(filepath: str) -> dict:
    """
    Read and parse a config file into a dictionary.

    Lines starting with '#' are treated as comments and ignored.
    Each other non-empty line must follow the KEY=VALUE format.

    Args:
        filepath: Path to the configuration file.

    Returns:
        A dictionary mapping config keys to their string values.

    Raises:
        MazeFileError: If the file cannot be opened or read.
        ConfigError: If a line has an invalid format.
    """
    if not os.path.isfile(filepath):
        raise MazeFileError(f"Config file not found: '{filepath}'")

    config: dict = {}

    try:
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()

                # skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ConfigError(
                        f"Line {line_num}: Invalid format '{line}'. "
                        f"Expected KEY=VALUE."
                    )

                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                if not key:
                    raise ConfigError(f"Line {line_num}: Empty key found.")

                config[key] = value

    except OSError as e:
        raise MazeFileError(f"Could not read config file: {e}")

    return config


# ---- Main entry point wrapper ----

def run_with_error_handling(main_func, *args, **kwargs) -> Optional[int]:  # type: ignore
    """
    Args:
        main_func: The callable to run.
        *args: Positional arguments to pass to main_func.
        **kwargs: Keyword arguments to pass to main_func.

    Returns:
        The return value of main_func, or None if an exception was raised.
    """
    try:
        return main_func(*args, **kwargs)
    except ConfigError as e:
        print_error(f"Configuration error: {e}")
        sys.exit(1)
    except MazeSizeError as e:
        print_error(f"Maze size error: {e}")
        sys.exit(1)
    except MazeFileError as e:
        print_error(f"File error: {e}")
        sys.exit(1)
    except MazeError as e:
        print_error(f"Maze error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        # user pressed ctrl+c, exit cleanly
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        # shouldnt happen but just in case
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
