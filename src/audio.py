from pygame.mixer import Sound

from src.constants import ASSET_DIR


class AudioManager:
    def __init__(self):
        bell_sound = Sound(ASSET_DIR + r"\bell.wav")
        strike_sound = Sound(ASSET_DIR + r"\strike.wav")
