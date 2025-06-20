from tkinter import *


class Auto_param_interface(Frame):
    """ This is a small Frame in which the user can define the nomber of targets per arena, in the case the number is variable between arenas."""
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        Grid.rowconfigure(parent,0,weight=1)
        Grid.columnconfigure(parent, 0, weight=1)
        parent.grab_set()  # Prevents interaction with other windows
        parent.focus_set()  # Sets keyboard focus to this window

        self.grid(sticky="nsew")

        Grid.rowconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        #Image to show results
        Image_can=Canvas(self, background="blue")
        Image_can.grid(row=0,column=0, rowspan=2, sticky="nsew")

        #Parameters
        Image_param=Frame(self, background="red")
        Image_param.grid(row=0,column=1, sticky="nsew")
        Label(Image_param, text="Parameters").grid(row=0, column=0, sticky="nsew")

        #List of videos
        Video_list=Frame(self, background="purple")
        Video_list.grid(row=1,column=1, sticky="nsew")
        Label(Video_list, text="Videos").grid(row=0, column=0, sticky="nsew")

        print("Verif")





