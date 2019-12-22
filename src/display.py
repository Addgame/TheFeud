import os
from abc import ABC, abstractmethod
from threading import Lock

import pygame
from pygame.math import Vector2

from src.constants import GameState, TICKS_PER_SEC, SILVER, WHITE, MAGENTA, ASSET_DIR


class TextLabel(pygame.sprite.Sprite):
    """
    Text that appears on the screen
    """

    def __init__(self, font_helper):
        super().__init__()
        self._text = ""
        self.rect = None
        self.image = None
        self.font_helper = font_helper

    def set_display(self, rect):
        self.rect = rect
        self.image = pygame.Surface(rect.size).convert()
        self.image.set_colorkey(MAGENTA)
        self.render()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self.render()

    def render(self):
        with GraphicsManager.instance.lock:
            self.image.fill(MAGENTA)
            font = self.font_helper.fits_default(self._text, 90, self.rect)
            text_image = font.render(self._text, False, SILVER)
            text_rect = text_image.get_rect()
            text_rect.x = self.rect.width / 2 - text_rect.centerx
            text_rect.y = self.rect.height / 2 - text_rect.centery
            self.image.blit(text_image, text_rect)


class IDLabel(TextLabel):
    """
    Renders the text image in the bottom right corner of given rect
    """

    def render(self):
        self.image.fill(MAGENTA)
        font = self.font_helper.fits_default(self._text, 72, self.rect)
        text_image = font.render(self._text, False, SILVER)
        text_rect = text_image.get_rect()
        text_rect.x = self.rect.width - text_rect.width
        text_rect.y = self.rect.height - text_rect.height
        self.image.blit(text_image, text_rect)


class AnimatedSprite(pygame.sprite.Sprite, ABC):
    """
    An animated sprite
    """

    def __init__(self):
        super().__init__()
        self.animation_counter = 0
        self.current_animation = None

    def is_anim_active(self):
        return self.current_animation is not None

    def start_animation(self, anim_id=0):
        self.animation_counter = 0
        self.current_animation = anim_id

    def update(self):
        if self.is_anim_active():
            self.animation_counter += 1
            self.tick()

    @abstractmethod
    def tick(self):
        pass

    def end_animation(self):
        self.animation_counter = 0
        self.current_animation = None


class LogoSplit(AnimatedSprite):
    """
    The logo splitting animation sprite
    """
    _ANIM_OPENING, _ANIM_CLOSING = range(2)

    def __init__(self):
        super().__init__()
        self.closed = True
        self.left_image = None
        self.right_image = None
        self.full_image = None
        self.background_image = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.left_x = 0
        self.right_x = 0
        self.dx = 0
        self.image = None
        self.blank_image = None

    def set_display(self, size, left_image, right_image):
        self.rect.size = size
        self.left_image = left_image
        self.right_image = right_image
        self.full_image = pygame.Surface(size)
        self.full_image.blit(left_image, (0, 0))
        self.full_image.blit(right_image, (size[0] / 2, 0))
        self.dx = left_image.get_width() / (2 * TICKS_PER_SEC)
        self.left_x = 0
        self.right_x = size[0] / 2
        self.image = pygame.Surface(size)
        self.image.set_colorkey(MAGENTA)
        self.render()

    def open(self):
        self.left_x = 0
        self.right_x = self.left_image.get_width()
        self.closed = False
        self.start_animation(self._ANIM_OPENING)

    def close(self):
        self.left_x = -self.left_image.get_width()
        self.right_x = self.rect.width
        self.closed = True
        self.background_image = GraphicsManager.instance.screen.copy()
        self.start_animation(self._ANIM_CLOSING)

    def stop_split(self):
        self.end_animation()

    def render(self):
        """
        Creates the image
        """
        if not self.is_anim_active():
            if self.closed:
                self.image.blit(self.full_image, (0, 0))
            else:
                self.image.fill(MAGENTA)
        else:
            if self.current_animation == self._ANIM_CLOSING:
                self.image.blit(self.background_image, (0, 0))
                self.left_x += self.dx
                self.right_x -= self.dx
            else:
                self.image.fill(MAGENTA)
                self.left_x -= self.dx
                self.right_x += self.dx
            self.image.blit(self.left_image, (self.left_x, 0))
            self.image.blit(self.right_image, (self.right_x, 0))

    def tick(self):
        if self.animation_counter >= (2 * TICKS_PER_SEC) + 1:
            self.stop_split()
        self.render()


