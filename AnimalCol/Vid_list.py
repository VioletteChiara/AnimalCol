import tkinter as tk
import numpy as np
from tkinter import *

class Interface_vid_list(tk.Frame):
    def __init__(self, parent, list_vids, on_confirm=None):
        super().__init__(parent)
        self.parent = parent
        self.list_vids = list_vids
        self.check_vars = []
        self.selected_indices = []
        self.on_confirm = on_confirm

        Grid.rowconfigure(self.parent,0,weight=1)
        Grid.columnconfigure(self.parent, 0, weight=1)

        Grid.rowconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=10000)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.rowconfigure(self, 4, weight=1)
        Grid.columnconfigure(self, 0, weight=10000)
        Grid.columnconfigure(self, 1, weight=1)

        self.grid(sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Select images to delete:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2)

        select_all_btn = Button(self, text="Select All", command=self.select_all)
        select_all_btn.grid(row=1, column=0, columnspan=2)

        # === Scrollable Area ===
        canvas = tk.Canvas(self, height=300)
        scrollbar = Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(sticky="nsew", row=2, column=0)
        scrollbar.grid(sticky="ns", row=2, column=1)

        # === Checkboxes ===
        for i, vid in enumerate(self.list_vids):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(scroll_frame, text=vid, variable=var, anchor="w")
            chk.grid()
            self.check_vars.append(var)


        # === Confirm Button ===
        confirm_btn = Button(self, text="Validate Selection", command=self.confirm_selection, background="green")
        confirm_btn.grid(row=3, column=0, columnspan=2)

    def select_all(self):
        nb_ok=np.sum([val.get() for val in self.check_vars])
        if nb_ok==len(self.check_vars):
            state=False
        else:
            state=True

        for var in self.check_vars:
            var.set(state)



    def confirm_selection(self):
        self.selected_indices = [i for i, var in enumerate(self.check_vars) if var.get()]
        print("Selected indices:", self.selected_indices)
        if self.on_confirm:
            self.on_confirm(self.selected_indices)
        self.parent.destroy()
