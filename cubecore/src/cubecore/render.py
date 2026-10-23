"""Render a 54-sticker string as a cross-shaped net for the terminal."""

# ANSI 256-color codes for the standard color scheme.
_ANSI = {"U": 15, "R": 196, "F": 34, "D": 226, "L": 208, "B": 21}


def _cell(face: str, color: bool) -> str:
    if color:
        return f"\x1b[48;5;{_ANSI[face]}m  \x1b[0m"
    return face


def net(stickers: str, color: bool = False) -> str:
    """Return the net of the cube.

      U
    L F R B
      D
    """
    if len(stickers) != 54:
        raise ValueError(f"Expected 54 stickers, got {len(stickers)}")

    cell_width = 2 if color else 1
    pad = " " * (3 * cell_width + 1)

    def face_row(face_index: int, row: int) -> str:
        start = face_index * 9 + row * 3
        return "".join(_cell(ch, color) for ch in stickers[start : start + 3])

    # Face order in the string: U R F D L B -> indices 0 1 2 3 4 5.
    lines: list[str] = []
    lines += [pad + face_row(0, r) for r in range(3)]
    lines += [
        " ".join(face_row(i, r) for i in (4, 2, 1, 5))  # L F R B
        for r in range(3)
    ]
    lines += [pad + face_row(3, r) for r in range(3)]
    return "\n".join(lines)