class ResponseCard(AnimatedSprite, ABC):
    """
    A graphical response card
    """

    def __init__(self):
        super().__init__()
        self._response = None
        self.rect = None
        self.image = None

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value
        self.update_images()

    @abstractmethod
    def update_images(self):
        """
        Creates the response image
        """
        pass

    @abstractmethod
    def render(self):
        """
        Recreates the graphical representations of the response (sets self.image) based on state
        """
        pass


class MainResponseCard(ResponseCard):
    """
    The response card style for the main game
    """

    def __init__(self, font_helper):
        super().__init__()
        self._visible = False
        self.hidden_image = None
        self.revealed_image = None
        self.revealed_bg_image = None
        self.text_rect = None
        self.num_rect = None
        self.font_helper = font_helper

    def set_display(self, full_rect, text_rect, num_rect, hidden_image, revealed_bg_image):
        self.rect = full_rect
        self.text_rect = text_rect
        self.num_rect = num_rect
        self.image = pygame.Surface(full_rect.size).convert()
        self.image.set_colorkey(MAGENTA)
        self.hidden_image = hidden_image
        self.revealed_bg_image = revealed_bg_image
        self.update_images()

    def reveal(self):
        self._visible = True
        self.start_animation(0)

    def hide(self):
        self._visible = False
        self.render()

    def tick(self):
        if self.animation_counter >= 1 * TICKS_PER_SEC:
            self.end_animation()
        self.render()

    def update_images(self):
        with GraphicsManager.instance.lock:
            self.image.fill(MAGENTA)
            if not self.response:
                return
            self.revealed_image = self.revealed_bg_image.copy()
            font = self.font_helper.fits_default(self.response.phrase, 72, self.text_rect)
            text_image = font.render(self.response.phrase, False, SILVER)
            rendered_rect = text_image.get_rect()
            rendered_rect.x = self.text_rect.centerx - rendered_rect.centerx
            rendered_rect.y = self.text_rect.centery - rendered_rect.centery
            self.revealed_image.blit(text_image, rendered_rect)
            font = self.font_helper.fits_default(str(self.response.count), 72, self.num_rect)
            num_image = font.render(str(self.response.count), False, SILVER)
            rendered_rect = num_image.get_rect()
            rendered_rect.x = self.num_rect.centerx - rendered_rect.centerx
            rendered_rect.y = self.num_rect.centery - rendered_rect.centery
            self.revealed_image.blit(num_image, rendered_rect)
        self.render()

    def render(self):
        if not self._visible:
            self.image.blit(self.hidden_image, (0, 0))
        elif not self.is_anim_active():
            self.image.blit(self.revealed_image, (0, 0))
        elif self.response:
            self.image = pygame.Surface(self.rect.size)
            self.image.blit(self.revealed_image, (0, 0))
            hidden_y = int(self.rect.height * (self.animation_counter / (.2 * TICKS_PER_SEC)))
            self.image.blit(self.hidden_image, (0, hidden_y))


