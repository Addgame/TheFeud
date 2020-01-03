import os.path as path
from abc import ABC, abstractmethod
from threading import Thread
from tkinter import Tk, PhotoImage, LabelFrame, Label, Radiobutton, Button, Listbox, IntVar, StringVar, N, S, E, W, \
    DISABLED, NORMAL, \
    Entry, Frame, END, Spinbox, RIGHT
from tkinter.messagebox import askquestion

import pygame

from src.audio import AudioManager
from src.constants import GameState, ASSET_DIR
from src.display import GraphicsManager, FastMoneyResponseCard
from src.survey import Survey, Response


class ControlApp:
    """
    The main central control class for the entire game
    Creates the display and audio managers along with a GUI to control everything
    """

    BG_COLOR = "#d9d9d9"
    BUTTON_COLOR = "#dfdfdf"
    LISTBOX_COLOR = "#d0d0d0"

    PREPARING_MAIN, PREPARING_FM = range(2)

    def __init__(self, root):
        self.root = root
        # Main Window
        root.geometry("800x800")
        root.title("The Feud Game Control")
        root.iconphoto(True, PhotoImage(file=path.realpath(ASSET_DIR + r"images\icon.png")))
        root.configure(background=self.BG_COLOR)
        root.protocol("WM_DELETE_WINDOW", self.click_close)

        # Setup display
        self.display_manager = GraphicsManager()
        self.graphics_thread = Thread(target=self.display_callback)
        self.quitting = False
        self.display_manager.team_1_score.text = "0"
        self.display_manager.team_2_score.text = "0"

        # Setup audio
        self.audio_manager = AudioManager()

        # Mode Selection (the game state)
        self.mode = GameState.PREPARING
        mode_frame = LabelFrame(root, text="Mode", bg=self.BG_COLOR)
        self.mode_var = IntVar(value=0)
        self.mode_var.trace_add("write", self.select_mode)
        self.mode_buttons = []
        for state in GameState:
            rb = Radiobutton(mode_frame, text=str(state), bg=self.BUTTON_COLOR, indicator=0, padx=19, value=state.value,
                             variable=self.mode_var, state=DISABLED if 1 <= state.value <= 6 else NORMAL)
            rb.grid(row=0, column=state.value, padx=2, pady=2, sticky=N + S + E + W)
            self.mode_buttons.append(rb)
            mode_frame.grid_columnconfigure(state.value, weight=1, uniform="mode_buttons")
        mode_frame.grid(row=0, column=0, padx=10)

        # Preparing
        self.preparing_frame = Frame(root, bg=self.BG_COLOR)

        self.preparing_mode_var = IntVar(value=0)
        self.preparing_mode_var.trace_add("write", self.select_preparing_mode)
        preparing_selector_frame = LabelFrame(self.preparing_frame, text="Preparing Mode", bg=self.BG_COLOR)
        Radiobutton(preparing_selector_frame, text="Main Game", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=0,
                    variable=self.preparing_mode_var).grid(row=0, column=0, padx=2, pady=2)
        preparing_selector_frame.grid_columnconfigure(0, weight=1, uniform="prepare_buttons")
        Radiobutton(preparing_selector_frame, text="Fast Money", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=1,
                    variable=self.preparing_mode_var).grid(row=0, column=1, padx=2, pady=2)
        preparing_selector_frame.grid_columnconfigure(1, weight=1, uniform="prepare_buttons")
        preparing_selector_frame.grid(row=0, column=0, padx=10, columnspan=4, sticky=W)

        preparing_reset_frame = LabelFrame(self.preparing_frame, text="Reset", bg=self.BG_COLOR)
        Button(preparing_reset_frame, text="Main Game Scores", bg=self.BUTTON_COLOR, padx=10,
               command=self.reset_main_scores).grid(
            row=0,
            column=0,
            padx=2,
            pady=2)
        preparing_reset_frame.grid_columnconfigure(0, weight=1, uniform="prepare_reset")
        Button(preparing_reset_frame, text="Fast Money State", bg=self.BUTTON_COLOR, padx=10,
               command=self.reset_fm_state).grid(
            row=0,
            column=1,
            padx=2,
            pady=2)
        preparing_reset_frame.grid_columnconfigure(1, weight=1, uniform="prepare_reset")
        preparing_reset_frame.grid(row=0, column=8, columnspan=4, sticky=E)

        # Main Game Preparing
        self.main_preparing_frame = Frame(self.preparing_frame, bg=self.BG_COLOR)
        self.main_preparing_current_survey_widget = LargeSurveyWidget(self.main_preparing_frame, Survey.NONE,
                                                                      text="Current Survey")
        self.main_preparing_current_survey_widget.grid(row=0, column=0, rowspan=2, padx=4, pady=2, sticky=N + S)
        self.main_preparing_survey_preview_widget = LargeSurveyWidget(self.main_preparing_frame, Survey.NONE,
                                                                      text="Survey Preview")
        self.main_preparing_survey_preview_widget.grid(row=0, column=1, rowspan=2, padx=4, pady=2, sticky=N + S)
        self.main_survey_list_widget = SurveyListWidget(self.main_preparing_frame, self.set_main_preview_survey)
        self.main_survey_list_widget.grid(row=0, column=2, padx=4, pady=2)
        Button(self.main_preparing_frame, text="Set As Current", command=self.set_main_survey_from_preview,
               bg=self.BUTTON_COLOR).grid(
            row=1,
            column=2,
            sticky=N + S + E + W, padx=4, pady=2)

        # Fast Money Preparing
        self.fm_preparing_frame = Frame(self.preparing_frame, bg=self.BG_COLOR)
        self.fm_survey_preview_widget = LargeSurveyWidget(self.fm_preparing_frame, Survey.NONE, text="Survey Preview")
        self.fm_survey_preview_widget.grid(row=0, column=0, sticky=N + S)
        self.fm_survey_list_widget = SurveyListWidget(self.fm_preparing_frame, self.set_fm_preview_survey)
        self.fm_survey_list_widget.grid(row=0, column=1)
        timer_frame = LabelFrame(self.fm_preparing_frame, text="Timer", bg=self.BG_COLOR)
        Label(timer_frame, text="First Player:", bg=self.BG_COLOR).grid(row=0, column=0)
        self.timer_spin_1 = Spinbox(timer_frame, width=2, from_=1, to=99)
        self.timer_spin_1.grid(row=0, column=1)
        Label(timer_frame, text="Second Player:", bg=self.BG_COLOR).grid(row=1, column=0)
        self.timer_spin_2 = Spinbox(timer_frame, width=2, from_=1, to=99)
        self.timer_spin_2.grid(row=1, column=1)
        Button(timer_frame, text="Defaults", bg=self.BUTTON_COLOR,
               command=self.set_fm_timer_defaults).grid(row=2, column=0, columnspan=2)
        self.set_fm_timer_defaults()
        timer_frame.grid(row=0, column=2)
        self.fm_preparing_survey_widgets = []
        for i in range(5):
            self.fm_preparing_survey_widgets.append(
                SmallSurveyWidget(self.fm_preparing_frame, Survey.NONE, text="Survey " + str(i + 1)))
            self.fm_preparing_survey_widgets[i].grid(row=1 + 2 * int(i / 3), column=i % 3)
            Button(self.fm_preparing_frame, text="Set From Preview", bg=self.BUTTON_COLOR,
                   command=lambda num=i: self.set_fm_survey_from_selected(num)).grid(
                row=2 + 2 * int(i / 3), column=i % 3)

        # Render preparing stuff
        self.select_preparing_mode()

        # Main Game
        self.active_team_var = IntVar(value=1)
        self.main_game_frame = Frame(root, bg=self.BG_COLOR)
        self.main_survey_game_widget = SmallSurveyWidget(self.main_game_frame, Survey.NONE, text="Survey")
        self.main_survey_game_widget.grid(row=0, column=0)

        scoring_frame = LabelFrame(self.main_game_frame, text="Scoring", bg=self.BG_COLOR)
        scoring_frame.grid(row=0, column=1, columnspan=2)
        Label(scoring_frame, text="Team 1:", bg=self.BG_COLOR).grid(row=0, column=0)

        self.main_team_1_score_var = StringVar(value="0", name="mt1sv")
        self.main_team_1_score_var.trace_add("write", self.validate_manual_score)
        self.main_team_1_score_entry = Entry(scoring_frame, textvariable=self.main_team_1_score_var, width=6,
                                             justify=RIGHT)
        self.main_team_1_score_entry.grid(row=0, column=1)
        Label(scoring_frame, text="Points:", bg=self.BG_COLOR).grid(row=0, column=2)
        self.main_total_score_var = StringVar(value="0", name="mtsv")
        self.main_total_score_var.trace_add("write", self.validate_manual_score)
        self.main_total_score_entry = Entry(scoring_frame, textvariable=self.main_total_score_var, width=6,
                                            justify=RIGHT)
        self.main_total_score_entry.grid(row=0, column=3)
        Label(scoring_frame, text="Team 2:", bg=self.BG_COLOR).grid(row=0, column=4)
        self.main_team_2_score_var = StringVar(value="0", name="mt2sv")
        self.main_team_2_score_var.trace_add("write", self.validate_manual_score)
        self.main_team_2_score_entry = Entry(scoring_frame, textvariable=self.main_team_2_score_var, width=6,
                                             justify=RIGHT)
        self.main_team_2_score_entry.grid(row=0, column=5)
        Radiobutton(scoring_frame, text="Team 1 Active", bg=self.BUTTON_COLOR, indicator=0,
                    value=1, variable=self.active_team_var).grid(row=1, column=0, columnspan=2, padx=2, pady=2)
        self.give_points_button = Button(scoring_frame, text="Give to Active", bg=self.BUTTON_COLOR,
                                         command=self.give_points_to_active)
        self.give_points_button.grid(row=1, column=2, columnspan=2, padx=2, pady=2)
        Radiobutton(scoring_frame, text="Team 2 Active", bg=self.BUTTON_COLOR, indicator=0, value=2,
                    variable=self.active_team_var).grid(row=1, column=4, columnspan=2, padx=2, pady=2)

        strikes_frame = LabelFrame(self.main_game_frame, text="Strikes", bg=self.BG_COLOR)
        strikes_frame.grid(row=1, column=0)
        self.multi_strikes_frame = Frame(strikes_frame)
        current_strikes_label = Label(self.multi_strikes_frame, text="Current:", bg=self.BG_COLOR)
        current_strikes_label.grid(row=0, column=0)
        self.strikes_spin = Spinbox(self.multi_strikes_frame, width=1, from_=1, to=3, validate="all",
                                    vcmd=(self.root.register(self.validate_strike_value), "%P"))
        self.strikes_spin.grid(row=0, column=1)
        self.multi_strikes_frame.grid(row=0, column=0)
        Button(strikes_frame, text="Strike", bg=self.BUTTON_COLOR, command=self.press_strike_button).grid(row=1,
                                                                                                          column=0,
                                                                                                          sticky=W + E,
                                                                                                          padx=2,
                                                                                                          pady=2)
        strikes_frame.grid_columnconfigure(0, minsize=70)

        self.round_frame = LabelFrame(self.main_game_frame, text="Round", bg=self.BG_COLOR)
        self.round_frame.grid(row=1, column=1)
        self.static_round_number = 1
        self.round_number_var = IntVar(value=1)
        self.round_number_var.trace_add("write", self.update_score_multiplier)
        for i in range(3):
            Radiobutton(self.round_frame, text="Round " + str(i + 1), bg=self.BUTTON_COLOR, indicator=0, value=i + 1,
                        variable=self.round_number_var).grid(row=0, column=i, padx=2, pady=2)

        self.main_responses_widget = MainSurveyResponsesWidget(self.main_game_frame, Survey.NONE,
                                                               self.set_main_response_visibility, text="Responses")
        self.main_responses_widget.grid(row=2, column=0, columnspan=2)

        # Fast Money
        self.fast_money_frame = Frame(root, bg=self.BG_COLOR)
        fm_player_responses_frame = Frame(self.fast_money_frame, bg=self.BG_COLOR)
        Label(fm_player_responses_frame, text="Player 1", bg=self.BG_COLOR).grid(row=0, column=0)
        Label(fm_player_responses_frame, text="Player 2", bg=self.BG_COLOR).grid(row=0, column=1)
        self.selected_fm_response_var = IntVar(value=0)
        self.selected_fm_response_var.trace_add('write', self.change_selected_fm_response)
        self.fm_player_responses_widget = FastMoneyPlayerResponsesWidget(self.fast_money_frame,
                                                                         self.selected_fm_response_var,
                                                                         self.show_fm_response_phrase,
                                                                         self.show_fm_response_count,
                                                                         self.hide_fm_response)
        self.fm_player_responses_widget.grid(row=0, column=0, columnspan=3, pady=4)
        self.fm_selected_survey_widget = SmallSurveyWidget(self.fast_money_frame, Survey.NONE,
                                                           text="Survey of Selected")
        self.fm_selected_survey_widget.grid(row=1, column=0)
        fm_timer_frame = LabelFrame(self.fast_money_frame, text="Timer", bg=self.BG_COLOR)
        fm_timer_frame.grid(row=2, column=0, pady=2)
        Button(fm_timer_frame, text="Set First", bg=self.BUTTON_COLOR,
               command=self.fm_set_time_1).grid(row=0, column=0, sticky=W + E, padx=2, pady=2)
        fm_timer_frame.grid_columnconfigure(0, weight=1, uniform="fm_timer")
        Button(fm_timer_frame, text="Set Second", bg=self.BUTTON_COLOR,
               command=self.fm_set_time_2).grid(row=0, column=1, sticky=W + E, padx=2, pady=2)
        fm_timer_frame.grid_columnconfigure(1, weight=1, uniform="fm_timer")
        self.fm_timer_toggle_button = Button(fm_timer_frame, text="Start", bg=self.BUTTON_COLOR,
                                             command=self.toggle_fm_timer)
        self.fm_timer_toggle_button.grid(row=1, column=0, columnspan=2, sticky=W + E, padx=2, pady=2)
        visibility_frame = LabelFrame(self.fast_money_frame, text="Visibility", bg=self.BG_COLOR)
        self.visibility_var = IntVar(value=1)
        self.visibility_var.trace_add('write', self.update_fm_visible)
        Radiobutton(visibility_frame, text="Show", bg=self.BUTTON_COLOR, indicator=0, variable=self.visibility_var,
                    value=1).grid(row=0, column=0, sticky=W + E)
        Radiobutton(visibility_frame, text="Hide", bg=self.BUTTON_COLOR, indicator=0, variable=self.visibility_var,
                    value=0).grid(row=0, column=1, sticky=W + E)
        visibility_frame.grid_columnconfigure(0, minsize=73)
        visibility_frame.grid_columnconfigure(1, minsize=73)
        visibility_frame.grid(row=3, column=0, pady=2)
        self.fm_survey_responses_widget = FastMoneySurveyResponsesWidget(self.fast_money_frame, Survey.NONE,
                                                                         self.fm_link_to_selected)
        self.fm_survey_responses_widget.grid(row=1, column=1, rowspan=2)
        retry_sound_frame = LabelFrame(self.fast_money_frame, text="Try Again Sound", bg=self.BG_COLOR)
        Button(retry_sound_frame, text="Play", bg=self.BUTTON_COLOR, command=self.audio_manager.play_try_again,
               padx=30).grid(sticky=W + E, padx=2, pady=2)
        retry_sound_frame.grid(row=3, column=1, sticky=W, padx=7, pady=2)

        self.preparing_frame.grid(row=1, column=0)

        self.graphics_thread.start()

    # General
    def display_callback(self):
        while not self.quitting:
            pygame.event.pump()
            self.display_manager.update(self.mode)

    def click_close(self):
        ret = askquestion("Confirm Action", "Are you sure you want to close the game?")
        if ret == "yes":
            self.quitting = True
            self.graphics_thread.join()
            self.root.destroy()

    # Mode Changes
    def select_mode(self, *_):
        current_state = self.mode
        new_state = GameState(self.mode_var.get())
        # Don't do anything if we aren't actually changing state
        if current_state == new_state:
            return
        if new_state == GameState.STEALING:
            self.active_team_var.set(int(self.active_team_var.get() != 2) + 1)
        if new_state == GameState.REVEALING:
            self.give_points_button.configure(state=DISABLED)
        else:
            self.give_points_button.configure(state=NORMAL)
        if current_state == GameState.FAST_MONEY and self.fm_timer_toggle_button["text"] == "Stop":
            self.toggle_fm_timer()
        if current_state == GameState.PREPARING:
            self.preparing_frame.grid_forget()
        if new_state == GameState.PREPARING:
            self.display_manager.logo_split.close()
            self.preparing_frame.grid(row=1, column=0)
        if GameState.FACE_OFF.value <= new_state.value <= GameState.TIEBREAKER.value:
            if new_state == GameState.TIEBREAKER or new_state == GameState.STEALING or new_state == GameState.FACE_OFF:
                self.multi_strikes_frame.grid_forget()
            else:
                self.multi_strikes_frame.grid(row=0, column=0)
            if new_state == GameState.TIEBREAKER:
                self.round_number_var.set(3)
                self.round_frame.grid_forget()
            else:
                self.round_frame.grid(row=1, column=1)
            if not (GameState.FACE_OFF.value <= current_state.value <= GameState.REVEALING.value) or \
                    new_state == GameState.TIEBREAKER:
                new_survey = self.main_preparing_current_survey_widget.survey
                if new_state == GameState.TIEBREAKER:
                    new_survey = self.make_tiebreaker_survey(new_survey)
                # The order of these two is extremely important
                self.main_responses_widget.survey = new_survey
                self.main_survey_game_widget.survey = new_survey
                #
                for i in range(8):
                    card = self.display_manager.main_cards[i]
                    if i < new_survey.num_responses:
                        card.from_response(self.main_survey_game_widget.survey.responses[i])
                    else:
                        card.from_response(None)
                self.display_manager.master_score.text = 0
                self.main_total_score_var.set("0")
            self.main_game_frame.grid(row=1, column=0)
        else:
            self.main_game_frame.grid_forget()
        if new_state == GameState.FAST_MONEY:
            self.selected_fm_response_var.set(0)
            self.display_manager.fm_points.text = 0
            self.fast_money_frame.grid(row=1, column=0)
            if not self.timer_spin_1.get().isdigit():
                self.timer_spin_1.delete(0, END)
                self.timer_spin_1.insert(0, 20)
            if not self.timer_spin_2.get().isdigit():
                self.timer_spin_2.delete(0, END)
                self.timer_spin_2.insert(0, 25)
        else:
            self.fast_money_frame.grid_forget()
        # Needs to happen here so that the screen behind it is ready
        if current_state == GameState.PREPARING:
            self.display_manager.logo_split.open()
        # Last thing is set new state to current and update display ids to match new state
        self.mode = new_state
        self.update_display_ids()

    @staticmethod
    def make_tiebreaker_survey(survey):
        if not survey.num_responses:
            return survey
        data = {"question": survey.question,
                "responses": [{"response": survey.responses[0].phrase, "count": survey.responses[0].count}]}
        return Survey(data)

    def select_preparing_mode(self, *_):
        # Main Game
        if not self.preparing_mode_var.get():
            self.fm_preparing_frame.grid_forget()
            self.main_preparing_frame.grid(row=1, column=0, columnspan=12)
            self.main_survey_list_widget.reload()
        # Fast Money
        else:
            self.main_preparing_frame.grid_forget()
            self.fm_preparing_frame.grid(row=1, column=0, columnspan=12)
            self.fm_survey_list_widget.reload()
        self.update_display_ids()

    def update_display_ids(self):
        if (self.preparing_mode_var.get() == self.PREPARING_MAIN and self.mode is GameState.PREPARING) or \
                (self.mode is not GameState.FAST_MONEY and self.mode is not GameState.PREPARING):
            self.display_manager.id_display.text = self.main_preparing_current_survey_widget.survey.id
        else:
            id_string = ""
            for i in range(5):
                id_string += str(self.fm_preparing_survey_widgets[i].survey.id)[0:4] + ". "
            id_string.rstrip()
            self.display_manager.id_display.text = id_string

    # Main Game operations
    def set_main_preview_survey(self):
        self.main_preparing_survey_preview_widget.survey = self.main_survey_list_widget.selected

    def set_main_survey_from_preview(self):
        if self.main_preparing_survey_preview_widget.survey == Survey.NONE:
            return
        if self.main_preparing_current_survey_widget.survey == Survey.NONE:
            for i in range(1, 6):
                self.mode_buttons[i].configure(state=NORMAL)
        self.main_preparing_current_survey_widget.survey = self.main_preparing_survey_preview_widget.survey
        self.update_display_ids()

    def set_main_response_visibility(self, rank, visible):
        current_score = int(self.main_total_score_var.get())
        if visible:
            self.audio_manager.play_correct()
            self.display_manager.main_cards[rank].reveal()
            current_score += self.static_round_number * self.main_survey_game_widget.survey.responses[rank].count
        else:
            self.display_manager.main_cards[rank].hide()
            current_score -= self.static_round_number * self.main_survey_game_widget.survey.responses[rank].count
        self.display_manager.master_score.text = str(current_score)
        self.main_total_score_var.set(str(current_score))

    def validate_manual_score(self, name, *_):
        # Validate int
        var = None
        text_label = None
        if name == "mt1sv":
            var = self.main_team_1_score_var
            text_label = self.display_manager.team_1_score
        elif name == "mtsv":
            var = self.main_total_score_var
            text_label = self.display_manager.master_score
        elif name == "mt2sv":
            var = self.main_team_2_score_var
            text_label = self.display_manager.team_2_score
        value = int(''.join(filter(lambda x: x.isdigit(), var.get())) or 0)
        var.set(str(value))
        # Update the display
        text_label.text = value

    def reset_main_scores(self):
        self.main_team_1_score_var.set("0")
        self.display_manager.team_1_score.text = "0"
        self.main_team_2_score_var.set("0")
        self.display_manager.team_2_score.text = "0"

    def update_score_multiplier(self, *_):
        old_mult = self.static_round_number
        new_mult = self.round_number_var.get()

        new_total = int((new_mult * int(self.main_total_score_var.get())) / old_mult)
        self.main_total_score_var.set(str(new_total))
        self.display_manager.master_score.text = new_total

        # Last thing is update previous value
        self.static_round_number = new_mult

    def press_strike_button(self):
        self.audio_manager.play_strike()
        if self.mode == GameState.FACE_OFF or self.mode == GameState.STEALING or self.mode == GameState.TIEBREAKER:
            self.display_manager.strikes.show_strikes(1)
            return
        current = max(0, min(3, int(self.strikes_spin.get() or 1)))
        self.display_manager.strikes.show_strikes(current)
        self.strikes_spin.delete(0, END)
        self.strikes_spin.insert(0, str(min(current + 1, 3)))

    @staticmethod
    def validate_strike_value(text):
        if not text or (text.isdigit() and 0 <= int(text) <= 3):
            return True
        return False

    def give_points_to_active(self):
        if self.active_team_var.get() == 1:
            current_score = int(self.main_team_1_score_var.get())
            current_score += int(self.main_total_score_var.get())
            self.main_team_1_score_var.set(str(current_score))
            self.display_manager.team_1_score.text = current_score
        else:
            current_score = int(self.main_team_2_score_var.get())
            current_score += int(self.main_total_score_var.get())
            self.main_team_2_score_var.set(str(current_score))
            self.display_manager.team_2_score.text = current_score

    # Fast Money Operations
    def toggle_fm_timer(self):
        if not self.display_manager.fm_timer.time > 0:
            return
        if self.fm_timer_toggle_button["text"] == "Start":
            self.fm_timer_toggle_button.configure(text="Stop")
            self.root.after(1000, self.fm_timer_tick)
        else:
            self.fm_timer_toggle_button.configure(text="Start")

    def fm_timer_tick(self):
        if self.display_manager.fm_timer.time == 0:
            self.fm_timer_toggle_button.configure(text="Start")
            return
        if self.fm_timer_toggle_button["text"] == "Start":
            return
        self.display_manager.fm_timer.time -= 1
        if self.display_manager.fm_timer.time == 0:
            self.audio_manager.play_timer_end()
        self.root.after(1000, self.fm_timer_tick)

    def set_fm_timer_defaults(self):
        self.timer_spin_1.delete(0, END)
        self.timer_spin_1.insert(0, 20)
        self.timer_spin_2.delete(0, END)
        self.timer_spin_2.insert(0, 25)

    def fm_set_time_1(self):
        self.display_manager.fm_timer.time = self.timer_spin_1.get()

    def fm_set_time_2(self):
        self.display_manager.fm_timer.time = self.timer_spin_2.get()

    def set_fm_survey_from_selected(self, survey_num):
        self.fm_preparing_survey_widgets[survey_num].survey = self.fm_survey_preview_widget.survey
        if self.mode_buttons[GameState.FAST_MONEY.value]["state"] == "disabled":
            for i in range(5):
                if self.fm_preparing_survey_widgets[i].survey == Survey.NONE:
                    break
            else:
                self.mode_buttons[GameState.FAST_MONEY.value].configure(state=NORMAL)
        self.update_display_ids()

    def set_fm_preview_survey(self):
        if self.fm_survey_list_widget.selected == Survey.NONE:
            return
        self.fm_survey_preview_widget.survey = self.fm_survey_list_widget.selected

    def show_fm_response_phrase(self, index, phrase):
        card = self.display_manager.fm_cards[index]
        card.phrase = phrase
        if card.reveal_stage == FastMoneyResponseCard.COUNT_REVEALED:
            curr_count = int(self.display_manager.fm_points.text)
            self.display_manager.fm_points.text = str(curr_count - card.count)
        card.reveal_phrase()
        self.audio_manager.play_fm_reveal()

    def show_fm_response_count(self, index, count):
        card = self.display_manager.fm_cards[index]
        card.count = count
        card.reveal_value()
        curr_count = int(self.display_manager.fm_points.text)
        self.display_manager.fm_points.text = str(curr_count + count)
        if count:
            self.audio_manager.play_correct()
        else:
            self.audio_manager.play_fm_wrong()

    def hide_fm_response(self, index):
        card = self.display_manager.fm_cards[index]
        if card.reveal_stage == FastMoneyResponseCard.COUNT_REVEALED:
            curr_count = int(self.display_manager.fm_points.text)
            self.display_manager.fm_points.text = str(curr_count - card.count)
        card.hide()

    def fm_link_to_selected(self, count):
        self.fm_player_responses_widget.set_response(self.selected_fm_response_var.get(), count)

    def change_selected_fm_response(self, *_):
        survey = self.fm_preparing_survey_widgets[self.selected_fm_response_var.get() % 5].survey
        self.fm_survey_responses_widget.survey = survey
        self.fm_selected_survey_widget.survey = survey

    def update_fm_visible(self, *_):
        if self.visibility_var.get() == 0 and not self.display_manager.logo_split.closed:
            self.display_manager.logo_split.close()
        elif self.visibility_var.get() == 1 and self.display_manager.logo_split.closed:
            self.display_manager.logo_split.open()

    def reset_fm_state(self):
        self.fm_player_responses_widget.reset()


