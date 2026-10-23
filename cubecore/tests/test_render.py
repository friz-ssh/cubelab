from cubecore import SOLVED, Cube, net


def test_solved_net() -> None:
    expected = "\n".join(["    UUU"] * 3 + ["LLL FFF RRR BBB"] * 3 + ["    DDD"] * 3)
    assert net(SOLVED) == expected


def test_net_after_R() -> None:
    expected = "\n".join(["    UUF"] * 3 + ["LLL FFD RRR UBB"] * 3 + ["    DDB"] * 3)
    assert net(Cube().apply("R").stickers) == expected


def test_color_net_has_ansi_codes() -> None:
    assert "\x1b[48;5;" in net(SOLVED, color=True)
