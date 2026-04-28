"""Config file parser for a_maze_ing."""

from __future__ import annotations

from dataclasses import dataclass


REQUIRED = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


class ConfigError(Exception):
    pass


def _to_int(name: str, raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got {raw!r}")


def _to_coord(name: str, raw: str) -> tuple[int, int]:
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 2:
        raise ConfigError(f"{name} must be 'x,y', got {raw!r}")
    return _to_int(f"{name}.x", parts[0]), _to_int(f"{name}.y", parts[1])


def _to_bool(name: str, raw: str) -> bool:
    s = raw.strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    raise ConfigError(f"{name} must be True or False, got {raw!r}")


def load(path: str) -> Config:
    """Read and validate a config file. Raises ConfigError on any problem."""
    try:
        with open(path) as f:
            text = f.read()
    except OSError as e:
        raise ConfigError(f"cannot open config file {path!r}: {e}")

    raw: dict[str, str] = {}
    for n, line in enumerate(text.splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ConfigError(f"line {n}: expected KEY=VALUE, got {line!r}")
        key, _, value = line.partition("=")
        key = key.strip().upper()
        if not key:
            raise ConfigError(f"line {n}: empty key")
        raw[key] = value.strip()

    for k in REQUIRED:
        if k not in raw:
            raise ConfigError(f"missing required key: {k}")

    width = _to_int("WIDTH", raw["WIDTH"])
    height = _to_int("HEIGHT", raw["HEIGHT"])
    if width < 2 or height < 2:
        raise ConfigError(
            f"WIDTH and HEIGHT must be >= 2 (got {width}x{height})"
        )

    entry = _to_coord("ENTRY", raw["ENTRY"])
    exit_ = _to_coord("EXIT", raw["EXIT"])
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError(f"ENTRY {entry} outside {width}x{height}")
    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        raise ConfigError(f"EXIT {exit_} outside {width}x{height}")
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must differ")

    output_file = raw["OUTPUT_FILE"]
    if not output_file:
        raise ConfigError("OUTPUT_FILE must not be empty")

    perfect = _to_bool("PERFECT", raw["PERFECT"])
    seed = _to_int("SEED", raw["SEED"]) if "SEED" in raw else None

    return Config(width, height, entry, exit_, output_file, perfect, seed)