class ResponseWidget(Frame):
    """
    Widget to display a single response
    """

    def __init__(self, root, response):
        super().__init__(root, bg=ControlApp.BG_COLOR)
        self._response = response
        self.rank_label = Label(self, text="#X | ", bg=ControlApp.BG_COLOR)
        self.rank_label.grid(row=0, column=0, sticky=W)

        self.columnconfigure(1, weight=1)
        self.phrase_label = Label(self, text=Response.BLANK_PHRASE, bg=ControlApp.BG_COLOR,
                                  justify="left", wraplength=106)
        self.phrase_label.grid(row=0, column=1, sticky=W)

        self.count_label = Label(self, text=" | Count: X", bg=ControlApp.BG_COLOR)
        self.count_label.grid(row=0, column=2)

        self.grid_rowconfigure(0, minsize=36)

        self.update()

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, new):
        self._response = new
        self.update()

    def update(self):
        self.rank_label.configure(text="#" + str(self.response.rank) + " | ")
        self.phrase_label.configure(text=str(self.response.phrase))
        self.count_label.configure(text=" | Count: " + str(self.response.count))


class AbstractSurveyWidget(LabelFrame, ABC):
    """
    Common abstract widget subclass that simplifies dealing with a survey in a widget
    """

    def __init__(self, root, survey, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        self._survey = survey

    @property
    def survey(self):
        return self._survey

    @survey.setter
    def survey(self, new):
        self.reset()
        self._survey = new
        self.update()

    @abstractmethod
    def update(self):
        pass

    def reset(self):
        pass


class SmallSurveyWidget(AbstractSurveyWidget):
    """
    Widget that shows survey ID and question
    """

    def __init__(self, root, survey, **kwargs):
        super().__init__(root, survey, **kwargs)
        Label(self, text="ID: ", bg=ControlApp.BG_COLOR).grid(row=0, column=0)
        self.id_string = StringVar()
        Label(self, textvariable=self.id_string, bg=ControlApp.BG_COLOR).grid(row=0, column=1, sticky=W)
        Label(self, text="Question: ", background=ControlApp.BG_COLOR).grid(row=1, column=0)
        self.question_string = StringVar()
        Label(self, textvariable=self.question_string, bg=ControlApp.BG_COLOR, wraplength=132, justify="left").grid(
            row=1, column=1, sticky=W)
        self.id_string.set(self._survey.id)
        self.question_string.set(self._survey.question)
        self.grid_columnconfigure(1, minsize=145)
        self.grid_rowconfigure(1, minsize=66)

    def update(self):
        self.id_string.set(str(self._survey.id))
        self.question_string.set(self._survey.question)


class LargeSurveyWidget(SmallSurveyWidget):
    """
    Widget that shows survey ID, question, and all responses
    """

    def __init__(self, root, survey, **kwargs):
        super().__init__(root, survey, **kwargs)

        self.response_widgets = []
        Label(self, text="Responses:", bg=ControlApp.BG_COLOR).grid(row=2, column=0,
                                                                    columnspan=2, sticky=W)
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets.append(ResponseWidget(self, self.survey.responses[i]))
            else:
                self.response_widgets.append(
                    ResponseWidget(self, Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)))
            self.response_widgets[i].grid(row=3 + i, column=0, columnspan=2, sticky=W + E)

    def update(self):
        super().update()
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets[i].response = self.survey.responses[i]
            else:
                self.response_widgets[i].response = Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)


