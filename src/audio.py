from pygame.mixer import Sound

from src.constants import ASSET_DIR


class AudioManager:
    """
    Handles the sound effects for the game
    """

    def __init__(self):
        self.correct_sound = Sound(ASSET_DIR + r"\sounds\correct.wav")
        self.short_wrong_sound = Sound(ASSET_DIR + r"\sounds\short_wrong.wav")
        self.long_wrong_sound = Sound(ASSET_DIR + r"\sounds\long_wrong.wav")
        self.try_again_sound = Sound(ASSET_DIR + r"\sounds\try_again.wav")
        self.reveal_sound = Sound(ASSET_DIR + r"\sounds\reveal.wav")

    def play_strike(self):
        self.long_wrong_sound.play()

    def play_correct(self):
        self.correct_sound.play()

    def play_fm_reveal(self):
        self.reveal_sound.play()

    def play_fm_wrong(self):
        self.short_wrong_sound.play()

    def play_try_again(self):
        self.try_again_sound.play()

    def play_timer_end(self):
        self.long_wrong_sound.play()
