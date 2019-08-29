from enum import Enum


class GameState(Enum):
    LOGO, \
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


# Timing
TICKS_PER_SEC = 20

# Colors
BLANK = (0, 0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)
LIGHT_GRAY = (208, 208, 208)
