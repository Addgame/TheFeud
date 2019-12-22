import os.path as path
from abc import ABC, abstractmethod
from threading import Thread
from tkinter import Tk, PhotoImage, LabelFrame, Label, Radiobutton, Button, Listbox, IntVar, StringVar, N, S, E, W, \
    DISABLED, NORMAL, \
    Entry, Frame, END, Spinbox, RIGHT
from tkinter.messagebox import askquestion

import pygame

from src.constants import GameState, ASSET_DIR
from src.display import GraphicsManager
from src.survey import Survey, Response


class ControlApp:
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
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        for i in range(12):
            root.grid_columnconfigure(i, weight=1, uniform="root_grid")

        # Setup display
        self.display_manager = GraphicsManager()
        self.graphics_thread = Thread(target=self.display_callback)
        self.quitting = False
        self.display_manager.team_1_score.text = "0"
        self.display_manager.team_2_score.text = "0"

        # Mode Selection (the game state)
        self.mode = GameState.PREPARING
        mode_frame = LabelFrame(root, text="Mode", bg=self.BG_COLOR, width=100, height=100)
        self.mode_var = IntVar(value=0)
        self.mode_var.trace_add("write", self.mode_change)
        self.mode_buttons = []
        for state in GameState:
            rb = Radiobutton(mode_frame, text=str(state), bg=self.BUTTON_COLOR, indicator=0, padx=19, value=state.value,
                             variable=self.mode_var, state=DISABLED if 1 <= state.value <= 7 else NORMAL)
            rb.grid(row=0, column=state.value, padx=2, pady=2, sticky=N + S + E + W)
            self.mode_buttons.append(rb)
            mode_frame.grid_columnconfigure(state.value, weight=1, uniform="mode_buttons")
        mode_frame.grid(row=0, column=0, padx=10, columnspan=12)

        # Preparing
        self.preparing_frame = Frame(root, bg=self.BG_COLOR)

        self.preparing_mode_var = IntVar(value=0)
        self.preparing_mode_var.trace_add("write", self.preparing_mode_change)
        self.preparing_selector = LabelFrame(self.preparing_frame, text="Preparing Mode", bg=self.BG_COLOR)
        Radiobutton(self.preparing_selector, text="Main Game", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=0,
                    variable=self.preparing_mode_var).grid(row=0, column=0, padx=2, pady=2)
        self.preparing_selector.grid_columnconfigure(0, weight=1, uniform="prepare_buttons")
        Radiobutton(self.preparing_selector, text="Fast Money", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=1,
                    variable=self.preparing_mode_var).grid(row=0, column=1, padx=2, pady=2)
        self.preparing_selector.grid_columnconfigure(1, weight=1, uniform="prepare_buttons")
        self.preparing_selector.grid(row=0, column=0, padx=10, columnspan=4, sticky=W)
        # self.name_1_frame = LabelFrame(self.preparing_frame, text="Team 1 Name", bg=self.BG_COLOR)
        # self.name_1_entry = Entry(self.name_1_frame, width=30)
        # self.name_1_entry.grid(padx=2, pady=2)
        # self.name_1_frame.grid(row=0, column=6, columnspan=3)
        # self.name_2_frame = LabelFrame(self.preparing_frame, text="Team 2 Name", bg=self.BG_COLOR)
        # self.name_2_entry = Entry(self.name_2_frame, width=30)
        # self.name_2_entry.grid(padx=2, pady=2)
        # self.name_2_frame.grid(row=0, column=9, columnspan=3)

        # Main Game Preparing
        self.main_preparing_frame = Frame(self.preparing_frame, bg=self.BG_COLOR)
        self.main_current_survey_prep_widget = LargeSurveyWidget(self.main_preparing_frame, Survey.NONE,
                                                                 text="Current Survey")
        self.main_current_survey_prep_widget.grid(row=0, column=0, rowspan=2, padx=4, pady=2)
        self.main_survey_preview_widget = LargeSurveyWidget(self.main_preparing_frame, Survey.NONE,
                                                            text="Survey Preview")
        self.main_survey_preview_widget.grid(row=0, column=1, rowspan=2, padx=4, pady=2)
        self.main_survey_list = SurveyList(self.main_preparing_frame, self.preview_select)
        self.main_survey_list.grid(row=0, column=2, padx=4, pady=2)
        Button(self.main_preparing_frame, text="Set As Current", command=self.set_current, bg=self.BUTTON_COLOR).grid(
            row=1,
            column=2,
            sticky=N + S + E + W, padx=4, pady=2)

        # Fast Money Preparing
        self.fm_preparing_frame = Frame(self.preparing_frame, bg=self.BG_COLOR)
        self.fm_survey_preview = LargeSurveyWidget(self.fm_preparing_frame, Survey.NONE, text="Survey Preview")
        self.fm_survey_preview.grid(row=0, column=0)
        self.fm_survey_list = SurveyList(self.fm_preparing_frame, self.preview_select)
        self.fm_survey_list.grid(row=0, column=1)
        timer_frame = LabelFrame(self.fm_preparing_frame, text="Timer", bg=self.BG_COLOR)
        Label(timer_frame, text="First Player:", bg=self.BG_COLOR).grid(row=0, column=0)
        self.timer_spin_1 = Spinbox(timer_frame, width=2, from_=1, to=99)
        self.timer_spin_1.grid(row=0, column=1)
        Label(timer_frame, text="Second Player:", bg=self.BG_COLOR).grid(row=1, column=0)
        self.timer_spin_2 = Spinbox(timer_frame, width=2, from_=1, to=99)
        self.timer_spin_2.grid(row=1, column=1)
        Button(timer_frame, text="Defaults", bg=self.BUTTON_COLOR,
               command=self.set_timer_defaults).grid(row=2, column=0, columnspan=2)
        self.set_timer_defaults()
        timer_frame.grid(row=0, column=2)
        self.fm_survey_widgets = []
        for i in range(5):
            self.fm_survey_widgets.append(
                SmallSurveyWidget(self.fm_preparing_frame, Survey.NONE, text="Survey " + str(i + 1)))
            self.fm_survey_widgets[i].grid(row=1 + 2 * int(i / 3), column=i % 3)
            Button(self.fm_preparing_frame, text="Set From Preview", bg=self.BUTTON_COLOR,
                   command=lambda num=i: self.set_from_selected(num)).grid(
                row=2 + 2 * int(i / 3), column=i % 3)

        # Render preparing stuff
        self.preparing_mode_change()

        # Main Game
        self.active_team = IntVar(value=1)
        self.main_game_frame = Frame(root, bg=self.BG_COLOR)
        self.main_survey_game_widget = SmallSurveyWidget(self.main_game_frame, Survey.NONE, text="Survey")
        self.main_survey_game_widget.grid(row=0, column=0)

        scoring_frame = LabelFrame(self.main_game_frame, text="Scoring", bg=self.BG_COLOR)
        scoring_frame.grid(row=0, column=1, columnspan=2)
        Label(scoring_frame, text="Team 1:", bg=self.BG_COLOR).grid(row=0, column=0)

        self.main_team_1_score_var = StringVar(value="0", name="mt1sv")
        self.main_team_1_score_var.trace_add("write", self.manual_score_update)
        self.main_team_1_score = Entry(scoring_frame, textvariable=self.main_team_1_score_var, width=6, justify=RIGHT)
        self.main_team_1_score.grid(row=0, column=1)
        Label(scoring_frame, text="Points:", bg=self.BG_COLOR).grid(row=0, column=2)
        self.main_total_score_var = StringVar(value="0", name="mtsv")
        self.main_total_score_var.trace_add("write", self.manual_score_update)
        self.main_total_score = Entry(scoring_frame, textvariable=self.main_total_score_var, width=6, justify=RIGHT)
        self.main_total_score.grid(row=0, column=3)
        Label(scoring_frame, text="Team 2:", bg=self.BG_COLOR).grid(row=0, column=4)
        self.main_team_2_score_var = StringVar(value="0", name="mt2sv")
        self.main_team_2_score_var.trace_add("write", self.manual_score_update)
        self.main_team_2_score = Entry(scoring_frame, textvariable=self.main_team_2_score_var, width=6, justify=RIGHT)
        self.main_team_2_score.grid(row=0, column=5)
        Radiobutton(scoring_frame, text="Team 1 Active", bg=self.BUTTON_COLOR, indicator=0,
                    value=1, variable=self.active_team).grid(row=1, column=0, columnspan=2)
        Button(scoring_frame, text="Give to Active", bg=self.BUTTON_COLOR,
               command=self.give_active_points).grid(row=1, column=2, columnspan=2)
        Radiobutton(scoring_frame, text="Team 2 Active", bg=self.BUTTON_COLOR, indicator=0, value=2,
                    variable=self.active_team).grid(row=1, column=4, columnspan=2)

        # TODO: remove strikes count maybe when only 1 strike possible
        strikes_frame = LabelFrame(self.main_game_frame, text="Strikes", bg=self.BG_COLOR)
        strikes_frame.grid(row=1, column=0)
        self.current_strikes_label = Label(strikes_frame, text="Current:", bg=self.BG_COLOR)
        self.current_strikes_label.grid(row=0, column=0)
        self.strikes_spin = Spinbox(strikes_frame, width=1, from_=1, to=3)
        self.strikes_spin.grid(row=0, column=1)
        Button(strikes_frame, text="Strike", bg=self.BUTTON_COLOR, command=self.activate_strike).grid(row=1, column=0,
                                                                                                      columnspan=2)

        # TODO: remove round number from tiebreaker mode
        round_frame = LabelFrame(self.main_game_frame, text="Round", bg=self.BG_COLOR)
        round_frame.grid(row=1, column=1)
        self.static_round_number = 1
        self.round_number = IntVar(value=1)
        self.round_number.trace_add("write", self.update_score_multiplier)
        for i in range(3):
            Radiobutton(round_frame, text="Round " + str(i + 1), bg=self.BUTTON_COLOR, indicator=0, value=i + 1,
                        variable=self.round_number).grid(row=0, column=i)

        self.main_responses_list = MainSurveyResponsesWidget(self.main_game_frame, Survey.NONE,
                                                             self.set_main_response_visibility, text="Responses")
        self.main_responses_list.grid(row=2, column=0, columnspan=2)

        # Fast Money
        self.fast_money_frame = Frame(root, bg=self.BG_COLOR)
        # place the responses from player here
        fm_player_responses_frame = Frame(self.fast_money_frame, bg=self.BG_COLOR)
        Label(fm_player_responses_frame, text="Player 1", bg=self.BG_COLOR).grid(row=0, column=0)
        Label(fm_player_responses_frame, text="Player 2", bg=self.BG_COLOR).grid(row=0, column=1)
        self.selected_fm_response_var = IntVar(value=0)
        self.selected_fm_response_var.trace_add('write', self.update_selected_fm_response)
        self.fm_player_responses = FastMoneyPlayerResponsesWidget(self.fast_money_frame, self.selected_fm_response_var,
                                                                  self.toggle_fm_response, self.toggle_fm_count)
        self.fm_player_responses.grid(row=0, column=0, columnspan=3)
        self.fm_selected_survey_widget = SmallSurveyWidget(self.fast_money_frame, Survey.NONE,
                                                           text="Survey of Selected")
        self.fm_selected_survey_widget.grid(row=1, column=0)
        # TODO: reorder timer to have time based in control app so ending can be checked
        fm_timer_frame = LabelFrame(self.fast_money_frame, text="Timer", bg=self.BG_COLOR)
        fm_timer_frame.grid(row=2, column=0)
        Button(fm_timer_frame, text="Set First", bg=self.BUTTON_COLOR,
               command=self.fm_set_time_1).grid(row=0, column=0)
        Button(fm_timer_frame, text="Set Second", bg=self.BUTTON_COLOR, command=self.fm_set_time_2).grid(row=0,
                                                                                                         column=1)
        self.fm_timer_toggle_button = Button(fm_timer_frame, text="Start", bg=self.BUTTON_COLOR,
                                             command=self.fm_timer_toggle)
        self.fm_timer_toggle_button.grid(row=1, column=0, columnspan=2)
        visibility_frame = LabelFrame(self.fast_money_frame, text="Visibility", bg=self.BG_COLOR)
        self.visibility_var = IntVar(value=1)
        self.visibility_var.trace_add('write', self.update_fm_visibility)
        Radiobutton(visibility_frame, text="Show", bg=self.BUTTON_COLOR, indicator=0, variable=self.visibility_var,
                    value=1).grid(row=0, column=0)
        Radiobutton(visibility_frame, text="Hide", bg=self.BUTTON_COLOR, indicator=0, variable=self.visibility_var,
                    value=0).grid(row=0, column=1)
        visibility_frame.grid(row=3, column=0)
        self.fm_responses_link = FastMoneySurveyResponsesWidget(self.fast_money_frame, Survey.NONE,
                                                                self.link_to_selected)
        self.fm_responses_link.grid(row=1, column=1, rowspan=2)

        # TODO: Perhaps move this to update GUI?
        self.preparing_frame.grid(row=1, column=0, columnspan=12)

        self.graphics_thread.start()

    def update_gui(self):
        pass

    def preview_select(self):
        # Main Game
        if not self.preparing_mode_var.get():
            self.main_survey_preview_widget.survey = self.main_survey_list.selected
        # Fast Money
        else:
            self.fm_survey_preview.survey = self.fm_survey_list.selected

    def set_current(self):
        if self.main_current_survey_prep_widget.survey == Survey.NONE:
            for i in range(1, 6):
                self.mode_buttons[i].configure(state=NORMAL)
        self.main_current_survey_prep_widget.survey = self.main_survey_preview_widget.survey
        self.set_display_ids()

    # TODO: When swapping modes, change which id format is displayed
    def set_from_selected(self, survey_num):
        self.fm_survey_widgets[survey_num].survey = self.fm_survey_preview.survey
        if self.mode_buttons[GameState.FAST_MONEY.value]["state"] == "disabled":
            for i in range(5):
                if self.fm_survey_widgets[i].survey == Survey.NONE:
                    break
            else:
                self.mode_buttons[GameState.FAST_MONEY.value].configure(state=NORMAL)
        self.set_display_ids()

    def set_display_ids(self):
        if self.preparing_mode_var.get() == self.PREPARING_MAIN and self.mode is not GameState.FAST_MONEY:
            self.display_manager.id_display.text = self.main_current_survey_prep_widget.survey.id
        else:
            id_string = ""
            for i in range(5):
                id_string += str(self.fm_survey_widgets[i].survey.id)[0:4] + ". "
            id_string.rstrip()
            self.display_manager.id_display.text = id_string

    def activate_strike(self, *args):
        if self.mode == GameState.FACE_OFF or self.mode == GameState.STEALING or self.mode == GameState.TIEBREAKER:
            self.display_manager.strikes.show_strikes(1)
            return
        try:
            current = max(0, min(3, int(self.strikes_spin.get())))
        except ValueError:
            print("Error - invalid strikes value")
            return
        self.display_manager.strikes.show_strikes(current)
        self.strikes_spin.delete(0)
        self.strikes_spin.insert(0, str(min(current + 1, 3)))

    # TODO: I'm essentially implementing int vars with string vars so maybe do scores in a better way
    def give_active_points(self):
        if self.active_team.get() == 1:
            current_score = int(self.main_team_1_score_var.get())
            current_score += int(self.main_total_score_var.get())
            self.main_team_1_score_var.set(str(current_score))
            self.display_manager.team_1_score.text = current_score
        else:
            current_score = int(self.main_team_2_score_var.get())
            current_score += int(self.main_total_score_var.get())
            self.main_team_2_score_var.set(str(current_score))
            self.display_manager.team_2_score.text = current_score

    def manual_score_update(self, name, *args):
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

    def update_score_multiplier(self, *args):
        old_mult = self.static_round_number
        new_mult = self.round_number.get()

        new_total = int((new_mult * int(self.main_total_score_var.get())) / old_mult)
        self.main_total_score_var.set(str(new_total))
        self.display_manager.master_score.text = new_total

        # Last thing is update previous value
        self.static_round_number = new_mult

    def display_callback(self):
        while not self.quitting:
            pygame.event.pump()
            self.display_manager.update_display(self.mode)

    def on_close(self):
        ret = askquestion("Confirm Action", "Are you sure you want to close the game?")
        if ret == "yes":
            self.quitting = True
            self.graphics_thread.join()
            self.root.destroy()

    def mode_change(self, *args):
        current_state = self.mode
        new_state = GameState(self.mode_var.get())
        # Don't do anything if we aren't actually changing state
        if current_state == new_state:
            return
        if current_state == GameState.PREPARING:
            self.set_display_ids()
            # TODO: This isn't in the right place
            self.preparing_frame.grid_forget()
        if new_state == GameState.PREPARING:
            self.display_manager.logo_split.close()
            # TODO: This isn't in the right place
            self.preparing_frame.grid(row=1, column=0, columnspan=12)
        if 1 <= new_state.value <= 5:
            if current_state == GameState.PREPARING:
                # self.display_manager.team_1_name.text = self.name_1_entry.get()
                # self.display_manager.team_2_name.text = self.name_2_entry.get()
                new_survey = self.main_current_survey_prep_widget.survey
                self.main_survey_game_widget.survey = new_survey
                self.main_responses_list.survey = new_survey
                for i in range(8):
                    card = self.display_manager.main_cards[i]
                    card.hide()
                    if i < new_survey.num_responses:
                        card.response = self.main_survey_game_widget.survey.responses[i]
                    else:
                        card.response = None
                self.display_manager.master_score.text = 0
                self.main_total_score_var.set("0")
                self.main_game_frame.grid(row=1, column=0, columnspan=12)
        else:
            self.main_game_frame.grid_forget()
        if new_state == GameState.FAST_MONEY:
            self.selected_fm_response_var.set(0)
            self.display_manager.fm_points.text = 0
            self.fast_money_frame.grid(row=1, column=0, columnspan=12)
        else:
            self.fast_money_frame.grid_forget()
        # Needs to happen here so that the screen behind it is ready
        if current_state == GameState.PREPARING:
            self.display_manager.logo_split.open()
        # Last thing is set new state to current
        self.mode = new_state

    def preparing_mode_change(self, *args):
        # Main Game
        if not self.preparing_mode_var.get():
            self.fm_preparing_frame.grid_forget()
            self.main_preparing_frame.grid(row=1, column=0, columnspan=12)
            self.main_survey_list.reload()
        # Fast Money
        else:
            self.main_preparing_frame.grid_forget()
            self.fm_preparing_frame.grid(row=1, column=0, columnspan=12)
            self.fm_survey_list.reload()
        self.set_display_ids()

    def set_timer_defaults(self):
        self.timer_spin_1.delete(0, END)
        self.timer_spin_1.insert(0, 20)
        self.timer_spin_2.delete(0, END)
        self.timer_spin_2.insert(0, 25)

    def set_main_response_visibility(self, response_index, show):
        current_score = int(self.main_total_score_var.get())
        # TODO: Don't use old val- architect this better
        old_val = self.static_round_number
        if self.mode == GameState.TIEBREAKER:
            self.static_round_number = 3
        if show:
            self.display_manager.main_cards[response_index].reveal()
            current_score += self.static_round_number * self.main_survey_game_widget.survey.responses[
                response_index].count
        else:
            self.display_manager.main_cards[response_index].hide()
            current_score -= self.static_round_number * self.main_survey_game_widget.survey.responses[
                response_index].count
        self.display_manager.master_score.text = str(current_score)
        self.main_total_score_var.set(str(current_score))
        self.static_round_number = old_val

    def fm_timer_toggle(self, *args):
        if self.fm_timer_toggle_button["text"] == "Start":
            self.fm_timer_toggle_button.configure(text="Stop")
            self.root.after(1000, self.timer_tick)
        else:
            self.fm_timer_toggle_button.configure(text="Start")
            self.display_manager.fm_timer.stop_countdown()

    def timer_tick(self, *args):
        if self.display_manager.fm_timer.time == 0:
            self.fm_timer_toggle_button.configure(text="Start")
            return
        if self.fm_timer_toggle_button["text"] == "Start":
            return
        self.display_manager.fm_timer.time -= 1
        self.root.after(1000, self.timer_tick)

    def fm_set_time_1(self, *args):
        self.display_manager.fm_timer.time = self.timer_spin_1.get()

    def fm_set_time_2(self, *args):
        self.display_manager.fm_timer.time = self.timer_spin_2.get()

    def update_fm_visibility(self, *args):
        if self.visibility_var.get() == 0:
            self.display_manager.logo_split.close()
        else:
            self.display_manager.logo_split.open()

    # TODO: change this function to use values of value to determine future state
    def toggle_fm_response(self, index, show, value=None):
        card = self.display_manager.fm_cards[index]
        if show:
            # TODO: do this better
            if not card.response:
                card.response = Response(Survey.NONE, "<Empty>", 0, 0)
            card.given_response = value
            card.reveal_phrase()
        else:
            card.hide()

    # TODO: make hide and show for these guarantee being sequential
    def toggle_fm_count(self, index, show, count=None):
        card = self.display_manager.fm_cards[index]
        if show:
            if not card.response:
                card.response = Response(Survey.NONE, "<Empty>", count, 0)
            else:
                card.response.count = count
            card.update_images()
            card.reveal_value()
            curr_count = int(self.display_manager.fm_points.text)
            self.display_manager.fm_points.text = str(curr_count + count)
        else:
            card.hide()
            card.reveal_phrase()
            curr_count = int(self.display_manager.fm_points.text)
            self.display_manager.fm_points.text = str(curr_count - count)

    def link_to_selected(self, response):
        self.fm_player_responses.set_response(self.selected_fm_response_var.get(), response)

    def update_selected_fm_response(self, *args):
        survey = self.fm_survey_widgets[self.selected_fm_response_var.get() % 5].survey
        self.fm_responses_link.survey = survey
        self.fm_selected_survey_widget.survey = survey


