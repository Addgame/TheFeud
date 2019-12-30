from enum import Enum

from pygame import Color


class GameState(Enum):
    PREPARING, \
    FACE_OFF, \
    MAIN_GAME, \
    STEALING, \
    REVEALING, \
    TIEBREAKER, \
    FAST_MONEY, \
    CREDITS, \
        = range(8)

    def __str__(self):
        return self.name.replace("_", " ").title()


# Assets
ASSET_DIR = r"assets\\"

# Timing
TICKS_PER_SEC = 20

# Colors
WHITE = Color("white")
TEXT_COLOR = Color(192, 192, 192)
MAGENTA = Color("magenta")
