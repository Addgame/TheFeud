import os
from tkinter import Tk
from typing import Callable

import pygame

os.environ["SDL_VIDEO_CENTERED"] = 'True'

SCORE_DISPLAY_SIZE = (135, 115)
RESPONSE_DISPLAY_SIZE = (320, 65)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class NumberDisplay(pygame.sprite.Sprite):
    """
    A display for a number on the screen
    """

    def __init__(self, name, loc, *groups):
        super().__init__(*groups)
        self.name = name
        self._value = 0
        self.rect = pygame.Rect(loc, SCORE_DISPLAY_SIZE)
        self.image = None
        self.update_image()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.update_image()

    def reset(self):
        self.value = 0

    def update_image(self):
        # TODO: Make sure text fits into size
        self.image = pygame.Surface(SCORE_DISPLAY_SIZE).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        text_surf = font.get(120).render(str(self.value), True, WHITE)
        self.image.blit(text_surf, (self.image.get_rect().size[0] / 2 - text_surf.get_rect().size[0] / 2, 0))


class ScoreboardResponse(pygame.sprite.Sprite):
    def __init__(self, response, loc, *groups):
        super().__init__(*groups)
        self.response = response
        self._revealed = False
        self.rect = pygame.Rect(loc, RESPONSE_DISPLAY_SIZE)
        self.hidden_image = pygame.Surface(RESPONSE_DISPLAY_SIZE).convert_alpha()
        self.hidden_image.fill((255, 255, 255, 0))
        self.hidden_image.blit(pygame.image.load(str(self.response.rank) + ".png"), (115, 0))
        self.response_image = pygame.Surface(RESPONSE_DISPLAY_SIZE).convert_alpha()
        self.response_image.fill((255, 255, 255, 0))
        self.response_image.blit(font.render(" " + response, True, BLACK), (0, 8))
        self.response_image.blit(font.render(str(self.response.count), True, BLACK), (RESPONSE_DISPLAY_SIZE[0] - 38, 8))
        self.image = None
        self.update_image()

    @property
    def revealed(self):
        return self._revealed

    @revealed.setter
    def revealed(self, set_val):
        self._revealed = set_val
        self.update_image()

    def update_image(self):
        if not self.revealed:
            self.image = self.hidden_image
        else:
            self.image = self.response_image
        # self.image = pygame.Surface(RESPONSE_DISPLAY_SIZE)
        # self.image.fill((0, 0, 255))

    @staticmethod
    def toggle_response(toggle_number):
        for response in responses:
            if response.response_number == toggle_number:
                if response.revealed:
                    main_score.value -= response.count
                else:
                    answer_sound.play()
                    main_score.value += response.count
                response.revealed = not response.revealed


# TODO: When moving to and from LOGO state do split in from sides transition
# (move into not logo state and do animation on top)
class State:
    """
    Acts as an enumerator holding values for the state of the program
    """
    LOGO, \
    FACE_OFF, \
    MAIN_GAME, \
    STEALING, \
    SHOWING_ANSWERS, \
    TIEBREAKER, \
    FAST_MONEY, \
    CREDITS, \
    QUITTING \
        = range(9)

    _state = LOGO

    @classmethod
    def set(cls, new_state):
        """
        Sets the state to the given state.

        :param new_state: the new state
        """
        # update the state
        old_state = cls._state
        cls._state = new_state
        # do state-specific transitions

    @classmethod
    def get(cls):
        """
        Gets the current state.

        :return: the current state
        """
        return cls._state


class State:
    """
    Represents the current state of the program
    """
    LOGO, \
    FACE_OFF, \
    MAIN_GAME, \
    STEALING, \
    SHOWING_ANSWERS, \
    TIEBREAKER, \
    FAST_MONEY, \
    CREDITS, \
    QUITTING \
        = range(9)

    def __init__(self):
        self.mode = State.LOGO
        self.num_strikes = 0
        self.main_survey = None
        self.main_team1_score = 0
        self.main_team2_score = 0
        self.main_
        self.fm_surveys = [None, None, None, None, None]


class Animation:
    """
    An animation that will occur over time.
    Has a callback and a counter to control how the animation happens.
    """

    _animations = []

    def __init__(self, callback: Callable[[int], bool]):
        """
        Sets up animation into default state and adds them to be tracked.
        The callback should take number of ticks the animation has been run and return boolean of if the animation is done.
        The counter runs first with counter equal to 0.

        :param callback: function to call every tick
        """
        self._call = callback
        self.counter = 0
        self._animations.append(self)

    def call(self):
        """
        Call the callback and removes animation if it is done.
        """
        if self._call(self.counter):
            self.remove()
        self.counter += 1

    def remove(self):
        """
        Remove the callback from the animations list
        """
        self._animations.remove(self)

    @classmethod
    def tick(cls):
        """
        Call all active animations.
        """
        for animation in cls._animations:
            animation.call()