class ResponseWidget(Frame):
    def __init__(self, root, response):
        super().__init__(root, bg=ControlApp.BG_COLOR)
        self._response = response
        self.rank_label = Label(self, text="#X | ", bg=ControlApp.BG_COLOR)
        self.rank_label.grid(row=0, column=0, sticky=W)

        self.columnconfigure(1, weight=1)
        self.phrase_label = Label(self, text="<Empty Response>", bg=ControlApp.BG_COLOR,
                                  justify="left", wraplength=106)
        self.phrase_label.grid(row=0, column=1, sticky=W)

        self.count_label = Label(self, text=" | Count: X", bg=ControlApp.BG_COLOR)
        self.count_label.grid(row=0, column=2)

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


class SurveyWidget(LabelFrame, ABC):
    def __init__(self, root, survey, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        self._survey = survey

    @property
    def survey(self):
        return self._survey

    @survey.setter
    def survey(self, new):
        self._survey = new
        self.update()

    @abstractmethod
    def update(self):
        pass


class SmallSurveyWidget(SurveyWidget):
    def __init__(self, root, survey, **kwargs):
        super().__init__(root, survey, **kwargs)
        Label(self, text="ID: ", bg=ControlApp.BG_COLOR).grid(row=0, column=0)
        self.id_string = StringVar()
        Label(self, textvariable=self.id_string, bg=ControlApp.BG_COLOR).grid(row=0, column=1, sticky=W)
        Label(self, text="Question: ", background=ControlApp.BG_COLOR).grid(row=1, column=0)
        self.question_string = StringVar()
        Label(self, textvariable=self.question_string, bg=ControlApp.BG_COLOR, wraplength=118, justify="left").grid(
            row=1, column=1, sticky=W)
        self.id_string.set(self._survey.id)
        self.question_string.set(self._survey.question)

    def update(self):
        self.id_string.set(str(self._survey.id))
        self.question_string.set(self._survey.question)


class LargeSurveyWidget(SmallSurveyWidget):
    def __init__(self, root, survey, **kwargs):
        super().__init__(root, survey, **kwargs)

        self.response_widgets = []
        Label(self, text="Responses:", bg=ControlApp.BG_COLOR).grid(row=2, column=0,
                                                                    columnspan=2, sticky=W)
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets.append(ResponseWidget(self, self.survey.responses[i]))
            else:
                self.response_widgets.append(ResponseWidget(self, Response(self.survey, "<Empty Response>", 0, i + 1)))
            self.response_widgets[i].grid(row=3 + i, column=0, columnspan=2, sticky=W + E)

    def update(self):
        super().update()
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets[i].response = self.survey.responses[i]
            else:
                self.response_widgets[i].response = Response(self.survey, "<Empty Response>", 0, i + 1)


class MainSurveyResponsesWidget(SurveyWidget):
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
                self.response_widgets.append(ResponseWidget(self, Response(self.survey, "<Empty Response>", 0, i + 1)))
                self.visibility_buttons.append(Button(self, text="Show", bg=ControlApp.BUTTON_COLOR, state=DISABLED,
                                                      command=lambda num=i: self.toggle_button(num)))
            self.response_widgets[i].grid(row=i % 4, column=2 * int(i / 4))
            self.visibility_buttons[i].grid(row=i % 4, column=2 * int(i / 4) + 1)

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
                self.response_widgets[i].response = Response(self.survey, "<Empty Response>", 0, i + 1)
                self.visibility_buttons[i].configure(text="Show", state=DISABLED)
        self.reset()

    def reset(self):
        for i in range(8):
            button = self.visibility_buttons[i]
            if button["text"] == "Hide":
                self.toggle_button(i)


class FastMoneySurveyResponsesWidget(SurveyWidget):
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
                self.response_widgets.append(ResponseWidget(self, Response(self.survey, "<Empty Response>", 0, i + 1)))
                self.link_buttons.append(Button(self, text="Link", bg=ControlApp.BUTTON_COLOR, state=DISABLED,
                                                command=lambda num=i: self.link_response(num)))
            self.response_widgets[i].grid(row=i % 4, column=2 * int(i / 4))
            self.link_buttons[i].grid(row=i % 4, column=2 * int(i / 4) + 1)
        Button(self, text="Unlink", bg=ControlApp.BUTTON_COLOR, command=lambda: self.link_response(-1)).grid(row=4,
                                                                                                             column=0,
                                                                                                             columnspan=4)

    def link_response(self, i):
        if i == -1:
            self.linking_handler(Response(self.survey, "<Empty Response>", 0, 0))
        else:
            self.linking_handler(self.survey.responses[i])

    def update(self):
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_widgets[i].response = self.survey.responses[i]
                self.link_buttons[i].configure(state=NORMAL)
            else:
                self.response_widgets[i].response = Response(self.survey, "<Empty Response>", 0, i + 1)
                self.link_buttons[i].configure(state=DISABLED)


class FastMoneyPlayerResponsesWidget(Frame):
    class ResponseInfo:
        def __init__(self, entry, score_var, response_button, count_button):
            self.entry = entry
            self.score_var = score_var
            self.response_button = response_button
            self.count_button = count_button

    def __init__(self, root, selected_var, toggle_response_command, toggle_count_command, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        Label(self, text="Player 1", bg=ControlApp.BG_COLOR).grid(row=0, column=0)
        Label(self, text="Player 2", bg=ControlApp.BG_COLOR).grid(row=0, column=1)
        left_responses_frame = Frame(self, bg=ControlApp.BG_COLOR, **kwargs)
        left_responses_frame.grid(row=1, column=0, padx=5)
        right_responses_frame = Frame(self, bg=ControlApp.BG_COLOR, **kwargs)
        right_responses_frame.grid(row=1, column=1, padx=5)
        self.toggle_response_command = toggle_response_command
        self.toggle_count_command = toggle_count_command
        self.response_infos = []
        for i in range(10):
            current_frame = None
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
            current_response_button = Button(current_frame, text="Show Response", bg=ControlApp.BUTTON_COLOR,
                                             command=lambda num=i: self.toggle_response_clicked(num))
            current_response_button.grid(row=i % 5, column=3)
            current_count_button = Button(current_frame, text="Show Count", bg=ControlApp.BUTTON_COLOR,
                                          command=lambda num=i: self.toggle_count_clicked(num))
            current_count_button.grid(row=i % 5, column=4)
            self.response_infos.append(
                self.ResponseInfo(current_entry, current_var, current_response_button, current_count_button))

    def set_response(self, i, response):
        self.response_infos[i].score_var.set(str(response.count))

    def toggle_response_clicked(self, i):
        response_info = self.response_infos[i]
        if response_info.response_button["text"] == "Show Response":
            response_info.response_button.configure(text="Hide Response")
            self.toggle_response_command(i, True, response_info.entry.get())
        else:
            response_info.response_button.configure(text="Show Response")
            self.toggle_response_command(i, False)

    def toggle_count_clicked(self, i):
        response_info = self.response_infos[i]
        if response_info.count_button["text"] == "Show Count":
            response_info.count_button.configure(text="Hide Count")
            self.toggle_count_command(i, True, int(response_info.score_var.get()))
        else:
            response_info.count_button.configure(text="Show Count")
            self.toggle_count_command(i, False, int(response_info.score_var.get()))

    def reset(self):
        for i in range(10):
            response_info = self.response_infos[i]
            if response_info.response_button["text"] == "Hide Response":
                self.toggle_response_clicked(i)
            if response_info.count_button["text"] == "Hide Count":
                self.toggle_count_clicked(i)
            response_info.score_var.set("0")


class SurveyList(Frame):
    def __init__(self, root, select_cb, **kwargs):
        super().__init__(root, bg=ControlApp.BG_COLOR, **kwargs)
        Label(self, text="Survey List", bg=ControlApp.BG_COLOR).grid(row=0, column=0, sticky=W)
        self.listbox = Listbox(self)
        self.listbox.grid(row=1, column=0)
        self.listbox.bind("<<ListboxSelect>>", self.clicked)
        self.listbox.configure(activestyle='none')
        self.select_cb = select_cb
        Button(self, text="Reload", command=self.reload, bg=ControlApp.BUTTON_COLOR).grid(row=2, column=0,
                                                                                          sticky=N + S + E + W)
        self.selected = Survey.NONE

    def clicked(self, *args):
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
