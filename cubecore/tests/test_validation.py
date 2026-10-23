import random

import pytest
from cubecore.moves import MOVES

from cubecore import SOLVED, Cube, InvalidCubeError, validate

FACE_MOVES = [f"{b}{s}" for b in "URFDLB" for s in ("", "'", "2")]


def _swap(stickers: str, i: int, j: int) -> str:
    s = list(stickers)
    s[i], s[j] = s[j], s[i]
    return "".join(s)


def test_solved_is_valid() -> None:
    validate(SOLVED)


def test_random_face_scrambles_are_valid() -> None:
    rng = random.Random(0)
    for _ in range(200):
        alg = " ".join(rng.choice(FACE_MOVES) for _ in range(30))
        validate(Cube().apply(alg).stickers)


def test_random_scrambles_with_slices_and_rotations_are_valid() -> None:
    rng = random.Random(1)
    names = sorted(MOVES)
    for _ in range(200):
        alg = " ".join(rng.choice(names) for _ in range(30))
        validate(Cube().apply(alg).stickers)


def test_wrong_length() -> None:
    with pytest.raises(InvalidCubeError, match="54"):
        validate(SOLVED[:-1])


def test_unknown_color() -> None:
    with pytest.raises(InvalidCubeError, match="Unknown"):
        validate("X" + SOLVED[1:])


def test_wrong_color_count() -> None:
    with pytest.raises(InvalidCubeError, match="9 times"):
        validate("R" + SOLVED[1:])


def test_twisted_corner() -> None:
    # Rotate the three stickers of the URF corner (slots 8, 9, 20).
    s = list(SOLVED)
    s[8], s[9], s[20] = s[9], s[20], s[8]
    with pytest.raises(InvalidCubeError, match="twist"):
        validate("".join(s))


def test_flipped_edge() -> None:
    # Flip the UF edge (slots 7 and 19).
    with pytest.raises(InvalidCubeError, match="flip"):
        validate(_swap(SOLVED, 7, 19))


def test_mirrored_corner() -> None:
    with pytest.raises(InvalidCubeError, match="Mirrored"):
        validate(_swap(SOLVED, 9, 20))


def test_swapped_edges_parity() -> None:
    # Swap the UF and UR edges in place.
    s = _swap(_swap(SOLVED, 7, 5), 19, 10)
    with pytest.raises(InvalidCubeError, match="parity"):
        validate(s)


def test_from_string() -> None:
    scrambled = Cube().apply("R U F' D2").stickers
    assert Cube.from_string(scrambled).stickers == scrambled
    with pytest.raises(InvalidCubeError):
        Cube.from_string(_swap(SOLVED, 7, 19))
