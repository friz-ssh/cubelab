import random

import pytest
from cubecore.cross import FACE_MOVES, cross_state, distance_table
from cubecore.facelets import INDEX, NORMAL

from cubecore import Cube, solve_cross


def _cross_solved(cube: Cube) -> bool:
    """Independent check straight from the stickers (does not use cross_state)."""
    down = NORMAL["D"]
    for face in "FRBL":
        side = NORMAL[face]
        pos = (down[0] + side[0], down[1] + side[1], down[2] + side[2])
        if cube.stickers[INDEX[(pos, down)]] != "D":
            return False
        if cube.stickers[INDEX[(pos, side)]] != face:
            return False
    return True


def _scramble(rng: random.Random, length: int = 25) -> str:
    return " ".join(rng.choice(FACE_MOVES) for _ in range(length))


def test_table_has_every_cross_state() -> None:
    assert len(distance_table()) == 24 * 22 * 20 * 18


def test_cross_needs_at_most_8_moves() -> None:
    assert max(distance_table().values()) == 8


def test_solved_cube_needs_no_moves() -> None:
    assert solve_cross(Cube()) == []


@pytest.mark.parametrize(
    ("scramble", "expected"),
    [
        ("U", []),  # U does not touch the D layer
        ("R", ["R'"]),
        ("F", ["F'"]),
        ("D", ["D'"]),
        ("D2", ["D2"]),
    ],
)
def test_single_move_scrambles(scramble: str, expected: list[str]) -> None:
    assert solve_cross(Cube().apply(scramble)) == expected


def test_random_scrambles_are_solved_optimally() -> None:
    rng = random.Random(2)
    table = distance_table()
    for _ in range(300):
        cube = Cube().apply(_scramble(rng))
        solution = solve_cross(cube)
        assert len(solution) <= 8
        assert len(solution) == table[cross_state(cube.stickers)]
        assert _cross_solved(cube.apply(" ".join(solution)))


def test_average_solution_length() -> None:
    rng = random.Random(3)
    total = sum(len(solve_cross(Cube().apply(_scramble(rng)))) for _ in range(1000))
    assert 5.0 < total / 1000 < 6.5


def test_rejects_moved_centers() -> None:
    with pytest.raises(ValueError, match="centers"):
        solve_cross(Cube().apply("x"))
