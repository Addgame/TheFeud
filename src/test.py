import os
from tkinter import *


class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.list = Listbox(frame)
        self.list.pack()
        for item in ("ONE", "TWO", "THREE", "FOUR"):
            self.list.insert(END, item)

        # menubar = Menu(frame)
        # menubar.add_command(label="Hello!", command=self.hello)
        # menubar.add_command(label="Quit!", command=frame.quit)
        # master.config(menu=menubar)

    def say_hi(self):
        print("hi there, everyone!")

    def hello(self):
        print("hello general")


def hello():
    print("DOOT")


def callback():
    print("called the callback!")


root = Tk()

toolbar = Frame(root)
b = Button(toolbar, text="new", width=6, command=callback)

b.pack(side=LEFT, padx=2, pady=2)
b = Button(toolbar, text="open", width=6, command=callback)

b.pack(side=LEFT, padx=2, pady=2)

toolbar.pack(side=TOP, fill=X)

app = App(root)


def update():
    global counter
    counter = counter + 1
    menu.entryconfig(0, label=str(counter))


scrollframe = Frame(root)
scrollbar = Scrollbar(scrollframe)

scrollbar.pack(side=RIGHT, fill=Y)
listbox = Listbox(scrollframe, yscrollcommand=scrollbar.set)
for i in range(1000):
    listbox.insert(END, str(i))

listbox.pack(side=LEFT, fill=BOTH)

scrollbar.config(command=listbox.yview)

scrollframe.pack()

menubar = Menu(root)
# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=hello)
filemenu.add_command(label="Save", command=hello)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)

menubar.add_cascade(label="File", menu=filemenu)
# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut", command=hello)
editmenu.add_command(label="Copy", command=hello)
editmenu.add_command(label="Paste", command=hello)

menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=hello)

menubar.add_cascade(label="Help", menu=helpmenu)
# POPUP
menu = Menu(root, tearoff=0)
menu.add_command(label="Undo", command=hello)

menu.add_command(label="Redo", command=hello)
# create a canvas
frame = Frame(root, width=512, height=512)

frame.pack()


def popup(event):
    menu.post(event.x_root, event.y_root)


# attach popup to canvas

frame.bind("<Button-3>", popup)

counter = 0

root.config(menu=menubar)
root.title("Test Window")
path = os.path.normpath(os.path.join(os.path.dirname(__file__), r"..\assets\images\icon.png"))
root.iconphoto(True, Image("photo", file=path))
# root.iconphoto(True, Image("photo", file=r".\icon.png"))

root.mainloop()
try:
    root.destroy()  # optional; see description below
except:
    pass
