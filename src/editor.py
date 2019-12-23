import os.path as path
from os import makedirs
from tkinter import Tk, Label, Entry, Spinbox, Button, PhotoImage, END, Frame
from tkinter.messagebox import askquestion, showerror, showinfo

from src.survey import Survey, SURVEY_DIR

ICON_DIR = r"assets/images/"


class EditorApp:
    BG_COLOR = "#d9d9d9"
    BUTTON_COLOR = "#dfdfdf"

    def __init__(self, root):
        self.root = root
        # Main Window Config
        root.geometry("480x240")
        root.title("The Feud Survey Editor")
        root.iconphoto(True, PhotoImage(file=path.realpath(ICON_DIR + r"/icon.png")))
        root.configure(background=self.BG_COLOR)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        # File Name
        Label(root, text="File Name", background=self.BG_COLOR).grid(row=0, column=0, columnspan=2)
        self.fn_entry = Entry(root, width=43)
        self.fn_entry.grid(row=0, column=2, columnspan=6, rowspan=1, sticky="W")
        # File Load Button
        Button(root, background=self.BUTTON_COLOR, text="Load", command=self.load, width=16).grid(row=0, column=8,
                                                                                                  columnspan=2)
        # Survey Question
        Label(root, text="Survey Question", background=self.BG_COLOR).grid(row=1, column=0, columnspan=2)
        self.sq_entry = Entry(root, width=63)
        self.sq_entry.grid(row=1, column=2, columnspan=8, rowspan=1, sticky="W")
        # Set Up Response List
        self.responses = []
        # Responses
        for i in range(8):
            widget = ResponseEntryWidget(root, i + 1)
            if i < 4:
                sticky = "W"
            else:
                sticky = "E"
            widget.grid(row=(i % 4) + 3, column=5 * int(i / 4), columnspan=5, sticky=sticky)
            self.responses.append(widget)
        # Save and Clear Buttons
        Button(root, text="Save", command=self.save, background=self.BUTTON_COLOR, width=16).grid(row=8, column=2,
                                                                                                  columnspan=2)
        Button(root, text="Clear", command=self.clear, background=self.BUTTON_COLOR, width=16).grid(row=8, column=6,
                                                                                                    columnspan=2)
        # Set Up Rows and Columns
        for i in range(10):
            root.grid_rowconfigure(i, weight=1, uniform="all")
            root.grid_columnconfigure(i, weight=1, uniform="col")

    def on_close(self):
        ret = askquestion("Confirm Action", "Are you sure you want to close the editor?")
        if ret == "yes":
            self.root.destroy()

    def load(self):
        if not self.validate_filename():
            return
        # Warn of risk of overwriting
        edited = False
        if self.sq_entry.get():
            edited = True
        else:
            for i in range(8):
                if self.responses[i].entry.get() or self.responses[i].spinbox.get() != "1":
                    edited = True
                    break
        if edited:
            ret = askquestion("Confirm Action",
                              "This will overwrite the current values in the editor. Are you sure you want to continue?")
            if ret == "no":
                return
        # Attempt load survey from file
        survey = Survey.load_survey_file(path.realpath(SURVEY_DIR + self.fn_entry.get() + ".survey"))
        if not survey:
            showerror("Error", "Could not load the survey from given filename")
            return
        # Want to be able to load again if another program edits the survey file
        Survey.clear_surveys()
        # Get question from survey
        self.sq_entry.delete(0, END)
        self.sq_entry.insert(0, survey.question)
        # Get responses and counts from survey
        for i in range(8):
            self.responses[i].entry.delete(0, END)
            self.responses[i].spinbox.delete(0, END)
            if i < survey.num_responses:
                current_response = survey.responses[i]
                self.responses[i].entry.insert(0, current_response.phrase)
                self.responses[i].spinbox.insert(0, str(current_response.count))
            else:
                self.responses[i].spinbox.insert(0, "1")
        # Tell the survey ID
        showinfo("Notice", "Loaded survey with ID: {}".format(survey.id))

    def save(self):
        if not self.validate_filename():
            return
        # Fill in survey data and get survey
        survey_dict = {"question": self.sq_entry.get(), "responses": []}
        if not self.sq_entry.get():
            showerror("Error", "A survey question is required. Did not save.")
            return
        prev_count = 100
        for i in range(8):
            try:
                current_response = self.responses[i].entry.get()
                current_count = int(self.responses[i].spinbox.get())
                if not 1 <= current_count <= 100:
                    raise ValueError
                if current_response:
                    if prev_count == -1:
                        showerror("Error", "Response number " + str(i) + " was blank but response number " + str(
                            i + 1) + " existed. Did not save.")
                        return
                    if current_count > prev_count:
                        showerror("Error",
                                  "Response number " + str(i) + " had a smaller count than response number " + str(
                                      i + 1) + ". Responses should be ordered by response count. Did not save.")
                        return
                    prev_count = current_count
                else:
                    prev_count = -1
                    continue
                survey_dict["responses"].append(
                    {"response": current_response, "count": current_count})
            except ValueError:
                showerror("Error", "Count for response number " + str(
                    i + 1) + " was invalid (should be integer from 1 to 100). Did not save.")
                return
        survey = Survey(survey_dict)
        # Confirm overwrite and save
        if not path.exists(SURVEY_DIR):
            makedirs(SURVEY_DIR)
        filepath = path.realpath(SURVEY_DIR + self.fn_entry.get() + ".survey")
        if path.exists(filepath):
            ret = askquestion("Confirm Action",
                              "Saving this will overwrite an existing file. Are you sure you want to continue?")
            if ret == "no":
                return
        if survey.save_to_file(filepath):
            showinfo("Notice", "Successfully saved survey with ID: {}".format(survey.id))
        else:
            showerror("Error", "Could not save survey")

    def validate_filename(self):
        # Validate filename
        filename = self.fn_entry.get()
        if not filename:
            showerror("Error", "No filename was provided")
            return False
        if "." in filename:
            showerror("Error", "Filename may not contain \".\"")
            return False
        return True

    def clear(self):
        # Confirm intended action
        ret = askquestion("Confirm Action",
                          "This will clear all values in the editor. Are you sure you want to continue?")
        if ret == "no":
            return
        # Clear all values
        self.fn_entry.delete(0, END)
        self.sq_entry.delete(0, END)
        for i in range(8):
            self.responses[i].entry.delete(0, END)
            self.responses[i].spinbox.delete(0, END)
            self.responses[i].spinbox.insert(0, "1")


class ResponseEntryWidget(Frame):
    def __init__(self, root, response_number):
        super().__init__(root, bg=EditorApp.BG_COLOR)
        Label(self, text=str(response_number), bg=EditorApp.BG_COLOR).grid(row=0, column=0)
        self.entry = Entry(self, width=30)
        self.entry.grid(row=0, column=1)
        self.spinbox = Spinbox(self, width=3, from_=1, to=100)
        self.spinbox.grid(row=0, column=2)


if __name__ == '__main__':
    master = Tk()
    EditorApp(master)
    master.mainloop()