class FastMoneyResponseCard(ResponseCard):
    """
    The response card style for fast money
    """

    UNREVEALED, PHRASE_REVEALED, COUNT_REVEALED = range(3)

    def __init__(self, font_helper):
        super().__init__()
        self.reveal_stage = self.UNREVEALED
        self._given_response = ""
        self.text_rect = None
        self.num_rect = None
        self.red_block_image = None
        self.red_block_width = 0
        self.revealed_image = None
        self.font_helper = font_helper

    def set_display(self, full_rect, text_rect, num_rect, red_block_image):
        self.rect = full_rect
        self.image = pygame.Surface(full_rect.size).convert()
        self.image.set_colorkey(MAGENTA)
        self.text_rect = text_rect
        self.num_rect = num_rect
        self.red_block_image = red_block_image
        self.red_block_width = red_block_image.get_rect().width
        self.update_images()

    @property
    def given_response(self):
        return self._given_response

    @given_response.setter
    def given_response(self, value):
        self._given_response = value
        self.update_images()

    def reveal_phrase(self):
        self.reveal_stage = self.PHRASE_REVEALED
        self.start_animation()

    def reveal_value(self):
        self.reveal_stage = self.COUNT_REVEALED
        self.end_animation()
        self.render()

    def hide(self):
        self.reveal_stage = self.UNREVEALED
        self.render()

    def update_images(self):
        with GraphicsManager.instance.lock:
            self.revealed_image = pygame.Surface(self.rect.size).convert()
            self.revealed_image.fill(MAGENTA)
            if not self.response:
                self.render()
                return
            font = self.font_helper.fits_default(self.given_response, 72, self.text_rect)
            text_image = font.render(self.given_response, False, SILVER)
            rendered_rect = text_image.get_rect()
            rendered_rect.x = self.text_rect.x + 5  # self.text_rect.centerx - rendered_rect.centerx
            rendered_rect.y = self.text_rect.centery - rendered_rect.centery
            self.revealed_image.blit(text_image, rendered_rect)
            font = self.font_helper.fits_default(str(self.response.count), 72, self.num_rect)
            num_image = font.render(str(self.response.count), False, SILVER)
            rendered_rect = num_image.get_rect()
            rendered_rect.x = self.num_rect.centerx - rendered_rect.centerx
            rendered_rect.y = self.num_rect.centery - rendered_rect.centery
            self.revealed_image.blit(num_image, rendered_rect)
        self.render()

    def tick(self):
        if self.animation_counter >= 4 * TICKS_PER_SEC:
            self.animation_counter = 2 * TICKS_PER_SEC
        self.render()

    def render(self):
        if (not self.response) or self.reveal_stage == self.UNREVEALED:
            self.image.fill(MAGENTA)
        elif self.reveal_stage == self.COUNT_REVEALED:
            self.image.blit(self.revealed_image, (0, 0))
        elif self.reveal_stage == self.PHRASE_REVEALED:
            self.image.fill(MAGENTA)
            temp_width = (self.text_rect.width - self.red_block_width) * min(1.0, self.animation_counter / (
                    2 * TICKS_PER_SEC))
            temp_rect = pygame.Rect(0, 0, temp_width, self.rect.height)
            self.image.blit(self.revealed_image, (0, 0), temp_rect)
            if self.animation_counter < 2 * TICKS_PER_SEC:
                # revealing phrase
                temp_rect.x = temp_rect.width
                self.image.blit(self.red_block_image, temp_rect)
            elif self.animation_counter < 3 * TICKS_PER_SEC:
                # flashing red box over count
                self.image.blit(self.red_block_image, self.num_rect.topleft)


class StrikeDisplay(AnimatedSprite):
    """
    Displays the strikes on the screen
    """

    def __init__(self):
        super().__init__()
        self.rect = None
        self.image = None
        self.strike_images = list()

    def set_display(self, rect, strike_image):
        self.strike_images.clear()
        self.rect = rect
        strike_rect = strike_image.get_rect()
        loc = Vector2()
        loc.y = (rect.height / 2) - strike_rect.centery

        # No strikes
        self.strike_images.append(pygame.Surface(rect.size).convert())
        self.strike_images[0].set_colorkey(MAGENTA)
        self.strike_images[0].fill(MAGENTA)

        # One strike
        self.strike_images.append(pygame.Surface(rect.size).convert())
        self.strike_images[1].set_colorkey(MAGENTA)
        self.strike_images[1].fill(MAGENTA)
        loc.x = (rect.width / 2) - strike_rect.centerx
        self.strike_images[1].blit(strike_image, tuple(loc))

        # Two strikes
        self.strike_images.append(pygame.Surface(rect.size).convert())
        self.strike_images[2].set_colorkey(MAGENTA)
        self.strike_images[2].fill(MAGENTA)
        loc.x = (rect.width / 3) - strike_rect.centerx
        self.strike_images[2].blit(strike_image, tuple(loc))
        loc.x = (2 * rect.width / 3) - strike_rect.centerx
        self.strike_images[2].blit(strike_image, tuple(loc))

        # Three strikes
        self.strike_images.append(pygame.Surface(rect.size).convert())
        self.strike_images[3].set_colorkey(MAGENTA)
        self.strike_images[3].fill(MAGENTA)
        loc.x = 0
        self.strike_images[3].blit(strike_image, tuple(loc))
        loc.x = (rect.width / 2) - strike_rect.centerx
        self.strike_images[3].blit(strike_image, tuple(loc))
        loc.x = rect.width - strike_rect.width
        self.strike_images[3].blit(strike_image, tuple(loc))
        self.render()

    def show_strikes(self, num_strikes):
        self.start_animation(num_strikes)
        self.render()

    def tick(self):
        if self.animation_counter >= 2 * TICKS_PER_SEC:
            self.end_animation()
        self.render()

    def render(self):
        self.image = self.strike_images[self.current_animation or 0]