class MainSurveyResponsesWidget(AbstractSurveyWidget):
    """
    Widget for controlling visibility of responses for main game
    """

    def __init__(self, root, survey, command, **kwargs):
        super().__init__(root, survey, **kwargs)

        self.visibility_handler = command
        self.response_widgets = []
        self.visibility_buttons = []
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets.append(ResponseWidget(self, self.survey.responses[i]))
                self.visibility_buttons.append(Button(self, text="Show", bg=ControlApp.BUTTON_COLOR,
                                                      command=lambda num=i: self.toggle_button(num)))
            else:
                self.response_widgets.append(
                    ResponseWidget(self, Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)))
                self.visibility_buttons.append(Button(self, text="Show", bg=ControlApp.BUTTON_COLOR, state=DISABLED,
                                                      command=lambda num=i: self.toggle_button(num)))
            self.response_widgets[i].grid(row=i % 4, column=3 * int(i / 4), sticky=W + E)
            self.visibility_buttons[i].grid(row=i % 4, column=3 * int(i / 4) + 1, sticky=W + E)
        self.grid_columnconfigure(1, minsize=40)
        self.grid_columnconfigure(2, minsize=25)
        self.grid_columnconfigure(4, minsize=40)

    def toggle_button(self, i):
        # Swap show and hide and call
        button = self.visibility_buttons[i]
        if button["text"] == "Show":
            self.visibility_handler(i, True)
            button.configure(text="Hide")
        else:
            self.visibility_handler(i, False)
            button.configure(text="Show")

    def update(self):
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets[i].response = self.survey.responses[i]
                self.visibility_buttons[i].configure(text="Show", state=NORMAL)
            else:
                self.response_widgets[i].response = Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)
                self.visibility_buttons[i].configure(text="Show", state=DISABLED)

    def reset(self):
        for i in range(8):
            button = self.visibility_buttons[i]
            if button["text"] == "Hide":
                self.toggle_button(i)


