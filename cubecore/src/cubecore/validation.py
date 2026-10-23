"""Validation: is a 54-sticker string a reachable Rubik's cube state?"""

from collections import Counter

from .facelets import FACES, INDEX, NORMAL, SLOTS, Vec


class InvalidCubeError(ValueError):
    """Raised when a sticker string cannot be a legal cube."""


_FACE_OF_NORMAL: dict[Vec, str] = {normal: face for face, normal in NORMAL.items()}


def _dot(a: Vec, b: Vec) -> int:
    return sum(x * y for x, y in zip(a, b, strict=True))


def _cross(a: Vec, b: Vec) -> Vec:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _unit(axis: int, sign: int) -> Vec:
    v = [0, 0, 0]
    v[axis] = sign
    return (v[0], v[1], v[2])


def _positions(nonzero: int) -> list[Vec]:
    return sorted({pos for pos, _ in SLOTS if sum(1 for c in pos if c != 0) == nonzero})


def _corner_normals(pos: Vec) -> tuple[Vec, Vec, Vec]:
    """Normals of a corner in a fixed right-handed order, U/D first."""
    a, b, c = _unit(1, pos[1]), _unit(0, pos[0]), _unit(2, pos[2])
    if _dot(a, _cross(b, c)) < 0:
        b, c = c, b
    return (a, b, c)


def _edge_normals(pos: Vec) -> tuple[Vec, Vec]:
    """Normals of an edge, ordered by priority U/D, then F/B, then R/L."""
    axes = [axis for axis in (1, 2, 0) if pos[axis] != 0]
    return (_unit(axes[0], pos[axes[0]]), _unit(axes[1], pos[axes[1]]))


_CORNERS = _positions(3)
_EDGES = _positions(2)

# Home colors of each piece (as face letters), read in the fixed order above.
_CORNER_HOME: dict[Vec, tuple[str, ...]] = {
    pos: tuple(_FACE_OF_NORMAL[n] for n in _corner_normals(pos)) for pos in _CORNERS
}
_EDGE_HOME: dict[Vec, tuple[str, ...]] = {
    pos: tuple(_FACE_OF_NORMAL[n] for n in _edge_normals(pos)) for pos in _EDGES
}
_CORNER_BY_SET = {frozenset(t): pos for pos, t in _CORNER_HOME.items()}
_EDGE_BY_SET = {frozenset(t): pos for pos, t in _EDGE_HOME.items()}


def _parity(perm: list[int]) -> int:
    seen = [False] * len(perm)
    cycles = 0
    for start in range(len(perm)):
        if not seen[start]:
            cycles += 1
            i = start
            while not seen[i]:
                seen[i] = True
                i = perm[i]
    return (len(perm) - cycles) % 2


def validate(stickers: str) -> None:
    """Raise InvalidCubeError if `stickers` is not a reachable cube state."""
    if len(stickers) != 54:
        raise InvalidCubeError(f"Expected 54 stickers, got {len(stickers)}")
    unknown = set(stickers) - set(FACES)
    if unknown:
        raise InvalidCubeError(f"Unknown color(s): {sorted(unknown)}")
    counts = Counter(stickers)
    for face in FACES:
        if counts[face] != 9:
            raise InvalidCubeError(f"Each color must appear 9 times: {face} appears {counts[face]}")

    # Name every color after the face whose center it sits on.
    face_of_color = {stickers[INDEX[(n, n)]]: face for face, n in NORMAL.items()}
    if len(face_of_color) != 6:
        raise InvalidCubeError("Centers must all be different colors")
    s = [face_of_color[ch] for ch in stickers]

    # Corners
    corner_perm: list[int] = []
    twist = 0
    for pos in _CORNERS:
        t = tuple(s[INDEX[(pos, n)]] for n in _corner_normals(pos))
        home = _CORNER_BY_SET.get(frozenset(t))
        if home is None:
            raise InvalidCubeError(f"Impossible corner at {pos}: {t}")
        ref = _CORNER_HOME[home]
        if not any(t == ref[k:] + ref[:k] for k in range(3)):
            raise InvalidCubeError(f"Mirrored corner at {pos}: {t}")
        twist += t.index(ref[0])
        corner_perm.append(_CORNERS.index(home))
    if sorted(corner_perm) != list(range(8)):
        raise InvalidCubeError("Duplicate corner")

    # Edges
    edge_perm: list[int] = []
    flip = 0
    for pos in _EDGES:
        t = tuple(s[INDEX[(pos, n)]] for n in _edge_normals(pos))
        home = _EDGE_BY_SET.get(frozenset(t))
        if home is None:
            raise InvalidCubeError(f"Impossible edge at {pos}: {t}")
        flip += 0 if t == _EDGE_HOME[home] else 1
        edge_perm.append(_EDGES.index(home))
    if sorted(edge_perm) != list(range(12)):
        raise InvalidCubeError("Duplicate edge")

    if twist % 3 != 0:
        raise InvalidCubeError("Corner twist error: one corner is twisted")
    if flip % 2 != 0:
        raise InvalidCubeError("Edge flip error: one edge is flipped")
    if _parity(corner_perm) != _parity(edge_perm):
        raise InvalidCubeError("Permutation parity error: two pieces are swapped")
