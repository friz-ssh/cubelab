"""Optimal solver for the D-layer cross (single color).

The cross state is the slot of the white (D) sticker of each cross edge.
One sticker fixes both the position and the orientation of its edge, giving
24 * 22 * 20 * 18 = 190,080 states, small enough for a full BFS distance table.
"""

from functools import cache

from .cube import Cube
from .facelets import INDEX, NORMAL, SLOTS
from .moves import MOVES, Perm

CrossState = tuple[int, int, int, int]

FACE_MOVES: tuple[str, ...] = tuple(
    f"{base}{suffix}" for base in "URFDLB" for suffix in ("", "'", "2")
)

# Cross piece k is the DF, DR, DB, DL edge, identified by its non-D color.
_NEIGHBORS = ("F", "R", "B", "L")

_EDGE_SLOTS: tuple[int, ...] = tuple(
    i for i, (pos, _) in enumerate(SLOTS) if sum(1 for c in pos if c != 0) == 2
)


def _partner(slot: int) -> int:
    """The other sticker of the edge that owns `slot`."""
    pos, normal = SLOTS[slot]
    for axis in range(3):
        if pos[axis] != 0 and normal[axis] == 0:
            other = [0, 0, 0]
            other[axis] = pos[axis]
            return INDEX[(pos, (other[0], other[1], other[2]))]
    raise ValueError(f"Slot {slot} is not an edge sticker")


def _solved_state() -> CrossState:
    down = NORMAL["D"]
    slots: list[int] = []
    for face in _NEIGHBORS:
        side = NORMAL[face]
        pos = (down[0] + side[0], down[1] + side[1], down[2] + side[2])
        slots.append(INDEX[(pos, down)])
    return (slots[0], slots[1], slots[2], slots[3])


def cross_state(stickers: str) -> CrossState:
    """Compress a sticker string into its cross state."""
    for face, normal in NORMAL.items():
        if stickers[INDEX[(normal, normal)]] != face:
            raise ValueError("The cross solver needs the centers in their standard place")
    found: dict[str, int] = {}
    for slot in _EDGE_SLOTS:
        if stickers[slot] == "D":
            found[stickers[_partner(slot)]] = slot
    if len(found) != 4 or set(found) != set(_NEIGHBORS):
        raise ValueError("Could not find the four cross edges")
    return (found["F"], found["R"], found["B"], found["L"])


def _apply(state: CrossState, perm: Perm) -> CrossState:
    return (perm[state[0]], perm[state[1]], perm[state[2]], perm[state[3]])


@cache
def distance_table() -> dict[CrossState, int]:
    """BFS from the solved cross: distance (in face turns) of every cross state.

    The move set is closed under inversion, so the distance from the goal to a
    state equals the distance from that state to the goal.
    """
    perms = [MOVES[name] for name in FACE_MOVES]
    start = _solved_state()
    dist: dict[CrossState, int] = {start: 0}
    frontier: list[CrossState] = [start]
    depth = 0
    while frontier:
        depth += 1
        following: list[CrossState] = []
        for state in frontier:
            for perm in perms:
                nxt = _apply(state, perm)
                if nxt not in dist:
                    dist[nxt] = depth
                    following.append(nxt)
        frontier = following
    return dist


def solve_cross(cube: Cube) -> list[str]:
    """Return an optimal (fewest face turns) solution for the D cross."""
    dist = distance_table()
    state = cross_state(cube.stickers)
    if state not in dist:
        raise ValueError("Unreachable cross state")
    solution: list[str] = []
    while dist[state] > 0:
        for name in FACE_MOVES:
            nxt = _apply(state, MOVES[name])
            if dist[nxt] == dist[state] - 1:
                solution.append(name)
                state = nxt
                break
        else:
            raise RuntimeError("Distance table is inconsistent")
    return solution