class FastMoneySurveyResponsesWidget(AbstractSurveyWidget):
    """
    Widget for linking to actual survey responses for fast money
    """

    def __init__(self, root, survey, command, **kwargs):
        super().__init__(root, survey, **kwargs)

        self.linking_handler = command
        self.response_widgets = []
        self.link_buttons = []
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets.append(ResponseWidget(self, self.survey.responses[i]))
                self.link_buttons.append(Button(self, text="Link", bg=ControlApp.BUTTON_COLOR,
                                                command=lambda num=i: self.link_response(num)))
            else:
                self.response_widgets.append(
                    ResponseWidget(self, Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)))
                self.link_buttons.append(Button(self, text="Link", bg=ControlApp.BUTTON_COLOR, state=DISABLED,
                                                command=lambda num=i: self.link_response(num)))
            self.response_widgets[i].grid(row=i % 4, column=3 * int(i / 4), sticky=W + E)
            self.link_buttons[i].grid(row=i % 4, column=3 * int(i / 4) + 1)
        self.grid_columnconfigure(2, minsize=25)
        Button(self, text="Unlink", bg=ControlApp.BUTTON_COLOR, padx=15,
               command=lambda: self.link_response(-1)).grid(row=4, column=0, columnspan=5)

    def link_response(self, i):
        if i == -1:
            self.linking_handler(0)
        else:
            self.linking_handler(self.survey.responses[i].count)

    def update(self):
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets[i].response = self.survey.responses[i]
                self.link_buttons[i].configure(state=NORMAL)
            else:
                self.response_widgets[i].response = Response(self.survey, Response.BLANK_PHRASE, 0, i + 1)
                self.link_buttons[i].configure(state=DISABLED)


