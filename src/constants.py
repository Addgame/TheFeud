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
BLANK = Color(0, 0, 0, 0)
BLACK = Color("black")
WHITE = Color("white")
SILVER = Color(192, 192, 192)
LIGHT_GRAY = Color(208, 208, 208)
MAGENTA = Color("magenta")
