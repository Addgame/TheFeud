import json
import os
from tkinter import *

import pygame

os.environ["SDL_VIDEO_CENTERED"] = 'True'

SCORE_DISPLAY_SIZE = (135, 115)
RESPONSE_DISPLAY_SIZE = (320, 65)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class NumberDisplay(pygame.sprite.Sprite):
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
        self.image = pygame.Surface(SCORE_DISPLAY_SIZE).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        text_surf = large_font.render(str(self.value), True, WHITE)
        self.image.blit(text_surf, (self.image.get_rect().size[0] / 2 - text_surf.get_rect().size[0] / 2, 0))

    def click(self):
        new_value = int(input("Enter the new value for the display " + self.name + ": "))
        self.value = new_value


class ScoreboardResponse(pygame.sprite.Sprite):
    def __init__(self, response, count, response_number, loc, *groups):
        super().__init__(*groups)
        self.response = response
        self.count = int(count)
        self._revealed = False
        self.response_number = response_number
        self.rect = pygame.Rect(loc, RESPONSE_DISPLAY_SIZE)
        self.hidden_image = pygame.Surface(RESPONSE_DISPLAY_SIZE).convert_alpha()
        self.hidden_image.fill((255, 255, 255, 0))
        self.hidden_image.blit(pygame.image.load("number_bg" + str(response_number) + ".png"), (115, 0))
        self.response_image = pygame.Surface(RESPONSE_DISPLAY_SIZE).convert_alpha()
        self.response_image.fill((255, 255, 255, 0))
        self.response_image.blit(font.render(" " + response, True, BLACK), (0, 8))
        self.response_image.blit(font.render(str(count), True, BLACK), (RESPONSE_DISPLAY_SIZE[0] - 38, 8))
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
    def from_survey(survey):
        for i in range(1, len(survey) + 1):
            for response, count in survey[i - 1].items():
                ScoreboardResponse(response, count, i,
                                   (170 + (525 - 170) * int((i - 1) / 4), 97 * int((i - 1) % 4) + 165), responses)

    @staticmethod
    def toggle_response(toggle_number):
        for response in responses:
            if response.response_number == toggle_number:
                if response.revealed:
                    main_display.value -= response.count
                else:
                    bell_sound.play()
                    main_display.value += response.count
                response.revealed = not response.revealed


def wrong_answer():
    global strikes
    strikes += 1
    if strikes == 1:
        screen.blit(strike_image, (385, 160))
    elif strikes == 2:
        screen.blit(strike_image, (260, 160))
        screen.blit(strike_image, (520, 160))
    elif strikes == 3:
        screen.blit(strike_image, (135, 160))
        screen.blit(strike_image, (385, 160))
        screen.blit(strike_image, (635, 160))
        strikes = 0
    pygame.display.flip()
    strike_sound.play()
    pygame.time.wait(1000)


def loop():
    global running, show_ts, strikes, current_survey
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    show_ts = not show_ts
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    responses.empty()
                    survey_name = input("Enter the name of the survey to open: ")
                    try:
                        with open("data/" + survey_name + ".json", 'r') as file:
                            current_survey = json.load(file)
                    except:
                        print("ERROR...An error occurred trying to open the survey!")
                        current_survey = []
                    ScoreboardResponse.from_survey(current_survey)
                    main_display.reset()
                    print(current_survey)
                elif event.key == pygame.K_0:
                    left_display.reset()
                    right_display.reset()
                    strikes = 0
                elif event.key == pygame.K_UP:
                    wrong_answer()
                elif event.key == pygame.K_DOWN:
                    strikes = 0
                elif event.key == pygame.K_LEFT:
                    left_display.value += main_display.value
                elif event.key == pygame.K_RIGHT:
                    right_display.value += main_display.value
                elif pygame.K_1 <= event.key <= pygame.K_8:
                    ScoreboardResponse.toggle_response(event.key - pygame.K_0)
                elif event.key == pygame.K_f:
                    pygame.display.set_mode((1024, 576), screen.get_flags() ^ pygame.FULLSCREEN)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_sprite.rect.topleft = event.pos
                    collisions = pygame.sprite.spritecollide(mouse_sprite, displays, False)
                    for d in collisions:
                        d.click()
        screen.blit(active_scoreboard, (0, 0))

        displays.draw(screen)
        responses.draw(screen)

        if show_ts:
            screen.blit(title_screen, (0, 0))

        pygame.display.flip()


root = Tk()

pygame.init()
displays = pygame.sprite.Group()
responses = pygame.sprite.Group()
monitor_info = pygame.display.Info()
screen = pygame.display.set_mode((monitor_info.current_w, monitor_info.current_h),
                                 pygame.RESIZABLE | pygame.NOFRAME)  # , pygame.FULLSCREEN)
active_scoreboard = pygame.image.load("active_scoreboard.png")
title_screen = pygame.image.load("title_screen.png")
strike_image = pygame.image.load("strike.png")
font = pygame.font.SysFont("calibri", 40)
large_font = pygame.font.SysFont("calibri", 120)
bell_sound = pygame.mixer.Sound("bell.wav")
strike_sound = pygame.mixer.Sound("strike.wav")

show_ts = False
strikes = 0
current_survey = []

main_display = NumberDisplay("Main Display Score", (440, 22), displays)
left_display = NumberDisplay("Left Team Score", (2, 328), displays)
right_display = NumberDisplay("Right Team Score", (885, 335), displays)

mouse_sprite = pygame.sprite.Sprite()
mouse_sprite.rect = pygame.Rect(0, 0, 1, 1)

running = True

root.after(0, loop)
root.mainloop()