class FastMoneyPlayerResponsesWidget(Frame):
    """
    Widget where operator writes fast money player responses controls fast money response visibility
    """

    class ResponseInfo:
        def __init__(self, entry, score_var, reveal_button, hide_button):
            self.entry = entry
            self.score_var = score_var
            self.reveal_button = reveal_button
            self.hide_button = hide_button

    def __init__(self, root, selected_var, reveal_response_command, reveal_count_command, hide_command, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        Label(self, text="Player 1", bg=ControlApp.BG_COLOR).grid(row=0, column=0)
        Label(self, text="Player 2", bg=ControlApp.BG_COLOR).grid(row=0, column=1)
        left_responses_frame = Frame(self, bg=ControlApp.BG_COLOR, **kwargs)
        left_responses_frame.grid(row=1, column=0, padx=5)
        right_responses_frame = Frame(self, bg=ControlApp.BG_COLOR, **kwargs)
        right_responses_frame.grid(row=1, column=1, padx=5)
        self.reveal_response_command = reveal_response_command
        self.reveal_count_command = reveal_count_command
        self.hide_command = hide_command
        self.response_infos = []
        for i in range(10):
            if i < 5:
                current_frame = left_responses_frame
            else:
                current_frame = right_responses_frame
            Radiobutton(current_frame, text="Select", bg=ControlApp.BUTTON_COLOR, indicator=0, value=i,
                        variable=selected_var).grid(row=i % 5, column=0)
            current_entry = Entry(current_frame, width=20)
            current_entry.grid(row=i % 5, column=1)
            current_var = StringVar(value="0")
            Label(current_frame, bg=ControlApp.BG_COLOR, textvariable=current_var).grid(row=i % 5, column=2)
            current_reveal_button = Button(current_frame, text="Show Response", bg=ControlApp.BUTTON_COLOR,
                                           command=lambda num=i: self.reveal_clicked(num))
            current_reveal_button.grid(row=i % 5, column=3, sticky=W + E)
            current_hide_button = Button(current_frame, text="Hide All", bg=ControlApp.BUTTON_COLOR,
                                         command=lambda num=i: self.hide_clicked(num))
            current_hide_button.grid(row=i % 5, column=4, sticky=W + E)
            self.response_infos.append(
                self.ResponseInfo(current_entry, current_var, current_reveal_button, current_hide_button))
        left_responses_frame.grid_columnconfigure(2, minsize=20)
        left_responses_frame.grid_columnconfigure(3, minsize=100)
        right_responses_frame.grid_columnconfigure(2, minsize=20)
        right_responses_frame.grid_columnconfigure(3, minsize=100)

    def set_response(self, i, count):
        self.response_infos[i].score_var.set(str(count))

    def reveal_clicked(self, i):
        response_info = self.response_infos[i]
        if response_info.reveal_button["text"] == "Show Response":
            response_info.reveal_button.configure(text="Show Count")
            self.reveal_response_command(i, response_info.entry.get())
        else:  # Show Count
            response_info.reveal_button.configure(text="Show Response")
            self.reveal_count_command(i, int(response_info.score_var.get()))

    def hide_clicked(self, i):
        response_info = self.response_infos[i]
        response_info.reveal_button.configure(text="Show Response")
        self.hide_command(i)

    def reset(self):
        for i in range(10):
            response_info = self.response_infos[i]
            response_info.entry.delete(0, END)
            self.hide_clicked(i)
            response_info.score_var.set("0")


class SurveyListWidget(Frame):
    """
    A Listbox with all the survey names plus a button to reload the list
    """

    def __init__(self, root, select_cb, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        Label(self, text="Survey List", bg=ControlApp.BG_COLOR).grid(row=0, column=0, sticky=W)
        self.listbox = Listbox(self, height=22, width=30)
        self.listbox.grid(row=1, column=0)
        self.listbox.bind("<<ListboxSelect>>", self.clicked)
        self.listbox.configure(activestyle='none')
        self.select_cb = select_cb
        Button(self, text="Reload", command=self.reload, bg=ControlApp.BUTTON_COLOR).grid(row=2, column=0,
                                                                                          sticky=N + S + E + W)
        self.selected = Survey.NONE

    def clicked(self, *_):
        # Need the 'or 0' for some reason
        self.selected = Survey.get_surveys().get(self.listbox.get(self.listbox.curselection() or 0), Survey.NONE)
        self.select_cb()

    def reload(self):
        Survey.reload_all()
        self.update()

    def update(self):
        self.listbox.delete(0, END)
        for name in Survey.get_surveys().keys():
            self.listbox.insert(END, name)
        self.listbox.select_set(0)
        self.clicked()


if __name__ == '__main__':
    pygame.init()

    # Set up tkinter and start looping
    master = Tk()
    ControlApp(master)
    master.mainloop()

    pygame.quit()
