from tkinter import *
import pyautogui
from tkinter import filedialog
import numpy as np
import cv2
import PIL.Image, PIL.ImageTk
import math
import csv
import Functions_find_red as Fun
import os
import pickle
import Loading
import display_colors
import imghdr


class Interface(Frame):
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=0, height=0, bd=5, **kwargs)
        self.grid()

        #image de saturation:
        self.saturations=display_colors.create_all_sat()
        self.values = display_colors.create_all_val()

        self.which_tool = "Target"  # "Scale_R","Scale_B","Scale_Y","Fish","Red"
        self.tool_size = 50
        self.pt_selected = None
        self.ratio = 0.25
        self.angle1 = 0
        self.angle2 = 0
        self.SizeMin = [10, 10]
        self.Images = []
        self.pt_Poly = []
        self.tool_type = StringVar()
        self.tool_type.set("Pencil")
        self.tool_add = IntVar()
        self.tool_add.set(1)

        #No images yet
        self.Images_names = []


        # Canvas:
        # Barre de titre
        self.canvas_title_bar = Canvas(fenetre, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_title_bar.grid(row=0, column=0, columnspan=3, sticky=(N, S, E, W))
        self.canvas_title_bar.columnconfigure(0, weight=1)
        self.canvas_title_bar.columnconfigure(1, weight=1)
        self.canvas_title_bar.columnconfigure(2, weight=100)
        self.canvas_title_bar.columnconfigure(3, weight=1)
        self.canvas_title_bar.columnconfigure(4, weight=1)
        self.canvas_title_bar.bind("<Button-1>", self.press_fenetre)
        self.canvas_title_bar.bind("<B1-Motion>", self.move_fenetre)

        # Visualisation de la video et barre de temps
        self.canvas_main = Canvas(fenetre, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_main.grid(row=1, column=0, sticky="ns")

        self.canvas_main_img = Canvas(self.canvas_main, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_main_img.grid(row=0, column=0, sticky="ns")

        self.canvas_main_but = Canvas(self.canvas_main, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_main_but.grid(row=1, column=0, sticky="ns")

        self.Image_prec = Button(self.canvas_main_but, text="Previous frame", state="disabled", command=self.precedant)
        self.Image_prec.grid(row=0, column=0, sticky="e")

        self.Image_suiv = Button(self.canvas_main_but, text="Next frame", command=self.suivant)
        self.Image_suiv.grid(row=0, column=1, sticky="w")


        # Right pannel
        self.canvas_user = Canvas(fenetre, height=100, width=100, bd=2, highlightthickness=1, relief='flat')
        self.canvas_user.grid(row=1, column=1, sticky="ns")
        self.canvas_user.rowconfigure(0, weight=1)
        self.canvas_user.rowconfigure(1, weight=1)
        self.canvas_user.rowconfigure(2, weight=1)
        self.canvas_user.rowconfigure(3, weight=1)
        self.canvas_user.rowconfigure(4, weight=1)

        # Widgets:
        # Barre de titre
        self.Nom_Logiciel = Label(self.canvas_title_bar, fg="white", text="ColCal", bg="purple",
                                  font=("courier new", 12))
        self.Nom_Logiciel.grid(row=0, column=0, sticky="w")

        self.position_mouse = StringVar()
        self.position_mouse.set("x=0, y=0")
        self.position_mouse_lab = Label(self.canvas_title_bar, textvariable=self.position_mouse)
        self.position_mouse_lab.grid(row=0, column=1, sticky="we")

        self.bouton_New = Button(self.canvas_title_bar, text="Add Images", command=self.open_new_seq)
        self.bouton_New.grid(row=0, column=2, sticky="e")

        self.bouton_Open = Button(self.canvas_title_bar, text="Open file", command=self.open_file)
        self.bouton_Open.grid(row=0, column=3, sticky="e")

        self.bouton_Save = Button(self.canvas_title_bar, text="Save", command=self.save)
        self.bouton_Save.grid(row=0, column=4, sticky="e")

        self.bouton_Save_Particles = Button(self.canvas_title_bar, text="Export particles", command=self.save_particles)
        self.bouton_Save_Particles.grid(row=0, column=5, sticky="e")

        self.bouton_Fermer = Button(self.canvas_title_bar, text="X", fg="white", bg="red", command=self.fermer)
        self.bouton_Fermer.grid(row=0, column=6, sticky="e")

        # Visualisation de la video
        self.canvas_main_img.bind("<Button-1>", self.callback_mask)
        self.canvas_main_img.bind("<B1-Motion>", self.move_pt_mask)
        self.canvas_main_img.bind("<ButtonRelease - 1>", self.end_move)

        self.canvas_main_img.bind("<Button-3>", self.callback_mask_R)
        self.canvas_main_img.bind("<B3-Motion>", self.move_pt_mask_R)
        self.canvas_main_img.bind("<ButtonRelease - 3>", self.end_move)


        self.canvas_main_img.bind("<Motion>", self.affiche_mouse)
        self.canvas_main_img.bind("<space>", self.Change_add)

        # Right pannel
        # Visualisation du blanc
        Frame_ratio=Frame(self.canvas_user)
        Frame_ratio.grid(row=0, column=0, columnspan=3)

        Label(Frame_ratio, text="Ratio").grid(row=0, column=0)
        self.distance=StringVar()
        Entry(Frame_ratio, textvariable=self.distance).grid(row=0, column=1)


        Frame_show_col=Frame(self.canvas_user)
        Frame_show_col.grid(row=1, column=0, columnspan=3)

        Color_selection=Frame(Frame_show_col, highlightthickness=5, highlightbackground="#9d9aff", relief="solid")
        Color_selection.grid(row=0, column=0, sticky="nsew")

        Label(Color_selection, text="Color selection", font=("Helvetica", 15), background="#9d9aff").grid(row=0, column=0, columnspan=3, sticky="nsew")

        Label(Color_selection, text="Colors", font=("Helvetica", 12)).grid(row=1, column=0)
        self.canvas_img_couleurs = Canvas(Color_selection, width=10, height=10, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_couleurs.grid(row=2, column=0, sticky="ns")
        self.img_colors = cv2.imread("Colors.png")
        Size = self.img_colors.shape
        self.ratio_col = 0.5
        self.img_colors_new = cv2.cvtColor(self.img_colors, cv2.COLOR_BGR2RGB)
        self.TMP_img_col = cv2.resize(self.img_colors_new,
                                      (int(Size[1] * self.ratio_col), int(Size[0] * self.ratio_col)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)
        self.canvas_img_couleurs.bind("<Button-1>", self.move_col)
        self.canvas_img_couleurs.bind("<B1-Motion>", self.drag_col)

        Label(Color_selection, text="Saturation", font=("Helvetica", 12)).grid(row=1, column=1)
        self.canvas_img_sat=Canvas(Color_selection, width=20, height=100, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_sat.grid(row=2, column=1, sticky="sn")
        self.canvas_img_sat.bind("<Button-1>",self.move_sat)
        self.canvas_img_sat.bind("<B1-Motion>", self.drag_sat)

        Label(Color_selection, text="Value", font=("Helvetica", 12)).grid(row=1, column=2)
        self.canvas_img_val=Canvas(Color_selection, width=20, height=100, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_val.grid(row=2, column=2, sticky="sn")
        self.canvas_img_val.bind("<Button-1>",self.move_val)
        self.canvas_img_val.bind("<B1-Motion>", self.drag_val)

        self.canvas_choice_couleurs = Canvas(self.canvas_user, width=10, height=10, bd=0, highlightthickness=0,relief='flat')
        self.canvas_choice_couleurs.grid(row=2, column=0, sticky="ns")

        self.hue_name = Label(self.canvas_choice_couleurs, text="Hue:")
        self.hue_name.grid(row=0, column=0, sticky="e")
        self.hue_bot = Entry(self.canvas_choice_couleurs)
        self.hue_bot.bind("<Return>",self.update_show)
        self.hue_bot.grid(row=0, column=1)
        self.hue_top = Entry(self.canvas_choice_couleurs)
        self.hue_top.grid(row=0, column=2)
        self.hue_top.bind("<Return>", self.update_show)

        self.sat_name = Label(self.canvas_choice_couleurs, text="Saturation:")
        self.sat_name.grid(row=1, column=0, sticky="e")
        self.sat_bot = Entry(self.canvas_choice_couleurs)
        self.sat_bot.grid(row=1, column=1)
        self.sat_bot.bind("<Return>", self.update_show)
        self.sat_top = Entry(self.canvas_choice_couleurs)
        self.sat_top.grid(row=1, column=2)
        self.sat_top.bind("<Return>", self.update_show)

        self.val_name = Label(self.canvas_choice_couleurs, text="Value:")
        self.val_name.grid(row=2, column=0, sticky="e")
        self.val_bot = Entry(self.canvas_choice_couleurs)
        self.val_bot.grid(row=2, column=1)
        self.val_bot.bind("<Return>", self.update_show)
        self.val_top = Entry(self.canvas_choice_couleurs)
        self.val_top.grid(row=2, column=2)
        self.val_top.bind("<Return>", self.update_show)


        self.bouton_Valider = Button(self.canvas_choice_couleurs, text="Valider", fg="white", bg="green",
                                     command=self.validate)
        self.bouton_Valider.grid(row=2, column=3, sticky="e")

        self.bouton_Valider_all = Button(self.canvas_choice_couleurs, text="Valider tout", fg="white", bg="red",
                                         command=self.validate_all)
        self.bouton_Valider_all.grid(row=2, column=4, sticky="e")

        self.hue_bot.delete(0, END)
        self.hue_bot.insert(0, "0")
        self.hue_top.delete(0, END)
        self.hue_top.insert(0, "360")

        self.sat_bot.delete(0, END)
        self.sat_bot.insert(0, "0")
        self.sat_top.delete(0, END)
        self.sat_top.insert(0, "255")

        self.val_bot.delete(0, END)
        self.val_bot.insert(0, "0")
        self.val_top.delete(0, END)
        self.val_top.insert(0, "255")

        self.Can_Tool_param = Canvas(self.canvas_user, height=20, bd=2, highlightthickness=1, relief='flat')
        self.Can_Tool_param.grid(row=3, column=0, sticky="ns")

        self.scale_tool_size = Scale(self.Can_Tool_param, label="Tool size", from_=3, to=500, resolution=1,
                                     orient=HORIZONTAL, length=200, command=self.Change_tool_size)
        self.scale_tool_size.grid(row=0, column=2)
        self.scale_tool_size.set(50)

        self.Add = Radiobutton(self.Can_Tool_param, text="Add", indicatoron=0, width=10, variable=self.tool_add,
                               value=1, command=lambda: self.Change_add(True))

        self.Remove = Radiobutton(self.Can_Tool_param, text="Remove", indicatoron=0, width=10, variable=self.tool_add, value=0, command=lambda: self.Change_add(False))

        self.Add.grid(row=0, column=0, sticky="s")
        self.Remove.grid(row=0, column=1, sticky="s")

        self.Pencil_butt = Radiobutton(self.Can_Tool_param, text="Pencil", indicatoron=1, width=10,
                                       variable=self.tool_type, value="Pencil")
        self.Poly_butt = Radiobutton(self.Can_Tool_param, text="Polygon", indicatoron=1, width=10,
                                     variable=self.tool_type, value="Poly")

        self.Pencil_butt.grid(row=1, column=0, sticky="s")
        self.Poly_butt.grid(row=1, column=1, sticky="s")

        self.Can_Tool_Choice = Frame(self.canvas_user, height=20, bd=2, highlightthickness=1, relief='flat')
        self.Can_Tool_Choice.grid(row=4, column=0, sticky="ns")

        self.which_tool = StringVar()
        self.which_tool.set("Target")  # "Fish", "Scale_R","Scale_B","Scale_Y","Scale_W",

        self.tool_Fish = Radiobutton(self.Can_Tool_Choice, text="Target", indicatoron=0, width=10,
                                     variable=self.which_tool, value="Target")

        self.tool_Scale_R = Radiobutton(self.Can_Tool_Choice, text="Red ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Red")

        self.tool_Scale_B = Radiobutton(self.Can_Tool_Choice, text="Blue ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Blue")

        self.tool_Scale_Y = Radiobutton(self.Can_Tool_Choice, text="Yellow ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Yellow")

        self.tool_Scale_W = Radiobutton(self.Can_Tool_Choice, text="White ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="White")

        self.tool_Fish.grid(row=0, column=0)
        self.tool_Scale_R.grid(row=0, column=1)
        self.tool_Scale_B.grid(row=0, column=2)
        self.tool_Scale_Y.grid(row=0, column=3)
        self.tool_Scale_W.grid(row=0, column=4)

        self.Can_Miniature = Canvas(self.canvas_user, height=20, bd=2, highlightthickness=1, relief='groove')
        self.Can_Miniature.grid(row=5, column=0, sticky="ns")

        self.Can_Miniature_img = Canvas(self.Can_Miniature, height=20, bd=2, highlightthickness=1, relief='flat')
        self.Can_Miniature_img.grid(row=0, column=0, sticky="ns")
        self.Can_Miniature_img.bind("<Button-1>", self.callback_miniature)
        self.Can_Miniature_img.bind_all("<MouseWheel>", self.On_mousewheel)

        self.canvas_main_img.focus_force()

        self.defilement = IntVar()
        self.defilement.set(250)
        self.scale_tool_size = Scale(self.Can_Miniature, showvalue=0, from_=250, to=self.SizeMin[0] - 1, resolution=1, variable=self.defilement, orient=VERTICAL, length=250, command=self.defile)
        self.scale_tool_size.grid(row=0, column=1)
        self.scale_tool_size.set(250)

        self.update_min = Button(self.Can_Miniature, text="Update_view", command=self.afficher_min)
        self.update_min.grid(row=1, column=0)

        Selected_color=Frame(Frame_show_col, highlightthickness=5, highlightbackground="#9affb9", relief="solid")
        Selected_color.grid(row=0, column=1, sticky="nse")

        Label(Selected_color,text="Selected colors", font=("Helvetica", 15), background="#9affb9").grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.canvas_img_saturation_value=Canvas(Selected_color, width=100, height=100, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_saturation_value.grid(row=2, column=0)

        self.canvas_img_hue=Canvas(Selected_color, width=20, height=100, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_hue.grid(row=2, column=1)

        Grid.rowconfigure(Selected_color, 0, weight=1)
        Grid.rowconfigure(Selected_color, 1, weight=50)
        Grid.rowconfigure(Selected_color, 2, weight=500)

        self.shown_col=[int(self.hue_bot.get()),0]
        self.shown_sat = [int(self.sat_bot.get()), 0]
        self.shown_val = [int(self.val_bot.get()), 0]
        self.update_show()


    def On_mousewheel(self,event):
        if len(self.Images)>0:
            if event.widget == self.Can_Miniature_img:
                new_pos=self.defilement.get() - (event.delta / 10)
                if new_pos > 250 and new_pos <self.SizeMin[0]:
                    self.defilement.set(new_pos)
                    self.scale_tool_size.set(new_pos)
                    self.defile(int(new_pos))

            else:
                self.center=[(event.x+ self.zoom_pts[0][0])/self.ratio,(event.y+ self.zoom_pts[0][1])/self.ratio]
                Delta=(event.delta/30)
                self.ratio = self.ratio+(Delta/240)
                self.afficher()

    def callback_miniature(self, event):
        Position = self.defilement.get() - (250 - event.y)
        possible_Pos = [*range(int(self.SizeMin[0] / len(self.Images)), self.SizeMin[0]+1, int(self.SizeMin[0] / len(self.Images)))]
        for Poss in range(len(possible_Pos)):
            if Position < possible_Pos[Poss]:
                if self.Current_img != Poss:
                    self.Current_img = Poss
                    self.pt_Poly = []
                    self.pt_selected = None
                if self.Current_img < (len(self.Images) - 1):
                    self.Image_suiv.config(state="normal")
                else:
                    self.Image_suiv.config(state="disabled")

                if self.Current_img == 0:
                    self.Image_prec.config(state="disabled")
                else:
                    self.Image_prec.config(state="normal")

                self.afficher()
                break

    def defile(self, val):
        if len(self.Images) > 0:
            val = int(val)
            self.cutted_Miniature = self.Miniature[(val - 250):val, 0:self.SizeMin_cut[1]]
            self.min_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cutted_Miniature))
            self.can_min = self.Can_Miniature_img.create_image(0, 0, image=self.min_show, anchor=NW)
            self.Can_Miniature_img.config(width=int(self.SizeMin_cut[1]), height=int(self.SizeMin_cut[0]))
            self.Can_Miniature_img.itemconfig(self.can_min, image=self.min_show)
            self.update()

    def transfo_img(self, image_ID):
        overlay = np.zeros(self.Images[image_ID].shape, dtype=np.uint8)
        for particle in range(len(self.Datas_generales[image_ID]["Particles"])):
            overlay = cv2.drawContours(overlay, self.Datas_generales[image_ID]["Particles"][particle], -1, (0, 0, 255), -1)
        opacity = 0.75

        TMP_image = np.copy(self.Images[image_ID])

        # Echelle
        TMP_image = cv2.line(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][0]),
                             tuple(self.Datas_generales[image_ID]["Scale"][1]), (255, 0, 150), 3)
        TMP_image = cv2.circle(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][0]),
                               10, (255, 0, 0), 2)
        TMP_image = cv2.circle(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][1]),
                               10, (255, 0, 0), 2)

        # Selection_Poly
        for pt in range(len(self.pt_Poly)):
            TMP_image = cv2.circle(TMP_image, tuple(self.pt_Poly[pt]), 10, (0, 255, 0), -1)
            if pt > 0:
                TMP_image = cv2.line(TMP_image, tuple(self.pt_Poly[pt - 1]), tuple(self.pt_Poly[pt]), (0, 255, 0), 2)

        TMP_image = cv2.addWeighted(TMP_image, 1, overlay, opacity, 0)

        if self.Datas_generales[image_ID]["Target"] is not None:
            TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Target"], -1, (250, 0, 0), 4)

        if self.Datas_generales[image_ID]["Particles"] is not None:
            for target in range(len(self.Datas_generales[image_ID]["Particles"])):
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Particles"][target], -1, (0, 0, 250), 2)

        if len(self.Datas_generales[image_ID]["Red"]) > 0 and self.Datas_generales[image_ID]["Red"][0] is not None:
            TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Red"], -1, (150, 0, 0), 10)

        if len(self.Datas_generales[image_ID]["Blue"]) > 0 and self.Datas_generales[image_ID]["Blue"][0] is not None:
            TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Blue"], -1, (0, 0, 150), 10)

        if len(self.Datas_generales[image_ID]["Yellow"]) > 0 and self.Datas_generales[image_ID]["Yellow"][0] is not None:
            TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Yellow"], -1, (150, 150, 2), 10)

        if len(self.Datas_generales[image_ID]["White"]) > 0 and self.Datas_generales[image_ID]["White"][0] is not None:
            TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["White"], -1, (200, 200, 200), 10)

        return (TMP_image)

    def afficher_min(self):
        if len(self.Images) > 0:
            for ImG in range(len(self.Images)):
                if ImG == 0:
                    TMP_min = self.transfo_img(ImG)
                    name = self.Images_names[ImG].split("/")[-1]
                    TMP_min = cv2.putText(TMP_min, name, (50, TMP_min.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 8,
                                          (255, 255, 255), 35, cv2.LINE_AA)
                    TMP_min = cv2.putText(TMP_min, name, (50, TMP_min.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 8,
                                          (0, 0, 0), 20, cv2.LINE_AA)
                    self.Miniature = TMP_min
                else:
                    TMP_min = self.transfo_img(ImG)
                    name = self.Images_names[ImG].split("/")[-1]
                    TMP_min = cv2.putText(TMP_min, name, (50, TMP_min.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 8,
                                          (255, 255, 255), 35, cv2.LINE_AA)
                    TMP_min = cv2.putText(TMP_min, name, (50, TMP_min.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 8,
                                          (0, 0, 0), 20, cv2.LINE_AA)
                    self.Miniature = np.concatenate((self.Miniature, TMP_min), axis=0)

            SizeMin = self.Miniature.shape
            self.Miniature = cv2.resize(self.Miniature,
                                        (int(SizeMin[1] * self.ratio_min), int(SizeMin[0] * self.ratio_min)))

            self.cutted_Miniature = self.Miniature[self.defilement.get() - 250: self.defilement.get(), 0:SizeMin[1]]
            self.SizeMin_cut = self.cutted_Miniature.shape

            self.min_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cutted_Miniature))
            self.can_min = self.Can_Miniature_img.create_image(0, 0, image=self.min_show, anchor=NW)
            self.Can_Miniature_img.config(width=int(self.SizeMin_cut[1]), height=int(self.SizeMin_cut[0]))
            self.Can_Miniature_img.itemconfig(self.can_min, image=self.min_show)

    def afficher(self, Coos=(-100, -100)):
        Size = self.Images[self.Current_img].shape
        max_X = 1100
        max_Y = max_X / (Size[1] / Size[0])

        self.TMP_image_to_show = self.transfo_img(self.Current_img)
        if self.pt_selected == None and self.tool_type.get() == "Pencil":
            self.TMP_image_to_show = cv2.circle(self.TMP_image_to_show, Coos, self.tool_size, (0, 0, 255), 3)

        self.TMP_image_to_show = cv2.resize(self.TMP_image_to_show,
                                            (int(Size[1] * self.ratio), int(Size[0] * self.ratio)))

        if self.TMP_image_to_show.shape[1] > max_X or self.TMP_image_to_show.shape[0] > max_Y:
            diff_x = int(self.TMP_image_to_show.shape[1] - max_X)
            diff_y = int(self.TMP_image_to_show.shape[0] - max_Y)

            min_x = int((self.center[0] * self.ratio) - (self.TMP_image_to_show.shape[1] - (diff_x)) / 2)
            max_x = int((self.center[0] * self.ratio) + (self.TMP_image_to_show.shape[1] - (diff_x)) / 2)

            if min_x < 0:
                min_x = 0
                max_x = self.TMP_image_to_show.shape[1] - (diff_x)

            if max_x > self.TMP_image_to_show.shape[1]:
                max_x = self.TMP_image_to_show.shape[1]
                min_x = diff_x

            min_y = int((self.center[1] * self.ratio) - (self.TMP_image_to_show.shape[0] - (diff_y)) / 2)
            max_y = int((self.center[1] * self.ratio) + (self.TMP_image_to_show.shape[0] - (diff_y)) / 2)

            if min_y < 0:
                min_y = 0
                max_y = int(self.TMP_image_to_show.shape[0] - (diff_y))

            if max_y > self.TMP_image_to_show.shape[0]:
                max_y = self.TMP_image_to_show.shape[0]
                min_y = diff_y
            self.TMP_image_to_show = self.TMP_image_to_show[min_y:max_y, min_x:max_x]

            self.zoom_pts = [[min_x, min_y], [max_x, max_y]]

        if len(self.Images_names[self.Current_img]) > 130:
            name = self.Images_names[self.Current_img][:3] + "[...]" + self.Images_names[self.Current_img][
                                                                       len(self.Images_names[self.Current_img]) - 110:]
        else:
            name = self.Images_names[self.Current_img]

        self.TMP_image_to_show = cv2.putText(self.TMP_image_to_show, name, (10, self.TMP_image_to_show.shape[0] - 10),
                                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        self.TMP_image_to_show = cv2.putText(self.TMP_image_to_show, name, (10, self.TMP_image_to_show.shape[0] - 10),
                                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show))
        self.can_import = self.canvas_main_img.create_image(0, 0, image=self.image_to_show2, anchor=NW)
        self.canvas_main_img.config(width=int(max_X), height=int(max_Y))
        self.canvas_main_img.itemconfig(self.can_import, image=self.image_to_show2)
        self.update()

    def move_pt_mask(self, event, invert=False):
        if int((event.x + self.zoom_pts[0][0]) / self.ratio)<0:
            event.x= 0

        elif int((event.x + self.zoom_pts[0][0]) / self.ratio)>self.Images[self.Current_img].shape[1]:
            event.x=(self.Images[self.Current_img].shape[1]*self.ratio) - self.zoom_pts[0][0]

        if int((event.y + self.zoom_pts[0][1]) / self.ratio)<0:
            event.y= 0

        elif int((event.y + self.zoom_pts[0][1]) / self.ratio)>self.Images[self.Current_img].shape[0]:
            event.y=(self.Images[self.Current_img].shape[0]*self.ratio) - self.zoom_pts[0][1]


        if self.pt_selected != None:
            if self.pt_selected == 1:
                self.Datas_generales[self.Current_img]["Scale"][0][0] = int((event.x + self.zoom_pts[0][0]) / self.ratio)
                self.Datas_generales[self.Current_img]["Scale"][0][1] = int((event.y + self.zoom_pts[0][1]) / self.ratio)
                self.afficher()
            elif self.pt_selected == 2:
                self.Datas_generales[self.Current_img]["Scale"][1][0] = int((event.x + self.zoom_pts[0][0]) / self.ratio)
                self.Datas_generales[self.Current_img]["Scale"][1][1] = int((event.y + self.zoom_pts[0][1]) / self.ratio)
                self.afficher()

            elif self.pt_selected > 2:
                self.pt_Poly[self.pt_selected - 3][0] = int((event.x + self.zoom_pts[0][0]) / self.ratio)
                self.pt_Poly[self.pt_selected - 3][1] = int((event.y + self.zoom_pts[0][1]) / self.ratio)
                self.afficher()

        elif self.tool_type.get() == "Pencil":
            if self.tool_add.get():
                color = 255
            else:
                color = 0

            if invert:
                color=255-color

            grey = cv2.cvtColor(self.Images[self.Current_img], cv2.COLOR_RGB2GRAY)
            mask = np.zeros(grey.shape, dtype=np.uint8)
            if len(self.Datas_generales[self.Current_img][self.which_tool.get()]) > 0 and np.any(self.Datas_generales[self.Current_img][self.which_tool.get()][0] != None):
                mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()], -1, (255), -1)
            cv2.line(mask, (int((event.x + self.zoom_pts[0][0]) / self.ratio), int((event.y + self.zoom_pts[0][1]) / self.ratio)), (int((self.last_pt.x + self.zoom_pts[0][0]) / self.ratio), int((self.last_pt.y + self.zoom_pts[0][1]) / self.ratio)), (color), int(self.tool_size*2))
            New_cnts, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts

        self.last_pt=event
        self.afficher((int((event.x + self.zoom_pts[0][0]) / self.ratio), int((event.y + self.zoom_pts[0][1]) / self.ratio)))

    def move_pt_mask_R(self, event):
        self.move_pt_mask(event, invert=True)

    def end_move(self, event):
        self.pt_selected = None
        self.last_pt=None
        self.afficher(
            (int((event.x + self.zoom_pts[0][0]) / self.ratio), int((event.y + self.zoom_pts[0][1]) / self.ratio)))

    def Change_add(self, type=None):
        if not isinstance(type, (bool)):
            self.tool_add.set(not self.tool_add.get())
        else:
            self.tool_add.set(type)

    def validate(self):
        self.update_show()

        if len(self.Images) > 0:
            self.Datas_generales[self.Current_img]["Particles"]=[]
            for fish in range(len(self.Datas_generales[self.Current_img]["Target"])):
                self.Datas_generales[self.Current_img]["Particles"].append(Fun.find_red(self.Images[self.Current_img],
                                                                         self.Datas_generales[self.Current_img]["Target"][fish], (
                                                                         int(float(self.hue_bot.get()) / 2),
                                                                         int(float(self.hue_top.get()) / 2)), (
                                                                         (int(float(self.sat_bot.get()))),
                                                                         int(float(self.sat_top.get()))), (
                                                                         int(float(self.val_bot.get())),
                                                                         int(float(self.val_top.get())))))
            self.afficher()
        self.update()

    def update_show(self, *args):
        Size = self.img_colors.shape

        if int(self.hue_bot.get()) < int(self.hue_top.get()):
            if not ((self.shown_col[0])>=int(self.hue_bot.get()) and (self.shown_col[0])<=int(self.hue_top.get())):
                self.shown_col=[int(self.hue_bot.get()),0]
        else:
            if ((self.shown_col[0])>=int(self.hue_bot.get()) and (self.shown_col[0])<=int(self.hue_top.get())):
                self.shown_col=[int(self.hue_bot.get()),0]


        self.img_colors_new = np.copy(self.img_colors)
        self.img_colors_new_r = cv2.resize(self.img_colors_new, (int(Size[1] * 0.5), int(Size[0] * 0.5)))
        self.img_colors_new_r = cv2.cvtColor(self.img_colors_new_r,cv2.COLOR_RGB2BGR)


        # Display color chart
        self.angle1 = -(float(self.hue_bot.get()) + 180) * math.pi / 180
        self.angle2 = -(float(self.hue_top.get()) + 180) * math.pi / 180

        new_x = int((540 / 2) + ((245 / 2) * math.sin(self.angle1)))
        new_y = int((540 / 2) + ((245 / 2) * math.cos(self.angle1)))
        new_x2 = int((540 / 2) + (((245 + 154) / 2) * math.sin(self.angle1)))
        new_y2 = int((540 / 2) + (((245 + 154) / 2) * math.cos(self.angle1)))
        cv2.line(self.img_colors_new, (new_x, new_y), (new_x2, new_y2), (255, 255, 255), 4)

        new_x = int((540 / 2) + ((245 / 2) * math.sin(self.angle2)))
        new_y = int((540 / 2) + ((245 / 2) * math.cos(self.angle2)))
        new_x2 = int((540 / 2) + (((245 + 154) / 2) * math.sin(self.angle2)))
        new_y2 = int((540 / 2) + (((245 + 154) / 2) * math.cos(self.angle2)))
        cv2.line(self.img_colors_new, (new_x, new_y), (new_x2, new_y2), (0, 0, 0), 4)

        self.img_colors_new = cv2.cvtColor(self.img_colors_new, cv2.COLOR_BGR2RGB)
        if float(self.hue_bot.get()) < float(self.hue_top.get()):
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0,
                                              int((float(self.hue_bot.get()) - 90)),
                                              int((float(self.hue_top.get()) - 90)), (20, 0, 20), 4)
        else:
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0,
                                              int((float(self.hue_bot.get()) - 90)), 360 - 90, (20, 0, 20), 4)
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0, 360 - 90,
                                              int((float(self.hue_top.get()) - 90)) + 360, (20, 0, 20), 4)

        self.TMP_img_col = cv2.resize(self.img_colors_new, (int(Size[1] * 0.5), int(Size[0] * 0.5)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)

        #Display saturation chart
        saturations=self.saturations.copy()
        self.sat3=cv2.line(saturations, (0,int(self.sat_bot.get())),(int(self.canvas_img_sat.winfo_width()),int(self.sat_bot.get())),(200,200,200),2)
        self.sat3 = cv2.line(saturations, (0, int(self.sat_top.get())),(int(self.canvas_img_sat.winfo_width()), int(self.sat_top.get())), (50, 50, 50), 2)
        self.sat3=cv2.resize(self.sat3,(int(self.canvas_img_sat.winfo_width()),int(self.canvas_img_sat.winfo_height())))
        self.sat_ratio=int(self.canvas_img_sat.winfo_height())/self.saturations.shape[0]
        self.sat4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.sat3))
        self.canvas_img_sat.create_image(0,0, image=self.sat4, anchor=NW)

        #Display value chart
        values=self.values.copy()
        self.val3=cv2.line(values, (0,int(self.val_bot.get())),(int(self.canvas_img_val.winfo_width()),int(self.val_bot.get())),(200,200,200),2)
        self.val3 = cv2.line(values, (0, int(self.val_top.get())),(int(self.canvas_img_val.winfo_width()), int(self.val_top.get())), (50, 50, 50), 2)
        self.val3=cv2.resize(self.val3,(int(self.canvas_img_val.winfo_width()),int(self.canvas_img_val.winfo_height())))
        self.val_ratio=int(self.canvas_img_val.winfo_height())/self.values.shape[0]
        self.val4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.val3))
        self.canvas_img_val.create_image(0,0, image=self.val4, anchor=NW)


        #Selected colors
        bgr=display_colors.create_sat_val(self.shown_col[0],int(self.sat_bot.get()),int(self.sat_top.get()),int(self.val_bot.get()),int(self.val_top.get()))
        self.bgr=cv2.resize(bgr,(int(self.canvas_img_saturation_value.winfo_width()),int(self.canvas_img_saturation_value.winfo_height())))
        self.bgr2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.bgr))
        self.canvas_img_saturation_value.create_image(0,0, image=self.bgr2, anchor=NW)

        himg=display_colors.create_hue(int(self.hue_bot.get()),int(self.hue_top.get()))
        self.bgr3=cv2.resize(himg,(int(self.canvas_img_hue.winfo_width()),int(self.canvas_img_hue.winfo_height())))
        self.bgrX=self.bgr3.copy()
        self.bgr3=cv2.rectangle(self.bgr3, (0,self.shown_col[1]-1),(int(self.canvas_img_hue.winfo_width()-1),self.shown_col[1]+1),(150,150,150),1)
        self.bgr4 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.bgr3))
        self.canvas_img_hue.create_image(0,0, image=self.bgr4, anchor=NW)
        self.canvas_img_hue.bind("<Button-1>",self.select_col)
        self.canvas_img_hue.bind("<B1-Motion>", self.select_col)

    def move_sat(self, event):
        rgb = np.uint8([[self.saturations[int(event.y/self.sat_ratio),1]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        new_val = hsv[0, 0, 1]

        if (self.focus_get()==self.sat_top):
            self.sat_top.delete(0, END)
            self.sat_top.insert(0, str(new_val))
        else:
            self.sat_bot.delete(0, END)
            self.sat_bot.insert(0, str(new_val))

        if int(self.sat_bot.get()) > int(self.sat_top.get()):
            nbot = self.sat_top.get()
            ntop = self.sat_bot.get()
            self.sat_top.delete(0, END)
            self.sat_top.insert(0, ntop)
            self.sat_bot.delete(0, END)
            self.sat_bot.insert(0, nbot)

        self.update_show()

    def drag_sat(self, event):
        rgb = np.uint8([[self.saturations[int(event.y/self.sat_ratio),1]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        new_val = hsv[0, 0, 1]

        if (self.focus_get()==self.sat_top):
            self.sat_bot.delete(0, END)
            self.sat_bot.insert(0, str(new_val))
        else:
            self.sat_top.delete(0, END)
            self.sat_top.insert(0, str(new_val))

        if int(self.sat_bot.get())>int(self.sat_top.get()):
            nbot=self.sat_top.get()
            ntop=self.sat_bot.get()
            self.sat_top.delete(0, END)
            self.sat_top.insert(0, ntop)
            self.sat_bot.delete(0, END)
            self.sat_bot.insert(0, nbot)

        self.update_show()

    def move_val(self, event):
        rgb = np.uint8([[self.values[int(event.y/self.val_ratio),1]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        new_val = hsv[0, 0, 2]

        if (self.focus_get()==self.val_top):
            self.val_top.delete(0, END)
            self.val_top.insert(0, str(new_val))
        else:
            self.val_bot.delete(0, END)
            self.val_bot.insert(0, str(new_val))

        if int(self.val_bot.get())>int(self.val_top.get()):
            nbot=self.val_top.get()
            ntop=self.val_bot.get()
            self.val_top.delete(0, END)
            self.val_top.insert(0, ntop)
            self.val_bot.delete(0, END)
            self.val_bot.insert(0, nbot)


        self.update_show()

    def drag_val(self, event):
        rgb = np.uint8([[self.values[int(event.y/self.val_ratio),1]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        new_val = hsv[0, 0, 2]

        if (self.focus_get()==self.val_top):
            self.val_bot.delete(0, END)
            self.val_bot.insert(0, str(new_val))
        else:
            self.val_top.delete(0, END)
            self.val_top.insert(0, str(new_val))

        if int(self.val_bot.get())>int(self.val_top.get()):
            nbot=self.val_top.get()
            ntop=self.val_bot.get()
            self.val_top.delete(0, END)
            self.val_top.insert(0, ntop)
            self.val_bot.delete(0, END)
            self.val_bot.insert(0, nbot)

        self.update_show()


    def select_col(self,event):
        if event.y<0:
            event.y=0
        elif event.y>=99:
            event.y=99

        if event.x < 0:
            event.x = 0
        elif event.x >= 19:
            event.x = 19

        rgb = np.uint8([[self.bgrX[event.y, event.x]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        self.shown_col = [int(float(hsv[0, 0, 0])) * 2, int(event.y)]  # hue
        self.update_show()

    def validate_all(self):
        load_frame = Loading.Loading(self.canvas_main)  # Progression bar
        load_frame.show_load(0)
        Size = self.img_colors.shape
        self.img_colors_new = np.copy(self.img_colors)
        self.img_colors_new_r = cv2.resize(self.img_colors_new, (int(Size[1] * 0.5), int(Size[0] * 0.5)))

        self.angle1 = -(float(self.hue_bot.get()) + 180) * math.pi / 180
        self.angle2 = -(float(self.hue_top.get()) + 180) * math.pi / 180

        new_x = int((540 / 2) + ((245 / 2) * math.sin(self.angle1)))
        new_y = int((540 / 2) + ((245 / 2) * math.cos(self.angle1)))
        new_x2 = int((540 / 2) + (((245 + 154) / 2) * math.sin(self.angle1)))
        new_y2 = int((540 / 2) + (((245 + 154) / 2) * math.cos(self.angle1)))
        cv2.line(self.img_colors_new, (new_x, new_y), (new_x2, new_y2), (255, 255, 255), 4)

        new_x = int((540 / 2) + ((245 / 2) * math.sin(self.angle2)))
        new_y = int((540 / 2) + ((245 / 2) * math.cos(self.angle2)))
        new_x2 = int((540 / 2) + (((245 + 154) / 2) * math.sin(self.angle2)))
        new_y2 = int((540 / 2) + (((245 + 154) / 2) * math.cos(self.angle2)))
        cv2.line(self.img_colors_new, (new_x, new_y), (new_x2, new_y2), (0, 0, 0), 4)

        self.img_colors_new = cv2.cvtColor(self.img_colors_new, cv2.COLOR_BGR2RGB)
        if float(self.hue_bot.get()) < float(self.hue_top.get()):
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0,
                                              int((float(self.hue_bot.get()) - 90)),
                                              int((float(self.hue_top.get()) - 90)), (20, 0, 20), 4)
        else:
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0,
                                              int((float(self.hue_bot.get()) - 90)), 360 - 90, (20, 0, 20), 4)
            self.img_colors_new = cv2.ellipse(self.img_colors_new, (int(540 / 2), int(540 / 2)),
                                              (int((245 + 200) / 2), int((245 + 200) / 2)), 0, 360 - 90,
                                              int((float(self.hue_top.get()) - 90)) + 360, (20, 0, 20), 4)

        self.TMP_img_col = cv2.resize(self.img_colors_new, (int(Size[1] * 0.5), int(Size[0] * 0.5)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)


        if len(self.Images) > 0:
            for img in range(len(self.Datas_generales)):
                load_frame.show_load(img/len(self.Datas_generales))
                self.Datas_generales[img]["Particles"]=[]

                for target in range(len(self.Datas_generales[img]["Target"])):
                    self.Datas_generales[img]["Particles"].append( Fun.find_red(self.Images[img], self.Datas_generales[img]["Target"][target], (
                    int(float(self.hue_bot.get()) / 2), int(float(self.hue_top.get()) / 2)), (
                                                                 (int(float(self.sat_bot.get()))),
                                                                 int(float(self.sat_top.get()))), (
                                                                 int(float(self.val_bot.get())),
                                                                 int(float(self.val_top.get())))))
            self.afficher_min()
            self.afficher()
        self.update()
        load_frame.destroy()

    def move_col(self, event):
        rgb = np.uint8([[self.img_colors_new_r[event.y, event.x]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

        new_val = int(float(hsv[0, 0, 0]))*2


        if (self.focus_get()==self.hue_top):
            self.hue_top.delete(0, END)
            self.hue_top.insert(0, str(new_val))
        else:
            self.hue_bot.delete(0, END)
            self.hue_bot.insert(0, str(new_val))

        self.update_show()

    def drag_col(self, event):
        rgb = np.uint8([[self.img_colors_new_r[event.y, event.x]]])  # shape: (1,1,3)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        new_val = int(float(hsv[0, 0, 0]))*2


        if (self.focus_get()==self.hue_top):
            self.hue_bot.delete(0, END)
            self.hue_bot.insert(0, str(new_val))
        else:
            self.hue_top.delete(0, END)
            self.hue_top.insert(0, str(new_val))
        self.update_show()



    def Change_tool_size(self, size):
        self.tool_size = int(size)

    def callback_mask(self, event, invert=False):
        X = (event.x + self.zoom_pts[0][0]) / self.ratio
        Y = (event.y + self.zoom_pts[0][1]) / self.ratio
        if math.sqrt((X - self.Datas_generales[self.Current_img]["Scale"][0][0]) ** 2 + (
                Y - self.Datas_generales[self.Current_img]["Scale"][0][1]) ** 2) < 20:
            self.pt_selected = 1
        elif math.sqrt((X - self.Datas_generales[self.Current_img]["Scale"][1][0]) ** 2 + (
                Y - self.Datas_generales[self.Current_img]["Scale"][1][1]) ** 2) < 20:
            self.pt_selected = 2

        elif self.tool_type.get() == "Poly":
            compteur = 0
            pt_find = False
            while not pt_find and compteur < len(self.pt_Poly):
                if math.sqrt(
                        (X - self.pt_Poly[compteur][0]) ** 2 + (Y - self.pt_Poly[compteur][1]) ** 2) < 20:
                    pt_find = True
                    if compteur != 0 or len(self.pt_Poly) == 1:
                        self.pt_selected = 3 + compteur
                    if compteur == 0:
                        self.fill_Poly(invert)
                compteur = compteur + 1

            if not pt_find:
                self.pt_Poly.append([int(X), int(Y)])
                self.pt_selected = len(self.pt_Poly) + 3 - 1

        elif self.tool_type.get() == "Pencil":
            if self.tool_add.get():
                color = 255
            else:
                color = 0

            if invert:
                color=255-color

            grey = cv2.cvtColor(self.Images[self.Current_img], cv2.COLOR_RGB2GRAY)
            mask = np.zeros(grey.shape, dtype=np.uint8)
            if len(self.Datas_generales[self.Current_img][self.which_tool.get()]) > 0 and np.any(self.Datas_generales[self.Current_img][self.which_tool.get()][0] != None):
                mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()], -1, (255), -1)

            cv2.circle(mask, (int(X), int(Y)),self.tool_size, (color), -1)
            New_cnts, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts
            self.last_pt=event
        self.afficher((int(X), int(Y)))


    def callback_mask_R(self, event):
        self.callback_mask(event,invert=True)



    def fill_Poly(self, invert=False):
        if self.tool_add.get():
            color = 255
        else:
            color = 0
        if invert:
            color=255-color
        grey = cv2.cvtColor(self.Images[self.Current_img], cv2.COLOR_RGB2GRAY)
        mask = np.zeros(grey.shape, dtype=np.uint8)
        if len(self.Datas_generales[self.Current_img][self.which_tool.get()]) > 0 and np.any(
                self.Datas_generales[self.Current_img][self.which_tool.get()][0] != None):
            mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()], -1, (255), -1)
        pts = np.array(self.pt_Poly, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.drawContours(mask, [pts], -1, color, -1)
        New_cnts, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts

        self.pt_Poly = []
        self.pt_selected = None
        self.afficher()

    def press_fenetre(self, event):
        self.press_position = pyautogui.position()
        self.win_old_pos = (fenetre.winfo_x(), fenetre.winfo_y())

    def move_fenetre(self, event):
        self.actual_pos = pyautogui.position()
        deplacement = ("", str(self.actual_pos[0] - self.press_position[0] + self.win_old_pos[0]),
                       str(self.actual_pos[1] - self.press_position[1] + self.win_old_pos[1]))
        fenetre.geometry("+".join(deplacement))

    def fermer(self):
        self.quitter = True
        fenetre.destroy()

    def save_particles(self):
        load_frame = Loading.Loading(self.canvas_main)  # Progression bar
        load_frame.show_load(0)
        file_to_save = filedialog.asksaveasfilename(defaultextension=".csv")
        with open(file_to_save, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            Names = ["File", "Type", "Fish_ID", "ID", "Area", "Mean_Hue", "Mean_Saturation", "Mean_Value"]
            writer.writerow(Names)

            for i in range(len(self.Datas_generales)):
                load_frame.show_load(i/len(self.Datas_generales))
                ratio_mm = float(self.distance.get()) / math.sqrt((self.Datas_generales[i]["Scale"][0][0] - self.Datas_generales[i]["Scale"][1][0]) ** 2 + (
                            self.Datas_generales[i]["Scale"][0][1] - self.Datas_generales[i]["Scale"][1][1]) ** 2)
                for j in range(len(self.Datas_generales[i]["Target"])):
                    File = self.Datas_generales[i]["File"]
                    Type = "Target"
                    Fish_ID=j
                    ID = j
                    Area = cv2.contourArea(self.Datas_generales[i]["Target"][j])
                    Area_mm = Area * (ratio_mm ** 2)
                    hsv = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2HSV)
                    grey = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2GRAY)
                    mask = np.zeros(grey.shape, dtype=np.uint8)
                    mask = cv2.drawContours(mask, [self.Datas_generales[i]["Target"][j]], -1, (255, 255, 255), -1)
                    ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                    Mean_H, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)
                    raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H*2, Mean_S, Mean_V]
                    writer.writerow(raw)

                for target in range(len(self.Datas_generales[i]["Particles"])):
                    load_frame.show_load((i+target/len(self.Datas_generales[i]["Particles"])) / len(self.Datas_generales))
                    for j in range(len(self.Datas_generales[i]["Particles"][target])):
                        File = self.Datas_generales[i]["File"]
                        Type = "Particle"
                        Fish_ID = target
                        ID = j
                        Area = cv2.contourArea(self.Datas_generales[i]["Particles"][target][j])
                        Area_mm = Area * (ratio_mm ** 2)
                        if Area_mm > 0:
                            hsv = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2HSV)
                            grey = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2GRAY)
                            mask = np.zeros(grey.shape, dtype=np.uint8)
                            mask = cv2.drawContours(mask, [self.Datas_generales[i]["Particles"][target][j]], -1, (255, 255, 255), -1)
                            ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                            Mean_H, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)
                            raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H*2, Mean_S, Mean_V]
                            writer.writerow(raw)

                for color in ["Yellow","Blue","Red","White"]:
                    for j in range(len(self.Datas_generales[i][color])):
                        if self.Datas_generales[i][color][j]!=None:
                            File = self.Datas_generales[i]["File"]
                            Type = color
                            ID = j
                            Area = cv2.contourArea(self.Datas_generales[i]["Yellow"][j])
                            Area_mm = Area * (ratio_mm ** 2)
                            hsv = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2HSV)
                            grey = cv2.cvtColor(self.Images[i], cv2.COLOR_RGB2GRAY)
                            mask = np.zeros(grey.shape, dtype=np.uint8)
                            mask = cv2.drawContours(mask, [self.Datas_generales[i][color][j]], -1, (255, 255, 255), -1)
                            ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                            Mean_H, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)
                            raw = [File, Type, "NA", ID, Area_mm, Mean_H*2, Mean_S, Mean_V]
                            writer.writerow(raw)

        load_frame.destroy()

    def suivant(self):
        if self.Current_img <= (len(self.Images) - 2):
            self.Current_img = self.Current_img + 1

            if self.Current_img == (len(self.Images) - 1):
                self.Image_suiv.config(state="disabled")
            else:
                self.Image_suiv.config(state="normal")
            if self.Current_img == 0:
                self.Image_prec.config(state="disabled")
            else:
                self.Image_prec.config(state="normal")
            self.afficher()

    def precedant(self):
        if self.Current_img > 0:
            self.Current_img = self.Current_img - 1
            if self.Current_img == (len(self.Images) - 1):
                self.Image_suiv.config(state="disabled")
            else:
                self.Image_suiv.config(state="normal")
            if self.Current_img == 0:
                self.Image_prec.config(state="disabled")
            else:
                self.Image_prec.config(state="normal")
            self.afficher()

    def affiche_mouse(self, event):
        if len(self.Images) > 0:
            X = int(round((event.x + self.zoom_pts[0][0]) / self.ratio, 1))
            Y = int(round((event.y + self.zoom_pts[0][1]) / self.ratio, 1))

            rgb = np.uint8([[self.Images[self.Current_img][Y,X]]])  # shape: (1,1,3)
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[0,0]


            self.position_mouse.set("x={0}, y={1}, Hue={2}, Saturation={3}, Value={4}".format(X,Y,hsv[0]*2,hsv[1],hsv[2]))
            self.afficher( (int((event.x + self.zoom_pts[0][0]) / self.ratio), int((event.y + self.zoom_pts[0][1]) / self.ratio)))


    def save(self):
        file_to_save = filedialog.asksaveasfilename(defaultextension=".rfd")
        Params=[self.hue_bot.get(), self.hue_top.get(), self.sat_bot.get(), self.sat_top.get(),self.val_bot.get(),self.val_top.get()]
        with open(file_to_save, 'wb') as fp:
            pickle.dump((self.Datas_generales, self.Images_names, Params), fp)

    def open_file(self):
        file_to_open = filedialog.askopenfilename()
        with open(file_to_open, 'rb') as fp:
            self.Datas_generales, self.Images_names, Params = pickle.load(fp)

        self.hue_bot.delete(0, END)
        self.hue_bot.insert(0, Params[0])
        self.hue_top.delete(0, END)
        self.hue_top.insert(0, Params[1])

        self.sat_bot.delete(0, END)
        self.sat_bot.insert(0, Params[2])
        self.sat_top.delete(0, END)
        self.sat_top.insert(0, Params[3])

        self.val_bot.delete(0, END)
        self.val_bot.insert(0, Params[4])
        self.val_top.delete(0, END)
        self.val_top.insert(0, Params[5])

        self.shown_col = [int(self.hue_bot.get()),0]
        self.shown_sat = [int(self.sat_bot.get()), 0]
        self.shown_val = [int(self.val_bot.get()), 0]
        self.update_show()

        load_frame = Loading.Loading(self.canvas_main)  # Progression bar
        load_frame.show_load(0)
        self.load_images(load_frame)
        load_frame.destroy()

        self.afficher()
        self.afficher_min()
        self.update()

    def open_new_seq(self):
        files = filedialog.askopenfilenames()

        load_frame = Loading.Loading(self.canvas_main)  # Progression bar
        load_frame.show_load(0)

        done=0
        for file in files:
            load_frame.show_load((done/len(files))*0.1)
            file=str(file)
            if os.path.isfile(file) and imghdr.what(file):
                self.Images_names.append(file)
            done+=1

        self.automated_findings(load_frame)
        self.load_images(load_frame)
        self.afficher()
        self.afficher_min()
        self.update()

    def load_images(self,load_frame):
        self.Images = []
        first = True
        compteur = -1
        count=0
        for file in self.Images_names:
            load_frame.show_load(0.5+0.5*(count/len(self.Images_names)))
            compteur = compteur + 1
            ImG = cv2.imread(file)
            ImG = cv2.cvtColor(ImG, cv2.COLOR_BGR2RGB)
            self.Images.append(ImG)

            if first:
                ImG = self.transfo_img(compteur)
                self.Miniature = ImG
                first = False
            else:
                ImG = self.transfo_img(compteur)
                self.Miniature = np.concatenate((self.Miniature, ImG), axis=0)
            count+=1

        SizeMin = self.Miniature.shape
        self.ratio_min = 400 / SizeMin[1]

        self.Current_img = 0
        self.Miniature = cv2.resize(self.Miniature,
                                    (int(SizeMin[1] * self.ratio_min), int(SizeMin[0] * self.ratio_min)))
        self.SizeMin = self.Miniature.shape
        self.center = [self.Images[self.Current_img].shape[1] / 2, self.Images[self.Current_img].shape[0] / 2]
        self.zoom_pts = [[0, 0], list(self.Images[self.Current_img].shape[:2])]

        self.cutted_Miniature = self.Miniature[0:250, 0:self.SizeMin[1]]
        self.SizeMin_cut = self.cutted_Miniature.shape
        self.scale_tool_size.configure(to=self.SizeMin[0] - 1)
        self.afficher_min()
        load_frame.destroy()

    def automated_findings(self, load_frame):
        self.Datas_generales = []
        count=0
        for file in self.Images_names:
            load_frame.show_load(0.1 + 0.4 * (count / len(self.Images_names)))
            ImG = cv2.imread(file)
            ImG = cv2.cvtColor(ImG, cv2.COLOR_BGR2RGB)
            Actual_fish_cnt = Fun.find_fish(ImG)
            pt1, pt2 = Fun.find_scale(ImG, (0,0),(0,0),(0,0))#For yellow scale:(15, 30), (50, 255), (100, 255)
            Actual_particles = []
            Actual_yellow_scale = Fun.color_calib(ImG, "yellow")
            Actual_blue_scale = Fun.color_calib(ImG, "blue")
            Actual_red_scale = Fun.color_calib(ImG, "red")
            Actual_white_scale = Fun.color_calib(ImG, "white")
            self.Datas_generales.append(
                {"Target":Actual_fish_cnt, "Particles":Actual_particles, "Scale":[pt1, pt2], "Yellow":Actual_yellow_scale, "Blue":Actual_blue_scale,
                 "Red":Actual_red_scale, "White":Actual_white_scale, "File":file})
            count+=1


fenetre = Tk()
fenetre.overrideredirect(1)
fenetre.geometry("+100+100")
interface = Interface(fenetre)
interface.mainloop()
