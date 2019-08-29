import os.path as path
from abc import ABC, abstractmethod
from tkinter import Tk, PhotoImage, LabelFrame, Label, Radiobutton, IntVar, StringVar, N, S, E, W, DISABLED, NORMAL, \
    Entry, Frame
from tkinter.messagebox import askquestion

import pygame

from constants import GameState
from display import GraphicsManager
from survey import Survey


class ControlApp:
    BG_COLOR = "#d9d9d9"
    BUTTON_COLOR = "#dfdfdf"

    PREPARING_MAIN, PREPARING_FM = range(2)

    def __init__(self, root):
        self.root = root
        # Main Window
        root.geometry("800x800")
        root.title("The Feud Game Control")
        root.iconphoto(True, PhotoImage(file=path.realpath(r"..\assets\images\icon.png")))
        root.configure(background=self.BG_COLOR)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        for i in range(12):
            root.grid_columnconfigure(i, weight=1, uniform="root_grid")

        # Setup display
        self.display_manager = GraphicsManager()
        self.root.after(0, self.display_callback)

        # Mode Selection (the game state)
        self.mode = GameState.LOGO
        mode_frame = LabelFrame(root, text="Mode", bg=self.BG_COLOR, width=100, height=100)
        self.mode_var = IntVar(value=0)
        self.mode_var.trace_add("write", self.mode_change)
        self.mode_buttons = []
        for state in GameState:
            rb = Radiobutton(mode_frame, text=str(state), bg=self.BUTTON_COLOR, indicator=0, padx=19, value=state.value,
                             variable=self.mode_var, state=DISABLED if 1 <= state.value <= 6 else NORMAL)
            rb.grid(row=0, column=state.value, padx=2, pady=2, sticky=N + S + E + W)
            self.mode_buttons.append(rb)
            mode_frame.grid_columnconfigure(state.value, weight=1, uniform="mode_buttons")
        mode_frame.grid(row=0, column=0, padx=10, columnspan=12)

        # Preparing
        self.preparing_mode = IntVar(value=0)
        self.preparing_mode.trace_add("write", self.preparing_mode_change)
        self.preparing_selector = LabelFrame(root, text="Preparing Mode", bg=self.BG_COLOR)
        Radiobutton(self.preparing_selector, text="Main Game", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=0,
                    variable=self.preparing_mode).grid(row=0, column=0, padx=2, pady=2)
        self.preparing_selector.grid_columnconfigure(0, weight=1, uniform="prepare_buttons")
        Radiobutton(self.preparing_selector, text="Fast Money", bg=self.BUTTON_COLOR, indicator=0, padx=10, value=1,
                    variable=self.preparing_mode).grid(row=0, column=1, padx=2, pady=2)
        self.preparing_selector.grid_columnconfigure(1, weight=1, uniform="prepare_buttons")
        self.preparing_selector.grid(row=1, column=0, padx=10, columnspan=4, sticky=W)
        self.name_1_frame = LabelFrame(root, text="Team 1 Name", bg=self.BG_COLOR)
        self.name_1_entry = Entry(self.name_1_frame, width=30)
        self.name_1_entry.grid(padx=2, pady=2)
        self.name_1_frame.grid(row=1, column=6, columnspan=3)
        self.name_2_frame = LabelFrame(root, text="Team 2 Name", bg=self.BG_COLOR)
        self.name_2_entry = Entry(self.name_2_frame, width=30)
        self.name_2_entry.grid(padx=2, pady=2)
        self.name_2_frame.grid(row=1, column=9, columnspan=3)

        # TESTING
        sw = LargeSurveyWidget(root, Survey({}))
        sw.grid(row=2, column=0, padx=10, columnspan=3)
        sw.survey = Survey.load_survey_file(r"..\surveys\Bethlehem Food.survey")
        self.display_manager.id_display.text = sw.survey.id
        # sw.grid_forget()

    def update_gui(self):
        pass

    def display_callback(self):
        pygame.event.pump()
        self.display_manager.update_display(self.mode)
        self.root.after(5, self.display_callback)

    def on_close(self):
        ret = askquestion("Confirm Action", "Are you sure you want to close the game?")
        if ret == "yes":
            self.root.destroy()

    def mode_change(self, *args):
        print(self.mode_var.get())
        current_state = self.mode
        new_state = GameState(self.mode_var.get())
        # Don't do anything if we aren't actually changing state
        if current_state == new_state:
            return
        if current_state == GameState.LOGO:
            self.display_manager.logo_split.open()
        if new_state == GameState.LOGO:
            self.display_manager.logo_split.close()
        # Last thing is set new state to current
        self.mode = new_state

    def preparing_mode_change(self, *args):
        pass

    def blank(self):
        pass


class ResponseWidget(Frame):
    def __init__(self, root, response):
        super().__init__(root, bg=ControlApp.BG_COLOR)
        self._response = response

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, new):
        self._response = new
        self.update()

    def update(self):
        pass


class SurveyWidget(LabelFrame, ABC):
    def __init__(self, root, survey):
        super().__init__(root, text="Survey", bg=ControlApp.BG_COLOR)
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
    def __init__(self, root, survey):
        super().__init__(root, survey)
        Label(self, text="ID: ", bg=ControlApp.BG_COLOR).grid(row=0, column=0)
        self.id_string = StringVar()
        Label(self, textvariable=self.id_string, bg=ControlApp.BG_COLOR).grid(row=0, column=1, sticky=W)
        Label(self, text="Question: ", background=ControlApp.BG_COLOR).grid(row=1, column=0)
        self.question_string = StringVar()
        Label(self, textvariable=self.question_string, bg=ControlApp.BG_COLOR, wraplength=118, justify="left").grid(
            row=1, column=1, sticky=W)
        self.update()

    def update(self):
        self.id_string.set(self._survey.id)
        self.question_string.set(self._survey.question)


class LargeSurveyWidget(SmallSurveyWidget):
    def __init__(self, root, survey):
        super().__init__(root, survey)

        self.response_strings = []
        self.count_strings = []
        Label(self, text="Responses: ", bg=ControlApp.BG_COLOR).grid(row=2, column=0, columnspan=2, sticky=W)
        for i in range(8):
            Label(self, text=str(i + 1) + " | ", bg=ControlApp.BG_COLOR).grid(row=3 + i, column=0, sticky=W)
            self.response_strings.append(StringVar())
            Label(self, textvariable=self.response_strings[i], bg=ControlApp.BG_COLOR, wraplength=80,
                  justify="left").grid(row=3 + i, column=0, sticky=W)
            Label(self, text=" |     ", bg=ControlApp.BG_COLOR).grid(row=3 + i, column=1, sticky=E)
            self.count_strings.append(StringVar())
            Label(self, textvariable=self.count_strings[i], bg=ControlApp.BG_COLOR).grid(row=3 + i, column=1, sticky=E)
        self.update()

    def update(self):
        super().update()
        for i in range(8):
            if i < self.survey.num_responses:
                self.response_strings[i].set(self.survey.responses[i].phrase)
                self.count_strings[i].set(str(self.survey.responses[i].count))


if __name__ == '__main__':
    pygame.init()

    # Set up tkinter and start looping
    master = Tk()
    ControlApp(master)
    master.mainloop()

    pygame.quit()
