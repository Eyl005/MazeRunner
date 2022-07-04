import tkinter as tk
from tkinter import Frame, Label, Button


class ButtonsFrame(Frame) :
    def __init__(self, parent) :
        Frame.__init__(self, parent.root)
        b1 = Button(self, text= "A")
        b2 = Button(self, text = "B")
        b1.pack(side=tk.LEFT,   expand=1)
        b1.config(background='green')
        b2.pack(side=tk.LEFT)
class MainWindow(object) :
    def __init__(self, root) :
        self.root = root
        Label(root, text="Buttons").pack()
        bf = ButtonsFrame(self)
        bf.pack(fill="x",expand=1)

root = tk.Tk()
bf = MainWindow(root)
root.mainloop()