class TimerLabel(TextLabel, AnimatedSprite):
    """
    Fast money timer label
    """

    def __init__(self, font_helper):
        super().__init__(font_helper)
        # Set up the initial text without rect yet
        self._text = "0"

    @property
    def time(self):
        return int(self.text)

    @time.setter
    def time(self, seconds):
        self.text = str(seconds)

    def start_countdown(self):
        self.start_animation()

    def stop_countdown(self):
        self.end_animation()

    def tick(self):
        # Note: in this I use self.time NOT self._time
        # If counter is 0 then stop
        if not self.time:
            self.stop_countdown()
        # Every second, increase the count
        if not self.animation_counter % TICKS_PER_SEC:
            self.time -= 1


class FontHelper:
    """
    A font that can have multiple sizes
    """

    def __init__(self, path):
        """
        Create a font helper with the font from the given path.
        Invalid paths will raise OSError.

        :param path: the path to the font
        """
        if not os.path.exists(path):
            raise OSError("The given font path is not valid: {}".format(path))
        self.path = path
        self._font_objects = {}

    def get(self, size):
        """
        Get a font object of the given size.
        Caches font objects to reduce memory usage.

        :param size: the size to get of the font

        :return: the font object for the given size
        """
        if size not in self._font_objects.keys():
            self._font_objects[size] = self._get_no_cache(size)
        return self._font_objects[size]

    def _get_no_cache(self, size):
        return pygame.font.Font(self.path, size)

    def fits(self, text, max_font_size, rect_size):
        """ TODO: Maybe make this a binary search instead of linear
        Get a font object of the largest size at or below given max size that fits the given
        text in the given rectangular size.

        :param text: the text to fit
        :param max_font_size: the maximum font size
        :param rect_size: the size to fit the text in (can be Rect or list/tuple)

        :return: the largest possible font object for the text size or else None
        """
        if isinstance(rect_size, pygame.Rect):
            rect_size = rect_size.size
        # TODO: Make the step size customizable since don't always need to check size? or maybe just do the binary search
        for i in range(max_font_size, 1, -5):
            font_size = max(1, i)
            text_size = self._get_no_cache(font_size).size(text)
            if rect_size[1] < text_size[1]:
                continue
            if rect_size[0] < text_size[0]:
                continue
            return self.get(font_size)
        return None

    def fits_default(self, text, max_font_size, rect_size, default_size=1):
        """
        Uses fit but if not found then uses the default size argument to get a font

        :param text: see fit()
        :param max_font_size: see fit()
        :param rect_size: see fit()
        :param default_size: the size to default to if nothing fits

        :return: a font that fits or a font of the default size
        """
        return self.fits(text, max_font_size, rect_size) or self.get(default_size)


