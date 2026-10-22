"""Move tables generated from 3D geometry, plus a notation parser."""

import re
from dataclasses import dataclass

from .facelets import INDEX, SLOTS, Vec

Perm = tuple[int, ...]

# For each axis, the two other axes in cyclic order.
_CYCLE: dict[int, tuple[int, int]] = {0: (1, 2), 1: (2, 0), 2: (0, 1)}


def rotate90(v: Vec, axis: int, quarter_turns: int) -> Vec:
    """Rotate `v` by `quarter_turns` * 90 degrees (right-hand rule) around `axis`."""
    b, c = _CYCLE[axis]
    x = list(v)
    for _ in range(quarter_turns % 4):
        x[b], x[c] = -x[c], x[b]
    return (x[0], x[1], x[2])


@dataclass(frozen=True)
class BaseMove:
    axis: int  # 0 = x, 1 = y, 2 = z
    layers: frozenset[int]  # which layers along `axis` move (-1, 0, 1)
    turns: int  # quarter turns (right-hand rule) for the plain move


_ALL = frozenset({-1, 0, 1})


def _layers(*values: int) -> frozenset[int]:
    return frozenset(values)


BASE_MOVES: dict[str, BaseMove] = {
    # Faces (clockwise as seen from outside that face)
    "R": BaseMove(0, _layers(1), -1),
    "L": BaseMove(0, _layers(-1), 1),
    "U": BaseMove(1, _layers(1), -1),
    "D": BaseMove(1, _layers(-1), 1),
    "F": BaseMove(2, _layers(1), -1),
    "B": BaseMove(2, _layers(-1), 1),
    # Slices (M follows L, E follows D, S follows F)
    "M": BaseMove(0, _layers(0), 1),
    "E": BaseMove(1, _layers(0), 1),
    "S": BaseMove(2, _layers(0), -1),
    # Whole-cube rotations (x follows R, y follows U, z follows F)
    "x": BaseMove(0, _ALL, -1),
    "y": BaseMove(1, _ALL, -1),
    "z": BaseMove(2, _ALL, -1),
    # Wide moves (face + adjacent slice), written r, l, u, d, f, b
    "r": BaseMove(0, _layers(0, 1), -1),
    "l": BaseMove(0, _layers(-1, 0), 1),
    "u": BaseMove(1, _layers(0, 1), -1),
    "d": BaseMove(1, _layers(-1, 0), 1),
    "f": BaseMove(2, _layers(0, 1), -1),
    "b": BaseMove(2, _layers(-1, 0), 1),
}

# "Rw" is an alias of "r", and so on.
WIDE_ALIASES: dict[str, str] = {
    "Rw": "r",
    "Lw": "l",
    "Uw": "u",
    "Dw": "d",
    "Fw": "f",
    "Bw": "b",
}


def build_permutation(move: BaseMove, power: int) -> Perm:
    """perm[i] = the slot that the sticker currently at slot i moves to."""
    turns = move.turns * power
    perm: list[int] = []
    for index, (pos, normal) in enumerate(SLOTS):
        if pos[move.axis] in move.layers:
            target = (rotate90(pos, move.axis, turns), rotate90(normal, move.axis, turns))
            perm.append(INDEX[target])
        else:
            perm.append(index)
    return tuple(perm)


def _build_table() -> dict[str, Perm]:
    table: dict[str, Perm] = {}
    for name, base in BASE_MOVES.items():
        table[name] = build_permutation(base, 1)
        table[name + "'"] = build_permutation(base, -1)
        table[name + "2"] = build_permutation(base, 2)
    return table


# MOVES["R"], MOVES["R'"], MOVES["R2"], MOVES["M"], MOVES["x'"], ...
MOVES: dict[str, Perm] = _build_table()

_TOKEN = re.compile(r"^(?P<base>[URFDLBMESxyzurfdlb]|[URFDLB]w)(?P<suffix>2'|2|')?$")


def parse(algorithm: str) -> list[str]:
    """Split an algorithm into normalized tokens, e.g. "Rw2' U" -> ["r2", "U"]."""
    tokens: list[str] = []
    for raw in algorithm.split():
        match = _TOKEN.match(raw)
        if match is None:
            raise ValueError(f"Invalid move: {raw!r}")
        base = WIDE_ALIASES.get(match.group("base"), match.group("base"))
        suffix = match.group("suffix") or ""
        if suffix == "2'":
            suffix = "2"
        tokens.append(base + suffix)
    return tokens


def invert(algorithm: str) -> str:
    """Return the inverse algorithm: reversed order, each move inverted."""
    result: list[str] = []
    for token in reversed(parse(algorithm)):
        if token.endswith("2"):
            result.append(token)
        elif token.endswith("'"):
            result.append(token[:-1])
        else:
            result.append(token + "'")
    return " ".join(result)
