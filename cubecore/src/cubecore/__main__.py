import sys

from .cube import Cube
from .render import net


def main() -> None:
    algorithm = " ".join(sys.argv[1:])
    print(net(Cube().apply(algorithm).stickers, color=sys.stdout.isatty()))


if __name__ == "__main__":
    main()
