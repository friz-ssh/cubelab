"""The Cube state: an immutable string of 54 stickers."""

from dataclasses import dataclass

from .facelets import SOLVED
from .moves import MOVES, parse


@dataclass(frozen=True)
class Cube:
    """Immutable cube state. `stickers[i]` is the color currently at slot i."""

    stickers: str = SOLVED

    def __post_init__(self) -> None:
        if len(self.stickers) != 54:
            raise ValueError(f"Expected 54 stickers, got {len(self.stickers)}")

    def apply_move(self, token: str) -> "Cube":
        """Apply one normalized move token such as "R", "U'", "M2"."""
        perm = MOVES[token]
        result = [""] * 54
        for source, target in enumerate(perm):
            result[target] = self.stickers[source]
        return Cube("".join(result))

    def apply(self, algorithm: str) -> "Cube":
        """Apply a whole algorithm, e.g. "R U R' U'"."""
        cube = self
        for token in parse(algorithm):
            cube = cube.apply_move(token)
        return cube

    def is_solved(self) -> bool:
        return self.stickers == SOLVED
