"""Facelet indexing: maps each of the 54 stickers to a 3D position and a normal."""

Vec = tuple[int, int, int]

# Face order used everywhere in the project (Kociemba convention).
FACES = "URFDLB"

# Outward normal of each face. x: L(-1)/R(+1), y: D(-1)/U(+1), z: B(-1)/F(+1).
NORMAL: dict[str, Vec] = {
    "U": (0, 1, 0),
    "R": (1, 0, 0),
    "F": (0, 0, 1),
    "D": (0, -1, 0),
    "L": (-1, 0, 0),
    "B": (0, 0, -1),
}


def _position(face: str, row: int, col: int) -> Vec:
    """3D position of the cubie that owns sticker (row, col) on `face`.

    Rows/columns follow the standard net: each face is read as if you were
    looking straight at it, U with B at the top, D with F at the top.
    """
    match face:
        case "U":
            return (col - 1, 1, row - 1)
        case "R":
            return (1, 1 - row, 1 - col)
        case "F":
            return (col - 1, 1 - row, 1)
        case "D":
            return (col - 1, -1, 1 - row)
        case "L":
            return (-1, 1 - row, col - 1)
        case "B":
            return (1 - col, 1 - row, -1)
        case _:
            raise ValueError(f"Unknown face: {face!r}")


# SLOTS[i] = (position, normal) of facelet slot i.
SLOTS: tuple[tuple[Vec, Vec], ...] = tuple(
    (_position(face, row, col), NORMAL[face])
    for face in FACES
    for row in range(3)
    for col in range(3)
)

# Reverse lookup: (position, normal) -> slot index.
INDEX: dict[tuple[Vec, Vec], int] = {slot: i for i, slot in enumerate(SLOTS)}

SOLVED = "".join(face * 9 for face in FACES)