# TODO: make all the objects only fully set self.image at end of updating image (due to multithreading) or use lock
# TODO: asset directory relative
class GraphicsManager:
    instance = None

    RAW_RESOLUTION = Vector2(1920, 1080)

    ID_RECT = pygame.Rect(1620, 1008, 300, 72)

    TEAM_1_NAME_RECT = pygame.Rect(83, 336, 364, 81)
    TEAM_2_NAME_RECT = pygame.Rect(1474, 336, 364, 81)

    TEAM_1_SCORE_RECT = pygame.Rect(128, 449, 274, 186)
    TEAM_2_SCORE_RECT = pygame.Rect(1518, 449, 274, 186)
    MASTER_SCORE_RECT = pygame.Rect(826, 69, 270, 195)

    MAIN_CARDS_TOPLEFT = pygame.Rect(556, 292, 389, 116)
    MAIN_CARDS_DELTA = Vector2(416, 134)  # 972 - 556, 426 - 292
    MAIN_CARDS_TEXT_IN_CARD = pygame.Rect(14, 15, 271, 86)
    MAIN_CARDS_NUMBER_IN_CARD = pygame.Rect(290, 15, 84, 86)
    MAIN_CARDS_RANK_NUM_ON_CARD = pygame.Rect(136, 18, 116, 80)
    MAIN_STRIKE_BOX = pygame.Rect(410, 390, 1100, 300)

    FM_CARDS_TOPLEFT = pygame.Rect(169, 104, 773, 112)
    FM_CARDS_DELTA = Vector2(807, 150)  # 976 - 169, 251 - 104 (+3?)
    FM_CARDS_TEXT_IN_CARD = pygame.Rect(0, 0, 634, 112)
    FM_CARDS_NUMBER_IN_CARD = pygame.Rect(661, 0, 112, 112)
    FM_TIMER_RECT = pygame.Rect(806, 881, 180, 150)
    FM_TOTAL_TEXT = pygame.Rect(1341, 876, 269, 112)
    FM_TOTAL_NUMBER = pygame.Rect(1637, 876, 112, 112)

    def __init__(self, resolution=None):
        """
        Creates the all the graphical elements

        :param resolution: the screen resolution (a Vector2 with width and height or an array)
        """
        GraphicsManager.instance = self
        self.lock = Lock()
        self.font_helper = FontHelper(ASSET_DIR + r"\MuktaMahee-Regular.ttf")
        monitor_info = pygame.display.Info()
        self.monitor_resolution = Vector2(monitor_info.current_w, monitor_info.current_h)
        if not resolution:
            resolution = Vector2(self.monitor_resolution)
        if not isinstance(resolution, Vector2):
            resolution = Vector2(resolution)
        self.resolution = Vector2()
        self.scaling = Vector2()
        self.clock = pygame.time.Clock()

        # Create raw images
        self.raw_logo_left = pygame.image.load(ASSET_DIR + r"\images\logo_left.png")
        self.raw_logo_right = pygame.image.load(ASSET_DIR + r"\images\logo_right.png")
        self.raw_main_board = pygame.image.load(ASSET_DIR + r"\images\main_board.png")
        self.raw_main_card_revealed = pygame.image.load(ASSET_DIR + r"\images\answer_card.png")
        self.raw_main_card_hidden = list()
        hidden_bg = pygame.image.load(ASSET_DIR + r"\images\hidden_card.png")
        for i in range(8):
            num_image = pygame.image.load(ASSET_DIR + r"\images\{}.png".format(i + 1))
            current_image = hidden_bg.copy()
            current_image.blit(num_image, self.MAIN_CARDS_RANK_NUM_ON_CARD)
            self.raw_main_card_hidden.append(current_image)
        self.raw_strike = pygame.image.load(ASSET_DIR + r"\images\strike.png")
        self.raw_fm_board = pygame.image.load(ASSET_DIR + r"\images\fast_money_board.png")
        self.raw_fm_red_box = pygame.image.load(ASSET_DIR + r"\images\fast_money_red_box.png")

        # Create static objects
        self.main_bg = None
        self.fm_bg = None

        # Create sprite objects
        self.id_display = IDLabel(self.font_helper)
        self.logo_split = LogoSplit()
        self.strikes = StrikeDisplay()
        # self.team_1_name = TextBox(self.font_helper)
        # self.team_2_name = TextBox(self.font_helper)
        self.master_score = TextLabel(self.font_helper)
        self.team_1_score = TextLabel(self.font_helper)
        self.team_2_score = TextLabel(self.font_helper)
        self.main_cards = list(MainResponseCard(self.font_helper) for _ in range(8))
        self.fm_cards = list(FastMoneyResponseCard(self.font_helper) for _ in range(10))
        self.fm_timer = TimerLabel(self.font_helper)
        self.fm_total_text = TextLabel(self.font_helper)
        self.fm_points = TextLabel(self.font_helper)

        # Add sprites to groups for the different states
        self.state_groups = list(pygame.sprite.OrderedUpdates() for _ in range(4))
        # Logo
        self.state_groups[0].add(self.logo_split)
        self.state_groups[0].add(self.id_display)
        # Main Game
        # self.state_groups[1].add(self.team_1_name)
        self.state_groups[1].add(self.team_1_score)
        # self.state_groups[1].add(self.team_2_name)
        self.state_groups[1].add(self.team_2_score)
        self.state_groups[1].add(self.master_score)
        self.state_groups[1].add(*self.main_cards)
        self.state_groups[1].add(self.strikes)
        self.state_groups[1].add(self.logo_split)
        self.state_groups[1].add(self.id_display)
        # Fast Money
        self.state_groups[2].add(*self.fm_cards)
        self.state_groups[2].add(self.fm_points)
        self.state_groups[2].add(self.fm_total_text)
        self.state_groups[2].add(self.fm_timer)
        self.state_groups[2].add(self.logo_split)
        self.state_groups[2].add(self.id_display)
        # Credits State
        self.state_groups[3].add(self.logo_split)

        # Create the display screen and update sprite images
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        pygame.display.set_caption("The Feud")
        pygame.display.set_icon(pygame.image.load(ASSET_DIR + r"\images\icon.png"))
        self.screen = None
        self.set_resolution(resolution)

        # Set static value
        self.fm_total_text.text = "TOTAL"

    def scale_rect(self, rect):
        """
        Scales a copy of the rect

        :param rect: the rect to get scaled form of

        :return: scaled copy of given rect
        """
        ret = rect.copy()
        ret.x *= self.scaling.x
        ret.y *= self.scaling.y
        ret.width *= self.scaling.x
        ret.height *= self.scaling.y
        return ret

    def scale_image(self, image):
        """
        Gets a scaled copy of the image provided

        :param image: the image to scale

        :return: a scaled copy of the image
        """
        return pygame.transform.smoothscale(image,
                                            (int(image.get_width() * self.scaling.x),
                                             int(image.get_height() * self.scaling.y)))

    @staticmethod
    def vec_to_int_tuple(vec):
        return tuple([int(vec.x), int(vec.y)])

    def set_resolution(self, resolution):
        """
        Updates the resolution scaling for the visuals - also update all components that need to be updated

        :param resolution: the resolution of the new screen (a Vector2 with width and height)
        """

        self.screen = pygame.display.set_mode(self.vec_to_int_tuple(resolution), pygame.NOFRAME)
        self.scaling.update(resolution.x / self.RAW_RESOLUTION.x, resolution.y / self.RAW_RESOLUTION.y)
        self.resolution = Vector2(resolution)
        # Create scaled images
        self.main_bg = self.scale_image(self.raw_main_board)
        self.fm_bg = self.scale_image(self.raw_fm_board)
        self.id_display.set_display(self.scale_rect(self.ID_RECT))
        self.logo_split.set_display(tuple(resolution), self.scale_image(self.raw_logo_left),
                                    self.scale_image(self.raw_logo_right))
        self.strikes.set_display(self.scale_rect(self.MAIN_STRIKE_BOX), self.scale_image(self.raw_strike))
        # TODO: make names a thing?
        # self.team_1_name.set_rect(self.scale_rect(self.TEAM_1_NAME_RECT))
        # self.team_2_name.set_rect(self.scale_rect(self.TEAM_2_NAME_RECT))
        self.master_score.set_display(self.scale_rect(self.MASTER_SCORE_RECT))
        self.team_1_score.set_display(self.scale_rect(self.TEAM_1_SCORE_RECT))
        self.team_2_score.set_display(self.scale_rect(self.TEAM_2_SCORE_RECT))
        for i in range(len(self.main_cards)):
            card_rect = self.MAIN_CARDS_TOPLEFT.copy()
            card_rect.x += int(i / 4) * self.MAIN_CARDS_DELTA.x
            card_rect.y += (i % 4) * self.MAIN_CARDS_DELTA.y
            self.main_cards[i].set_display(self.scale_rect(card_rect), self.scale_rect(self.MAIN_CARDS_TEXT_IN_CARD),
                                           self.scale_rect(self.MAIN_CARDS_NUMBER_IN_CARD),
                                           self.scale_image(self.raw_main_card_hidden[i]),
                                           self.scale_image(self.raw_main_card_revealed))
        for i in range(len(self.fm_cards)):
            card_rect = self.FM_CARDS_TOPLEFT.copy()
            card_rect.x += int(i / 5) * self.FM_CARDS_DELTA.x
            card_rect.y += (i % 5) * self.FM_CARDS_DELTA.y
            self.fm_cards[i].set_display(self.scale_rect(card_rect), self.scale_rect(self.FM_CARDS_TEXT_IN_CARD),
                                         self.scale_rect(self.FM_CARDS_NUMBER_IN_CARD),
                                         self.scale_image(self.raw_fm_red_box))
        self.fm_timer.set_display(self.scale_rect(self.FM_TIMER_RECT))
        self.fm_total_text.set_display(self.scale_rect(self.FM_TOTAL_TEXT))
        self.fm_points.set_display(self.scale_rect(self.FM_TOTAL_NUMBER))

    def update_display(self, state):
        """
        Updates and then draws all the sprites in the given state

        :param state: the state to update and draw for
        """
        self.screen.fill(WHITE)
        if state == GameState.PREPARING:
            current_group = self.state_groups[0]
        elif state == GameState.FAST_MONEY:
            current_group = self.state_groups[2]
            self.screen.blit(self.fm_bg, (0, 0))
        elif state == GameState.CREDITS:
            current_group = self.state_groups[3]
        else:
            current_group = self.state_groups[1]
            self.screen.blit(self.main_bg, (0, 0))
        with self.lock:
            current_group.update()
            current_group.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(TICKS_PER_SEC)