def wrong_answer():
    global strikes

    def strikes_animation_1(counter):
        num_strikes = 1
        for i in range(num_strikes):
            screen.blit(strike_image, strike_locs[num_strikes][i])
        if counter < 2 * clock.get_fps():
            return False
        return True

    def strikes_animation_2(counter):
        num_strikes = 2
        for i in range(num_strikes):
            screen.blit(strike_image, strike_locs[num_strikes][i])
        if counter < 2 * clock.get_fps():
            return False
        return True

    def strikes_animation_3(counter):
        num_strikes = 3
        for i in range(num_strikes):
            screen.blit(strike_image, strike_locs[num_strikes][i])
        if counter < 2 * clock.get_fps():
            return False
        return True

    strikes += 1

    if strikes == 1:
        Animation(strikes_animation_1)
    elif strikes == 2:
        Animation(strikes_animation_2)
    else:
        Animation(strikes_animation_3)

    if state in (State.FACE_OFF, State.STEALING, State.TIEBREAKER) or strikes >= 3:
        strikes = 0
    strike_sound.play()


# TODO: Add credits screen
def draw_screen():
    if state is State.LOGO:
        screen.blit(logo_screen, (0, 0))
    elif state in (State.FACE_OFF, State.MAIN_GAME, State.STEALING, State.TIEBREAKER):
        pass  # Draw the normal screen for the game
    elif state is State.FAST_MONEY:
        pass  # Draw the fast money screen
    elif state is State.CREDITS:
        screen.blit(credits_screen, (0, 0))


def handle_events():
    global state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state = State.QUITTING


def loop():
    handle_events()
    draw_screen()
    Animation.tick()
    pygame.display.flip()
    clock.tick()
    if state is not State.QUITTING:
        root.after(0, loop)


def setup_strike_locs():
    global strike_locs
    strike_y = screen.height / 2 - strike_image.height / 2
    strike_locs = [[[0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]]]
    for num_strikes in range(3):
        for i in range(num_strikes + 1):
            strike_locs[num_strikes][i][0] = int(screen.width / 2 - (
                    strike_image.width * (num_strikes + 1) / 2 + strike_spacing * num_strikes / 2 - i * (
                    strike_image.width + strike_spacing)))
            strike_locs[num_strikes][i][1] = strike_y


if __name__ == '__main__':
    # Set up pygame
    pygame.init()
    clock = pygame.time.Clock()
    monitor_info = pygame.display.Info()
    pygame.display.set_caption("The Feud")
    screen = pygame.display.set_mode((monitor_info.current_w, monitor_info.current_h),
                                     pygame.RESIZABLE | pygame.NOFRAME)  # , pygame.FULLSCREEN)

    # Load resources
    asset_dir = "assets/"
    image_dir = asset_dir + "images/"
    sound_dir = asset_dir + "sounds/"

    font = FontHelper(os.path.abspath(asset_dir + "MuktaMahee-Regular.ttf"))

    main_scoreboard = pygame.image.load(image_dir + "main_board.png")
    fast_money_scoreboard = pygame.image.load(image_dir + "fast_money_board.png")
    logo_screen = pygame.image.load(image_dir + "logo_screen.png")
    logo_screen_left = pygame.image.load(image_dir + "logo_screen_left.png")
    logo_screen_right = pygame.image.load(image_dir + "logo_screen_right.png")
    strike_image = pygame.image.load(image_dir + "strike.png")
    credits_screen = pygame.image.load("")

    answer_sound = pygame.mixer.Sound(sound_dir + "bell.wav")
    strike_sound = pygame.mixer.Sound(sound_dir + "strike.wav")
    try_again_sound = pygame.mixer.Sound(sound_dir + "try_again.wav")

    # Set up game variables
    strikes = 0
    responses = pygame.sprite.Group()
    # TODO: Attach up responses group to be drawn / reorganize this section
    displays = pygame.sprite.Group()
    # TODO: Make all these locations relative
    main_score = NumberDisplay("Main Display Score", (440, 22), displays)
    left_score = NumberDisplay("Left Team Score", (2, 328), displays)
    right_score = NumberDisplay("Right Team Score", (885, 335), displays)

    # Set up strike locations
    strike_spacing = 0
    strike_locs = []
    setup_strike_locs()

    # Set up tkinter and start looping
    master = Tk()
    ControlApp(master)
    master.after(0, loop)
    master.mainloop()

    # Once tkinter stops close pygame
    pygame.quit()
