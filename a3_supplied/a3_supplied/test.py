import tkinter as tk
from tkinter import ttk


class NameInputBox:
    entry_value = 'Empty String'

    def __init__(self, text):
        self.window = tk.Toplevel()
        self.window.wm_title("Input Name.")

        self.label = tk.Label(self.window, text=text)
        self.label.pack(side='top')

        self.frame = ttk.Frame(self.window)
        self.frame.pack(side='bottom')

        self.entry = ttk.Entry(self.frame)
        self.entry.pack(side='left')

        self.button = ttk.Button(self.frame, text="Ok",
                                 command=self.name_input_box_exit)
        self.button.pack(side='left')

    def name_input_box_exit(self):
        # get value from widget and assign to variable
        self.entry_value = self.entry.get()

        self.window.destroy()


class MainWindow:
    def __init__(self):
        self.window = tk.Tk()

        self.label = tk.Label(self.window)
        self.label.pack()

        self.button = ttk.Button(self.window, text="Name",
                                 command=self.ask_name)
        self.button.pack()

        # the only `mainloop` in all code
        self.window.mainloop()

    def ask_name(self):
        # show Toplevel
        self.box = NameInputBox('Input the Name:')

        # set it modal (to wait for value)
        self.box.window.focus_set()  # take over input focus,
        self.box.window.grab_set()  # disable other windows while I'm open,
        self.box.window.wait_window()  # and wait here until win destroyed

        # get value from Toplevel
        self.label['text'] = self.box.entry_value


MainWindow()