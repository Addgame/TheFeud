import os.path as path
from tkinter import Tk, Label, Entry, Spinbox, Button, PhotoImage, END
from tkinter.messagebox import askquestion, showerror, showinfo

from survey import Survey


class EditorApp:
    BG_COLOR = "#d9d9d9"
    BUTTON_COLOR = "#dfdfdf"

    def __init__(self, root):
        self.root = root
        # Main Window
        root.geometry("480x240")
        root.title("The Feud Survey Editor")
        root.iconphoto(True, PhotoImage(file=path.realpath(r"..\assets\images\FamilyFeudIcon.png")))
        root.configure(background=self.BG_COLOR)
        # File Name
        Label(root, text="File Name", background=self.BG_COLOR).grid(row=0, column=0)
        self.fn_entry = Entry(root, width=46)
        self.fn_entry.grid(row=0, column=1, columnspan=3, rowspan=1, sticky="W")
        # File Load Button
        Button(root, background=self.BUTTON_COLOR, text="Load", command=self.load, width=16).grid(row=0, column=4)
        # Survey Question
        Label(root, text="Survey Question", background=self.BG_COLOR).grid(row=1, column=0)
        self.sq_entry = Entry(root, width=63)
        self.sq_entry.grid(row=1, column=1, columnspan=4, rowspan=1, sticky="W")
        # Set Up Response Lists
        self.entries = []
        self.spinboxes = []
        # Responses
        for i in range(8):
            label = Label(root, text=str(i + 1), background=self.BG_COLOR)
            entry = Entry(root, width=25)
            self.entries.append(entry)
            spinbox = Spinbox(root, width=3, from_=1, to=100)
            self.spinboxes.append(spinbox)
            if i < 4:
                label.grid(row=3 + i, column=0, sticky="W", padx=14)
                entry.grid(row=3 + i, column=0, columnspan=2, sticky="E")
                spinbox.grid(row=3 + i, column=2, sticky="W")
            else:
                label.grid(row=3 + (i - 4), column=3, sticky="W", padx=8)
                entry.grid(row=3 + (i - 4), column=3, columnspan=2, padx=25, sticky="W")
                spinbox.grid(row=3 + (i - 4), column=4, padx=18, sticky="E")
        # Save and Clear Buttons
        Button(root, text="Save", command=self.save, background=self.BUTTON_COLOR, width=16).grid(row=8, column=1)
        Button(root, text="Clear", command=self.clear, background=self.BUTTON_COLOR, width=16).grid(row=8, column=3)
        # Set Up Rows and Columns
        for i in range(10):
            root.grid_rowconfigure(i, weight=1, uniform="all")
        for i in range(5):
            root.grid_columnconfigure(i, weight=1, uniform="col")

    def load(self):
        if not self.validate_filename():
            return
        # Warn of risk of overwriting
        ret = askquestion("Confirm Action",
                          "This will overwrite the current values in the editor. Are you sure you want to continue?")
        if ret == "no":
            return
        # Attempt load survey from file
        if not Survey.load_survey_file(path.realpath(r"..\surveys\\" + self.fn_entry.get() + ".survey")):
            showerror("Error", "Could not load the survey from given filename")
            return
        survey = Survey.get_surveys()[0]
        Survey.clear_surveys()
        # Get question from survey
        self.sq_entry.delete(0, END)
        self.sq_entry.insert(0, survey.question)
        # Get responses and counts from survey
        for i in range(8):
            self.entries[i].delete(0, END)
            self.spinboxes[i].delete(0, END)
            if i < survey.num_responses:
                current_response = survey.responses[i]
                self.entries[i].insert(0, current_response.phrase)
                self.spinboxes[i].insert(0, str(current_response.count))
            else:
                self.spinboxes[i].insert(0, "1")

    def save(self):
        if not self.validate_filename():
            return
        # Fill in survey data and get survey
        survey_dict = {"question": self.sq_entry.get(), "responses": []}
        prev_count = 100
        for i in range(8):
            try:
                current_response = self.entries[i].get()
                current_count = int(self.spinboxes[i].get())
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
        filepath = path.realpath(r"..\surveys\\" + self.fn_entry.get() + ".survey")
        if path.exists(filepath):
            ret = askquestion("Confirm Action",
                              "Saving this will overwrite an existing file. Are you sure you want to continue?")
            if ret == "no":
                return
        survey.save_to_file(filepath)
        showinfo("Notice", "Save successful")

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
            self.entries[i].delete(0, END)
            self.spinboxes[i].delete(0, END)
            self.spinboxes[i].insert(0, "1")


if __name__ == '__main__':
    master = Tk()
    EditorApp(master)
    master.mainloop()
