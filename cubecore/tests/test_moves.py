import pytest
from cubecore.moves import BASE_MOVES, MOVES

from cubecore import SOLVED, Cube, invert, parse

# A fixed, non-trivial state so tests cannot pass just because the cube is solved.
SCRAMBLE = "R U F' D2 L B' M x' r2 E S2 U' R2 f"
SCRAMBLED = Cube().apply(SCRAMBLE)


def test_solved_string() -> None:
    assert SOLVED == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    assert Cube().is_solved()


def test_scramble_is_not_solved() -> None:
    assert not SCRAMBLED.is_solved()


@pytest.mark.parametrize("name", sorted(MOVES))
def test_every_move_is_a_valid_permutation(name: str) -> None:
    assert sorted(MOVES[name]) == list(range(54))


@pytest.mark.parametrize("name", sorted(BASE_MOVES))
def test_four_quarter_turns_is_identity(name: str) -> None:
    assert SCRAMBLED.apply(" ".join([name] * 4)) == SCRAMBLED


@pytest.mark.parametrize("name", sorted(BASE_MOVES))
def test_move_then_inverse_is_identity(name: str) -> None:
    assert SCRAMBLED.apply(f"{name} {name}'") == SCRAMBLED


@pytest.mark.parametrize("name", sorted(BASE_MOVES))
def test_double_move_equals_two_quarter_turns(name: str) -> None:
    assert SCRAMBLED.apply(f"{name}2") == SCRAMBLED.apply(f"{name} {name}")


def test_algorithm_then_its_inverse_is_identity() -> None:
    assert SCRAMBLED.apply(SCRAMBLE).apply(invert(SCRAMBLE)) == SCRAMBLED


# --- Equivalences: these verify directions of different moves against each other ---


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("M", "R L' x'"),
        ("E", "U D' y'"),
        ("S", "F' B z"),
        ("r", "R M'"),
        ("l", "L M"),
        ("u", "U E'"),
        ("d", "D E"),
        ("f", "F S"),
        ("b", "B S'"),
        ("x", "R M' L'"),
        ("y", "U E' D'"),
        ("z", "F S B'"),
        ("Rw", "r"),
    ],
)
def test_equivalences(left: str, right: str) -> None:
    assert SCRAMBLED.apply(left) == SCRAMBLED.apply(right)


# --- Golden values and known group facts ---


def test_golden_R_move() -> None:
    expected = "UUFUUFUUFRRRRRRRRRFFDFFDFFDDDBDDBDDBLLLLLLLLLUBBUBBUBB"
    assert Cube().apply("R").stickers == expected


def test_x_rotation_moves_front_to_up() -> None:
    assert Cube().apply("x").stickers[4] == "F"  # U center now shows F's color


def test_sexy_move_has_order_6() -> None:
    sexy = "R U R' U'"
    assert SCRAMBLED.apply(" ".join([sexy] * 6)) == SCRAMBLED
    for n in (1, 2, 3):
        assert Cube().apply(" ".join([sexy] * n)) != Cube()


def test_RU_has_order_105() -> None:
    assert Cube().apply(" ".join(["R U"] * 105)).is_solved()
    for n in (1, 3, 5, 7, 15, 21, 35):
        assert not Cube().apply(" ".join(["R U"] * n)).is_solved()


def test_color_counts_preserved() -> None:
    for face in "URFDLB":
        assert SCRAMBLED.stickers.count(face) == 9


def test_parse_normalizes_notation() -> None:
    assert parse("Rw2' U  F'") == ["r2", "U", "F'"]


def test_parse_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        parse("R U Q")
