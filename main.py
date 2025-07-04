from tkinter import *
from tkinter import filedialog
import numpy as np
import cv2
import PIL.Image, PIL.ImageTk
import math
import csv
import Extracting_particles
import Functions_find_red as Fun
import os
import pickle
import Loading
import display_colors
import imghdr
import User_loading
import Auto_detection
import Vid_list
from functools import partial
import Canvas_images
from scipy.stats import circmean



class Interface(Frame):
    def __init__(self, window, **kwargs):
        Frame.__init__(self, window, width=0, height=0, bd=5, **kwargs)
        '''Main frame of the program'''

        #Configuration of the layout
        self.grid()
        self.root=window
        self.root.rowconfigure(0,weight=1)
        self.root.rowconfigure(1, weight=100)
        self.root.columnconfigure(0, weight=1000)
        self.root.columnconfigure(1, weight=1)
        self.root.bind('<Control-s>', self.save)

        #Creation of RGB images showing the selected colors' characterictics:
        self.saturations=display_colors.create_all_sat()
        self.values = display_colors.create_all_val()

        ##Various variable initiation:
        #Related to the tool:
        self.which_tool = "Target"  #What kind of tool is selected ("Target","Red","Yellow","Blue","White"), by default our tool is selcting/unselecting the main targets
        self.tool_size = 50# Radius of the tool

        self.tool_type = StringVar()
        self.tool_type.set("Pencil") #Whether the user will draw (pencil) or create shape (polygon) to select specifi areas of the images

        self.tool_add = IntVar()
        self.tool_add.set(1)#Whether the tool incluse drawings in the selection (1) or remove those (0)

        #Other:
        #Is there a point already selected? (used later to move scale points and polygon points)
        self.pt_selected = None #None if no point is selected, if a point is selected, get it's int value

        #The size of the Miniature display (bottom left corner, used to show all images and navigate). This is for initialisation, values are updated later
        self.SizeMin = [10, 10]

        #List of Images being part of the project
        self.Images = [] #Images themselves
        self.Images_names = [] #File names of the images
        self.Current_img = 0#Which image is the one showed

        #List of points of the polygon being drawn
        self.pt_Poly = []

        ##Parameters of the program
        #Loading of the parameters that must remain always, independently from the projects (for now, only auto update exists)
        Param_file = User_loading.resource_path(os.path.join("Settings"))
        with open(Param_file, 'rb') as fp:
            Params = pickle.load(fp)

        #If True, auto_update will recalculate the particles location of the image as soon as a modification is done.
        #Can be set to False to avoid computer to be slow (in that case, the user will need to hit the "Validate" button to update particles.
        self.auto_update=Params[0]

        ## Parameters relative to the program
        self.project_open=False#Whether a project is opened (at initiation, no)
        #At initiation, we use default values of parameters used to find the taregt location
        self.param_find_targets=[0,0,0,5000,1000000,0, [[],[],[]]]
        #0=Iterations of frist erosion, 1=Iterations of dilation, 2=Iterations of second erosion, 3=Min area of the target, 4=Max area of the target,5=Smoothing (unavailable),6=HSV values associated to background

        ##GUI organisation:
        #Menubar
        self.menubar = Menu(self.root)
        self.projectmenu = Menu(self.menubar, tearoff=0)
        #Options linked to the project management
        self.menubar.add_cascade(label="Project", menu=self.projectmenu)
        self.projectmenu.add_command(label="New", command=self.create_project)
        self.projectmenu.add_command(label="Open", command=self.open_file)
        self.projectmenu.add_command(label="Save", command=self.save)
        self.projectmenu.add_command(label="Save as...", command=self.save_as)
        self.projectmenu.add_command(label="Close", command=self.close)
        self.projectmenu.entryconfig(2, state="disabled")
        self.projectmenu.entryconfig(3, state="disabled")
        self.projectmenu.entryconfig(4, state="disabled")
        # Options linked to the images of the project (disabled if there is no project open)
        self.imagesmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Images", menu=self.imagesmenu)
        self.imagesmenu.add_command(label="Add new images", command=self.add_images)
        self.imagesmenu.add_command(label="Remove current image", command=self.remove_image)
        self.imagesmenu.add_command(label="Remove images", command=self.remove_images)
        self.menubar.entryconfig("Images", state="disabled")
        # Options linked to the particles/targets to be detected
        self.particlesmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Detection", menu=self.particlesmenu)
        self.particlesmenu.add_command(label="Automatic target detection", command=self.automated_findings)
        self.particlesmenu.add_command(label="Export particles", command=self.save_particles)
        self.menubar.entryconfig("Detection", state="disabled")
        #The auto-update may be on of off. If on, the particles will be calculated each time there is a modification of the parameters/drawings
        #If off, users will have to click the "Validate" button, which will limit the risks of having slow rendering
        if self.auto_update:
            text="Auto update of particles ✔"
        else:
            text="Auto update of particles"
        self.optionsmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Options", menu=self.optionsmenu)
        self.optionsmenu.add_command(label=text, command=self.change_auto_part)
        self.root.config(menu=self.menubar)

        # Bar informing about the mouse position and pixels characteristics under the cursor
        self.canvas_info_cursor = Canvas(window, height=20, relief='flat')
        self.canvas_info_cursor.grid(row=0, column=0, columnspan=1, sticky=("nsew"))
        #X position of the mouse
        self.position_mouse_x = StringVar()
        self.position_mouse_x.set("X=0")
        self.position_mouse_x_lab = Label(self.canvas_info_cursor, textvariable=self.position_mouse_x, anchor="w")
        self.position_mouse_x_lab.grid(row=0, column=0, sticky="w")
        # Y position of the mouse
        self.position_mouse_y = StringVar()
        self.position_mouse_y.set("Y=0")
        self.position_mouse_y_lab = Label(self.canvas_info_cursor, textvariable=self.position_mouse_y, anchor="w")
        self.position_mouse_y_lab.grid(row=0, column=1, sticky="we")
        # Hue of the pixel of shown image under the cursor
        self.position_mouse_h = StringVar()
        self.position_mouse_h.set("Hue=0")
        self.position_mouse_h_lab = Label(self.canvas_info_cursor, textvariable=self.position_mouse_h, anchor="w")
        self.position_mouse_h_lab.grid(row=0, column=2, sticky="we")
        # Saturation of the pixel of shown image under the cursor
        self.position_mouse_s = StringVar()
        self.position_mouse_s.set("Sat=0")
        self.position_mouse_s_lab = Label(self.canvas_info_cursor, textvariable=self.position_mouse_s, anchor="w")
        self.position_mouse_s_lab.grid(row=0, column=3, sticky="we")
        # Value of the pixel of shown image under the cursor
        self.position_mouse_v = StringVar()
        self.position_mouse_v.set("Val=0")
        self.position_mouse_v_lab = Label(self.canvas_info_cursor, textvariable=self.position_mouse_v)
        self.position_mouse_v_lab.grid(row=0, column=4, sticky="we")
        #Organisation
        Grid.columnconfigure(self.canvas_info_cursor, 0, weight=1, minsize=75)
        Grid.columnconfigure(self.canvas_info_cursor, 1, weight=1, minsize=75)
        Grid.columnconfigure(self.canvas_info_cursor, 2, weight=1, minsize=75)
        Grid.columnconfigure(self.canvas_info_cursor, 3, weight=1, minsize=75)
        Grid.columnconfigure(self.canvas_info_cursor, 4, weight=1, minsize=75)
        Grid.columnconfigure(self.canvas_info_cursor, 5, weight=100)

        ##Showing the image
        self.frame_main = Frame(window, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.frame_main.grid(row=1, column=0, sticky="nsew")
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_rowconfigure(1, weight=0)  # button bar doesn't expand vertically

        #Creation of an empty image to be placed in the image canvas before images are imported
        self.blank = np.zeros((500, 500, 3), np.uint8)
        self.blank.fill(255)

        #Canvas that will show the images
        self.canvas_main_img = Canvas_images.Image_show(self.frame_main, self, self.blank, "No image")
        self.canvas_main_img.grid(row=0, column=0, sticky="nsew")
        self.canvas_main_img.focus_force()# we force the focus as it is the main source of interaction

        #Where the buttons to change the image are displayed (previous image/next image)
        self.frame_main_but = Frame(self.frame_main, height=20, bd=2, highlightthickness=1, relief='ridge')
        self.frame_main_but.grid(row=1, column=0, sticky="ns")

        #Buttons allowing to change the current displayed image
        self.Image_prec = Button(self.frame_main_but, text="Previous image", state="disabled", command=self.precedant)
        self.Image_prec.grid(row=0, column=0, sticky="e")#Go to the previous image (disabled when the current frame is teh first one)
        self.Image_suiv = Button(self.frame_main_but, text="Next image", command=self.suivant)
        self.Image_suiv.grid(row=0, column=1, sticky="w")#Go to the next image (disabled when the current frame is the last one)

        # Pannel with all the parameters for particle detection
        self.canvas_user = Frame(window, width=100, bd=2, highlightthickness=1, relief='flat')
        self.canvas_user.grid(row=1, column=1, sticky="nswe")
        self.canvas_user.rowconfigure(0, weight=1)
        self.canvas_user.rowconfigure(1, weight=1)
        self.canvas_user.rowconfigure(2, weight=1)
        self.canvas_user.rowconfigure(3, weight=1)
        self.canvas_user.rowconfigure(4, weight=1)
        self.canvas_user.rowconfigure(5, weight=10)
        self.canvas_user.columnconfigure(0, weight=1)


        ### Right pannel (parameters for particles detection)
        ## Selecting a real-life distance for ratio calculation, to be written by the user
        Frame_ratio=Frame(self.canvas_user)
        Frame_ratio.grid(row=0, column=0, columnspan=3)
        Label(Frame_ratio, text="Real life distance").grid(row=0, column=0)
        self.distance=StringVar()
        self.Entry_dist=Entry(Frame_ratio, textvariable=self.distance)
        self.Entry_dist.grid(row=0, column=1)

        ## Frame to select the parameters of particle detection:
        Frame_show_col=Frame(self.canvas_user)
        Frame_show_col.grid(row=1, column=0, columnspan=3, sticky="nsew")

        Frame_show_col.rowconfigure(0,weight=1)
        Frame_show_col.columnconfigure(0, weight=1)
        Frame_show_col.columnconfigure(1, weight=1)

        # Frame in which the canvas for color selection are displayed
        Color_selection=Frame(Frame_show_col, highlightthickness=5, highlightbackground="#9d9aff", relief="solid")
        Color_selection.grid(row=0, column=0, sticky="nsew")

        Color_selection.rowconfigure(0,weight=1)
        Color_selection.rowconfigure(1, weight=1)
        Color_selection.rowconfigure(2, weight=1)
        Color_selection.rowconfigure(3, weight=1)
        Color_selection.columnconfigure(0, weight=1)
        Color_selection.columnconfigure(1, weight=1)

        #Organisation of the Frame_show_col: 3 clickable canvas: one for hue, one for saturation, one for value
        Label(Color_selection, text="Color selection", font=("Helvetica", 15), background="#9d9aff").grid(row=0, column=0, columnspan=3, sticky="nsew")
        Label(Color_selection, text="Colors", font=("Helvetica", 12)).grid(row=1, column=0)
        #Canvas for Hue
        self.canvas_img_couleurs = Canvas(Color_selection, bd=0, highlightthickness=0, relief='flat', background="purple")
        self.canvas_img_couleurs.grid(row=2, column=0, sticky="ns")
        self.img_colors = cv2.imread(User_loading.resource_path(os.path.join("Colors.png")))#We load a representation of the hue values
        Size = self.img_colors.shape
        self.ratio_col = 0.35 #To resize properly the image
        self.img_colors_new = cv2.cvtColor(self.img_colors, cv2.COLOR_BGR2RGB)
        self.TMP_img_col = cv2.resize(self.img_colors_new,(int(Size[1] * self.ratio_col), int(Size[0] * self.ratio_col)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)
        self.canvas_img_couleurs.bind("<Button-1>", self.move_col)
        self.canvas_img_couleurs.bind("<B1-Motion>", self.drag_col)
        #Canvas for Saturation
        Label(Color_selection, text="Saturation", font=("Helvetica", 12)).grid(row=1, column=1)
        self.canvas_img_sat=Canvas(Color_selection, width=20, height=125, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_sat.grid(row=2, column=1, sticky="sn", pady=15)
        self.canvas_img_sat.bind("<Button-1>",self.move_sat)
        self.canvas_img_sat.bind("<B1-Motion>", self.drag_sat)
        #Canvas for Value
        Label(Color_selection, text="Value", font=("Helvetica", 12)).grid(row=1, column=2)
        self.canvas_img_val=Canvas(Color_selection, width=20, height=125, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_val.grid(row=2, column=2, sticky="sn", pady=15)
        self.canvas_img_val.bind("<Button-1>",self.move_val)
        self.canvas_img_val.bind("<B1-Motion>", self.drag_val)


        ## Display of the selected colors (so that user can see clearly how the combination of hue/sat/val looks like
        Selected_color = Frame(Frame_show_col, highlightthickness=5, highlightbackground="#9affb9", relief="solid")
        Selected_color.grid(row=0, column=1, sticky="nswe")

        Color_selection.rowconfigure(0,weight=1)
        Color_selection.rowconfigure(1, weight=1)
        Color_selection.columnconfigure(0, weight=1)
        Color_selection.columnconfigure(1, weight=1)

        Label(Selected_color, text="Selected colors", font=("Helvetica", 15), background="#9affb9").grid(row=0,
                                                                                                         column=0,
                                                                                                         columnspan=2,
                                                                                                         sticky="nsew")
        #A first canvas with the saturation ~ value representation with fixed hue
        self.canvas_img_saturation_value = Canvas(Selected_color, width=100, height=100, bd=0, highlightthickness=0,
                                                  relief='flat')
        self.canvas_img_saturation_value.grid(row=1, column=0)
        #A second canvas to change the hue
        self.canvas_img_hue = Canvas(Selected_color, width=20, height=100, bd=0, highlightthickness=0, relief='flat')
        self.canvas_img_hue.grid(row=1, column=1)



        #Bellow the clickable canvas, we have Entries allowing to display teh values or write them directly.
        self.canvas_choice_couleurs = Canvas(self.canvas_user, width=10, height=10, bd=0, highlightthickness=0,relief='flat')
        self.canvas_choice_couleurs.grid(row=2, column=0, sticky="ns")
        # Hue
        self.hue_name = Label(self.canvas_choice_couleurs, text="Hue:")
        self.hue_name.grid(row=0, column=0, sticky="e")
        self.hue_bot = Entry(self.canvas_choice_couleurs)
        self.hue_bot.bind("<Return>",self.update_show)
        self.hue_bot.grid(row=0, column=1)
        self.hue_top = Entry(self.canvas_choice_couleurs)
        self.hue_top.grid(row=0, column=2)
        self.hue_top.bind("<Return>", self.update_show)
        # Saturation
        self.sat_name = Label(self.canvas_choice_couleurs, text="Saturation:")
        self.sat_name.grid(row=1, column=0, sticky="e")
        self.sat_bot = Entry(self.canvas_choice_couleurs)
        self.sat_bot.grid(row=1, column=1)
        self.sat_bot.bind("<Return>", self.update_show)
        self.sat_top = Entry(self.canvas_choice_couleurs)
        self.sat_top.grid(row=1, column=2)
        self.sat_top.bind("<Return>", self.update_show)
        # Value
        self.val_name = Label(self.canvas_choice_couleurs, text="Value:")
        self.val_name.grid(row=2, column=0, sticky="e")
        self.val_bot = Entry(self.canvas_choice_couleurs)
        self.val_bot.grid(row=2, column=1)
        self.val_bot.bind("<Return>", self.update_show)
        self.val_top = Entry(self.canvas_choice_couleurs)
        self.val_top.grid(row=2, column=2)
        self.val_top.bind("<Return>", self.update_show)

        #A button to reset the selection of color (i.e. nothind is selected and user can use "Ctrl-click")
        bouton_Reset = Button(self.canvas_choice_couleurs, text="Reset color values", fg="white", bg="red",
                                         command=partial(self.empty_proj, redo=True))
        bouton_Reset.grid(row=0, column=3, rowspan=3, sticky="nswe")

        #Under the manual entries, we have a validate button which will confirm entries values and update the currrent image display
        bouton_Valider = Button(self.canvas_choice_couleurs, text="Validate", fg="white", bg="green", command=partial(self.update_show, True))
        bouton_Valider.grid(row=3, column=0, columnspan=2, sticky="nswe")
        #A "validate all" button is here to apply these parameters to all the images of the project
        bouton_Valider_all = Button(self.canvas_choice_couleurs, text="Validate all", fg="white", bg="orange",
                                         command=self.validate_all)
        bouton_Valider_all.grid(row=3, column=2, columnspan=2, sticky="nswe")



        ##Bellow the color selection, we find the Tool informations. The tool is how the user interact with the current image
        self.Frame_Tool_param = Canvas(self.canvas_user, height=20, bd=2, highlightthickness=1, relief='flat')
        self.Frame_Tool_param.grid(row=3, column=0, sticky="ns")

        #The tool size can be changed
        self.scale_tool_size = Scale(self.Frame_Tool_param, label="Tool size", from_=3, to=500, resolution=1,
                                     orient=HORIZONTAL, length=200, command=self.Change_tool_size)
        self.scale_tool_size.grid(row=0, column=2)
        self.scale_tool_size.set(50)

        #The tool can either increase the selection area ("Add"), or decrease it ("Remove")
        Add = Radiobutton(self.Frame_Tool_param, text="Add", indicatoron=0, width=10, variable=self.tool_add,
                               value=1, command=lambda: self.Change_add(True))
        Remove = Radiobutton(self.Frame_Tool_param, text="Remove", indicatoron=0, width=10, variable=self.tool_add, value=0, command=lambda: self.Change_add(False))
        Add.grid(row=0, column=0, sticky="s")
        Remove.grid(row=0, column=1, sticky="s")

        #The tool can be a pencil (i.e. the user is simply drawing on the image), or a polygon (i.e. the user define a polygon shape)
        Pencil_button = Radiobutton(self.Frame_Tool_param, text="Pencil", indicatoron=1, width=10,
                                       variable=self.tool_type, value="Pencil")
        Poly_butt = Radiobutton(self.Frame_Tool_param, text="Polygon", indicatoron=1, width=10,
                                     variable=self.tool_type, value="Poly")
        Pencil_button.grid(row=1, column=0, sticky="s")
        Poly_butt.grid(row=1, column=1, sticky="s")

        #The user can be selecting the target itself, or one of the color reference
        Frame_Tool_Choice = Frame(self.canvas_user, height=20, bd=2, highlightthickness=1, relief='flat')
        Frame_Tool_Choice.grid(row=4, column=0, sticky="ns")

        self.which_tool = StringVar()
        self.which_tool.set("Target")  # possible options: "Fish", "Red","Blue","Yellow","White"
        tool_Fish = Radiobutton(Frame_Tool_Choice, text="Target", indicatoron=0, width=10,
                                     variable=self.which_tool, value="Target")
        tool_Scale_R = Radiobutton(Frame_Tool_Choice, text="Red ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Red")
        tool_Scale_B = Radiobutton(Frame_Tool_Choice, text="Blue ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Blue")
        tool_Scale_Y = Radiobutton(Frame_Tool_Choice, text="Yellow ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="Yellow")
        tool_Scale_W = Radiobutton(Frame_Tool_Choice, text="White ref", indicatoron=0, width=10,
                                        variable=self.which_tool, value="White")
        tool_Fish.grid(row=0, column=0)
        tool_Scale_R.grid(row=0, column=1)
        tool_Scale_B.grid(row=0, column=2)
        tool_Scale_Y.grid(row=0, column=3)
        tool_Scale_W.grid(row=0, column=4)

        ###The Miniature Canvas shows all the images from the project. It allow to have a fast view of everything and b=navigate easily.
        self.Can_Miniature = Canvas(self.canvas_user, height=10, bd=2, highlightthickness=1, relief='groove', background="orange")
        self.Can_Miniature.grid(row=5, column=0, sticky="ns")
        #The main Canvas containing the displayed image
        self.Can_Miniature_img = Canvas(self.Can_Miniature, height=10, bd=2, highlightthickness=1, relief='flat')
        self.Can_Miniature_img.grid(row=0, column=0, sticky="ns")
        self.Can_Miniature_img.bind("<Button-1>", self.callback_miniature)
        self.Can_Miniature_img.bind_all("<MouseWheel>", self.On_mousewheel)
        #We have a scrollbar allowing to move the miniature canvas around (not a real movement of the canvas image as it would require too much memory, it fakes the movement)
        self.defilement = IntVar()
        self.defilement.set(250)
        self.scale_tool_size = Scale(self.Can_Miniature, showvalue=0, from_=250, to=self.SizeMin[0] - 1, resolution=1, variable=self.defilement, orient=VERTICAL, length=250, command=self.defile)
        self.scale_tool_size.grid(row=0, column=1)
        self.scale_tool_size.set(250)
        #We have a button to update this miniature canvas because auto-update would be unnecessarily time-consuming
        self.update_min = Button(self.Can_Miniature, text="Update_view", command=self.afficher_min)
        self.update_min.grid(row=1, column=0)



        #We finally prepare the project
        self.empty_proj() # This function is used at initiation and later to close projects
        self.shown_col = [int(self.hue_bot.get()), 0]        # Variable keeping the hue value to be displayed and corresponding Y position in "self.canvas_img_hue"
        self.update()
        self.update_show() # Update the canvas to show colors



    def change_auto_part(self):
        '''This function change the automatic particle fiinder mode from activated to disabled.
        The particle finder update the particle display on the current frame, if auto is on, it will be changed each time the user modify something.
        If off (savec computer power), only when user click the validate button'''
        self.auto_update= not self.auto_update #Flag for on/off

        #Update visual of the menubar
        if self.auto_update:
            text="Auto update of particles ✔"
        else:
            text="Auto update of particles"
        self.optionsmenu.entryconfig(0, label=text)

        #We update the programs settings accordingly so it will remember user choice
        Param_file = User_loading.resource_path(os.path.join("Settings"))
        with open(Param_file, 'wb') as fp:
            pickle.dump([self.auto_update], fp)


    def empty_proj(self, redo=False):
        '''Change the values for when there is no project open
        redo: boolean, True= all the data will have to be redone, False=we keep the scale data'''
        #Minimum values everywhere
        self.hue_bot.delete(0, END)
        self.hue_bot.insert(0, "0")
        self.hue_top.delete(0, END)
        self.hue_top.insert(0, "1")

        self.sat_bot.delete(0, END)
        self.sat_bot.insert(0, "0")
        self.sat_top.delete(0, END)
        self.sat_top.insert(0, "0")

        self.val_bot.delete(0, END)
        self.val_bot.insert(0, "0")
        self.val_top.delete(0, END)
        self.val_top.insert(0, "0")

        if not redo:#If redo, we reset all values, of not we keep the previous scale values
            self.Entry_dist.delete(0, END)
            self.Entry_dist.insert(0, "1")
        else:
            self.update_show()


    def create_project(self):
        '''Create a new project from scratch'''
        self.empty_proj()#Prepare GUI
        self.Datas_generales=[]#Where the data will be saved
        self.Images_names=[]#Names of all image files
        self.Images=[]#Images themselves
        self.save_as()#Save the new project somewhere
        self.update_show()#Update color show
        self.prepare_GUI_with_proj()#Prepare GUI
        self.modif_image()#Prepare and display a blank image
        self.afficher_min()#Prepare the miniature


    def On_mousewheel(self,event):
        '''The miniature can be moved along with the mousewheel'''
        if len(self.Images)>0:
            if event.widget == self.Can_Miniature_img:#If the mouse is abose the miniature
                new_pos=self.defilement.get() - (event.delta / 10)
                if new_pos > 250 and new_pos <self.SizeMin[0]:#if we are not higher than max, lower than min
                    self.defilement.set(new_pos)
                    self.scale_tool_size.set(new_pos)
                    self.defile(int(new_pos))



    def callback_miniature(self, event):
        '''What happen when the miniature is pressed'''
        Position = self.defilement.get() - (250 - event.y)#Position relative to teh miniature
        possible_Pos = [*range(int(self.SizeMin[0] / len(self.Images)), self.SizeMin[0]+1, int(self.SizeMin[0] / len(self.Images)))]
        for Poss in range(len(possible_Pos)):
            if Position < possible_Pos[Poss]:
                if self.Current_img != Poss:
                    self.Current_img = Poss
                    self.pt_Poly = []
                    self.pt_selected = None
                #We then update the "Next/Previous" buttons
                if self.Current_img < (len(self.Images) - 1):
                    self.Image_suiv.config(state="normal")
                else:
                    self.Image_suiv.config(state="disabled")

                if self.Current_img == 0:
                    self.Image_prec.config(state="disabled")
                else:
                    self.Image_prec.config(state="normal")

                self.canvas_main_img.name=self.Images_names[self.Current_img]
                self.modif_image()
                break

    def defile(self, val):
        #We update the miniature
        if len(self.Images) > 0:
            val = int(val)
            self.cutted_Miniature = self.Miniature[(val - 250):val, 0:self.SizeMin_cut[1]]
            self.min_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cutted_Miniature))
            self.can_min = self.Can_Miniature_img.create_image(0, 0, image=self.min_show, anchor=NW)
            self.Can_Miniature_img.config(width=int(self.SizeMin_cut[1]), height=int(self.SizeMin_cut[0]))
            self.Can_Miniature_img.itemconfig(self.can_min, image=self.min_show)
            self.update()

    def modif_image(self, show=None):
        self.img_to_show=self.transfo_img(self.Current_img)
        tmp_img = self.img_to_show.copy()
        if not show is None:
            tmp_img = cv2.circle(tmp_img, show, self.tool_size, (255, 0, 0),
                                 max([1, int(2 * self.canvas_main_img.ratio)]))
        self.canvas_main_img.afficher_img(tmp_img)


    def transfo_img(self, image_ID):
        if len(self.Images)>0:
            overlay = np.zeros(self.Images[image_ID].shape, dtype=np.uint8)
            for target in range(len(self.Datas_generales[image_ID]["Particles"])):
                if len(self.Datas_generales[image_ID]["Particles"][target])>0:
                    overlay = cv2.drawContours(overlay, self.Datas_generales[image_ID]["Particles"][target][0], -1, (0, 0, 255), -1)
            opacity = 0.75

            TMP_image = np.copy(self.Images[image_ID])

            # Echelle
            TMP_image = cv2.line(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][0]),
                                 tuple(self.Datas_generales[image_ID]["Scale"][1]), (255, 0, 150), max([1,int(2*self.canvas_main_img.ratio)]))
            TMP_image = cv2.circle(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][0]),
                                   max([1,int(5*self.canvas_main_img.ratio)]), (255, 0, 0), max([1,int(2*self.canvas_main_img.ratio)]))
            TMP_image = cv2.circle(TMP_image, tuple(self.Datas_generales[image_ID]["Scale"][1]),
                                   max([1,int(5*self.canvas_main_img.ratio)]), (255, 0, 0), max([1,int(2*self.canvas_main_img.ratio)]))

            # Selection_Poly
            for pt in range(len(self.pt_Poly)):
                TMP_image = cv2.circle(TMP_image, tuple(self.pt_Poly[pt]), max([1,int(10*self.canvas_main_img.ratio)]), (0, 255, 0), -1)
                if pt > 0:
                    TMP_image = cv2.line(TMP_image, tuple(self.pt_Poly[pt - 1]), tuple(self.pt_Poly[pt]), (0, 255, 0), max([1,int(2*self.canvas_main_img.ratio)]))

            TMP_image = cv2.addWeighted(TMP_image, 1, overlay, opacity, 0)

            if self.Datas_generales[image_ID]["Target"][0] is not None:
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Target"][0], -1, (250, 0, 0), max([1,int(2*self.canvas_main_img.ratio)]))

            if self.Datas_generales[image_ID]["Particles"] is not None:
                for target in range(len(self.Datas_generales[image_ID]["Particles"])):
                    if len(self.Datas_generales[image_ID]["Particles"][target]) > 0:
                        TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Particles"][target][0], -1, (0, 0, 250), max([1,int(1*self.canvas_main_img.ratio)]))

            if len(self.Datas_generales[image_ID]["Red"]) > 0 and self.Datas_generales[image_ID]["Red"][0] is not None:
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Red"][0], -1, (150, 0, 0), max([1,int(4*self.canvas_main_img.ratio)]))

            if len(self.Datas_generales[image_ID]["Blue"]) > 0 and self.Datas_generales[image_ID]["Blue"][0] is not None:
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Blue"][0], -1, (0, 0, 150), max([1,int(4*self.canvas_main_img.ratio)]))

            if len(self.Datas_generales[image_ID]["Yellow"]) > 0 and self.Datas_generales[image_ID]["Yellow"][0] is not None:
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["Yellow"][0], -1, (150, 150, 2), max([1,int(4*self.canvas_main_img.ratio)]))

            if len(self.Datas_generales[image_ID]["White"]) > 0 and self.Datas_generales[image_ID]["White"][0] is not None:
                TMP_image = cv2.drawContours(TMP_image, self.Datas_generales[image_ID]["White"][0], -1, (200, 200, 200), max([1,int(4*self.canvas_main_img.ratio)]))

            return (TMP_image)
        else:
            return(self.blank)

    def afficher_min(self):
        min_width=400
        if len(self.Images) > 0:
            for ImG in range(len(self.Images)):
                if ImG == 0:
                    TMP_min = self.transfo_img(ImG)
                    ratio=TMP_min.shape[1]/min_width
                    TMP_min=cv2.resize(TMP_min,[min_width,int(TMP_min.shape[0]/ratio)])
                    name = self.Images_names[ImG].split("/")[-1]
                    TMP_min = cv2.putText(TMP_min, name, (10, TMP_min.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                          (255, 255, 255), 3, cv2.LINE_AA)
                    TMP_min = cv2.putText(TMP_min, name, (10, TMP_min.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                          (0, 0, 0), 1, cv2.LINE_AA)
                    self.Miniature = TMP_min
                else:
                    TMP_min = self.transfo_img(ImG)
                    ratio=TMP_min.shape[1]/min_width
                    TMP_min=cv2.resize(TMP_min,[min_width,int(TMP_min.shape[0]/ratio)])
                    name = self.Images_names[ImG].split("/")[-1]
                    TMP_min = cv2.putText(TMP_min, name, (10, TMP_min.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                          (255, 255, 255), 3, cv2.LINE_AA)
                    TMP_min = cv2.putText(TMP_min, name, (10, TMP_min.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                          (0, 0, 0), 1, cv2.LINE_AA)
                    self.Miniature = np.concatenate((self.Miniature, TMP_min), axis=0)

            SizeMin = self.Miniature.shape
            self.cutted_Miniature = self.Miniature[self.defilement.get() - 250: self.defilement.get(), 0:SizeMin[1]]
            self.SizeMin_cut = self.cutted_Miniature.shape

            self.min_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cutted_Miniature))
            self.can_min = self.Can_Miniature_img.create_image(0, 0, image=self.min_show, anchor=NW)
            self.Can_Miniature_img.config(width=int(self.SizeMin_cut[1]), height=int(self.SizeMin_cut[0]))
            self.Can_Miniature_img.itemconfig(self.can_min, image=self.min_show)

        else:
            self.Can_Miniature_img.delete("all")


    def moved_can_right(self, pos, event):
        self.moved_can(pos, event,invert=True)

    def moved_can(self, pos, event, invert=False):
        if not bool(event.state & 0x0001) and not bool(event.state & 0x0004):
            pos=list(pos)
            pos[0]=int(pos[0])
            pos[1] = int(pos[1])
            if self.pt_selected != None:
                if self.pt_selected == 1:
                    self.Datas_generales[self.Current_img]["Scale"][0][0] = pos[0]
                    self.Datas_generales[self.Current_img]["Scale"][0][1] = pos[1]
                    self.modif_image()
                elif self.pt_selected == 2:
                    self.Datas_generales[self.Current_img]["Scale"][1][0] = pos[0]
                    self.Datas_generales[self.Current_img]["Scale"][1][1] = pos[1]
                    self.modif_image()

                elif self.pt_selected > 2:
                    self.pt_Poly[self.pt_selected - 3][0] = pos[0]
                    self.pt_Poly[self.pt_selected - 3][1] = pos[1]
                    self.modif_image()

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
                    mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()][0], -1, (255), -1)
                cv2.line(mask, pos, self.last_pt, (color), int(self.tool_size*2))
                New_cnts = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts

            self.last_pt=pos

            self.modif_image(show=pos)



    def released_can(self, event):
        self.pt_selected = None
        self.last_pt=None
        if self.auto_update:
            self.validate()

        self.modif_image()

    def Change_add(self, type=None):
        if not isinstance(type, (bool)):
            self.tool_add.set(not self.tool_add.get())
        else:
            self.tool_add.set(type)

    def validate(self):
        if len(self.Images) > 0:
            self.Datas_generales[self.Current_img]["Particles"]=[]
            for target in range(len(self.Datas_generales[self.Current_img]["Target"][0])):
                if self.Datas_generales[self.Current_img]["Target"][1][0][target][3] == -1:
                    self.Datas_generales[self.Current_img]["Particles"].append(Fun.find_particles(self.Images[self.Current_img],
                                                                         self.Datas_generales[self.Current_img]["Target"],target, (
                                                                         int(float(self.hue_bot.get()) / 2),
                                                                         int(float(self.hue_top.get()) / 2)), (
                                                                         (int(float(self.sat_bot.get()))),
                                                                         int(float(self.sat_top.get()))), (
                                                                         int(float(self.val_bot.get())),
                                                                         int(float(self.val_top.get())))))
            self.modif_image()
        self.update()

    def update_show(self, force_auto=False, *args):
        if self.auto_update or force_auto:
            self.validate()
        Size = self.img_colors.shape

        if int(self.hue_bot.get()) < int(self.hue_top.get()):
            if not ((self.shown_col[0])>=int(self.hue_bot.get()) and (self.shown_col[0])<=int(self.hue_top.get())):
                self.shown_col=[int(self.hue_bot.get()),0]
        else:
            if ((self.shown_col[0])>=int(self.hue_bot.get()) and (self.shown_col[0])<=int(self.hue_top.get())):
                self.shown_col=[int(self.hue_bot.get()),0]

        self.img_colors_new = np.copy(self.img_colors)
        self.img_colors_new_r = cv2.resize(self.img_colors_new, (int(Size[1] * self.ratio_col), int(Size[0] * self.ratio_col)))
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

        self.TMP_img_col = cv2.resize(self.img_colors_new, (int(Size[1] * self.ratio_col), int(Size[0] * self.ratio_col)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)

        #Display saturation chart
        saturations=self.saturations.copy()
        self.sat3=cv2.line(saturations, (0,int(self.sat_bot.get())),(int(self.canvas_img_sat.winfo_width()),int(self.sat_bot.get())),(200,200,200),2)
        self.sat3 = cv2.line(saturations, (0, int(self.sat_top.get())),(int(self.canvas_img_sat.winfo_width()), int(self.sat_top.get())), (50, 50, 50), 2)
        self.sat3=cv2.resize(self.sat3,(int(self.canvas_img_sat.winfo_width()),int(self.canvas_img_val.winfo_height())))
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
        if event.y<0:
            event.y=0
        if int(event.y/self.sat_ratio)>255:
            event.y=int(255*self.sat_ratio)
        rgb = np.uint8([[self.saturations[int(round(event.y/self.sat_ratio)),1]]])  # shape: (1,1,3)
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
        if event.y<0:
            event.y=0
        if int(event.y/self.val_ratio)>255:
            event.y=int(255*self.val_ratio)
        rgb = np.uint8([[self.values[int(round(event.y/self.val_ratio)),1]]])  # shape: (1,1,3)
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
        load_frame = Loading.Loading(self.frame_main)  # Progression bar
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

        self.TMP_img_col = cv2.resize(self.img_colors_new, (int(Size[1] * self.ratio_col), int(Size[0] * self.ratio_col)))
        self.col_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_img_col))
        self.can_col = self.canvas_img_couleurs.create_image(0, 0, image=self.col_show, anchor=NW)
        self.canvas_img_couleurs.config(width=int(Size[1] * self.ratio_col), height=int(Size[0] * self.ratio_col))
        self.canvas_img_couleurs.itemconfig(self.can_col, image=self.col_show)


        if len(self.Images) > 0:
            for img in range(len(self.Datas_generales)):
                load_frame.show_load(img/len(self.Datas_generales))
                self.Datas_generales[img]["Particles"]=[]

                for target in range(len(self.Datas_generales[img]["Target"][0])):
                    if self.Datas_generales[self.Current_img]["Target"][1][0][target][3] == -1:
                        self.Datas_generales[img]["Particles"].append( Fun.find_particles(self.Images[img], self.Datas_generales[img]["Target"],target, (
                        int(float(self.hue_bot.get()) / 2), int(float(self.hue_top.get()) / 2)), (
                                                                     (int(float(self.sat_bot.get()))),
                                                                     int(float(self.sat_top.get()))), (
                                                                     int(float(self.val_bot.get())),
                                                                     int(float(self.val_top.get())))))
            self.afficher_min()
            self.modif_image()
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

    def mouse_over(self, pos):
        tmp_img=self.img_to_show.copy()
        tmp_img=cv2.circle(tmp_img,pos,self.tool_size,(255,0,0),max([1,int(2*self.canvas_main_img.ratio)]))
        self.affiche_mouse(pos)
        self.canvas_main_img.afficher_img(tmp_img)


    def pressed_can(self, pos, event, invert=False):
        X = int(pos[0])
        Y = int(pos[1])
        if bool(event.state & 0x0001) and not bool(event.state & 0x0004):#If Shift is pressed
            rgb = np.uint8([[self.Images[self.Current_img][int(Y), int(X)]]])  # shape: (1,1,3)
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[0, 0]
            hsv=np.uint16(hsv)

            if abs(int(self.hue_bot.get())-int(self.hue_top.get()))<=1:
                new_bot=(hsv[0] * 2)-2
                if new_bot<0:
                    new_bot=360-new_bot
                self.hue_bot.delete(0, END)
                self.hue_bot.insert(0, str(new_bot))

                new_top=(hsv[0] * 2)+2
                if new_top>360:
                    new_top=new_top-360
                self.hue_top.delete(0, END)
                self.hue_top.insert(0, str(new_top))

            else:
                #Change Hue
                diff_bot=min([abs((360-int(self.hue_bot.get()))+(int(hsv[0])*2)),abs((360-(int(hsv[0])*2))+int(self.hue_bot.get())),abs((int(hsv[0])*2)-int(self.hue_bot.get()))])
                diff_top=min([abs((360-int(self.hue_top.get()))+(int(hsv[0])*2)),abs((360-(int(hsv[0])*2))+int(self.hue_top.get())),abs((int(hsv[0])*2)-int(self.hue_top.get()))])

                diffs=[diff_bot,diff_top]
                which_bt=diffs.index(min(diffs))

                if which_bt==0:
                    min_diff=min([abs((360-int(self.hue_bot.get()))+(int(hsv[0])*2)),abs((360-(int(hsv[0])*2))+int(self.hue_bot.get()))])
                    diff_loop=min_diff<abs((int(hsv[0])*2)-int(self.hue_bot.get()))
                    new_lower_old=int((hsv[0])*2)<int(self.hue_bot.get())
                    if invert:
                        new_lower_old = not new_lower_old

                    if (not diff_loop and new_lower_old) or (diff_loop and not new_lower_old):
                            self.hue_bot.delete(0, END)
                            self.hue_bot.insert(0, str(hsv[0]*2))
                else:
                    min_diff = min([abs((360 - int(self.hue_top.get())) + (int(hsv[0]) * 2)),
                                    abs((360 - (int(hsv[0]) * 2)) + int(self.hue_top.get()))])
                    diff_loop=min_diff<abs((int(hsv[0])*2)-int(self.hue_top.get()))
                    new_higher_old=int((hsv[0])*2)>int(self.hue_top.get())

                    if invert:
                        new_higher_old = not new_higher_old

                    if (not diff_loop and new_higher_old) or (diff_loop and not new_higher_old):
                        self.hue_top.delete(0, END)
                        self.hue_top.insert(0, str(hsv[0]*2))

            #Change Sat:
            if abs(int(self.sat_bot.get())-int(self.sat_top.get()))<=1:
                self.sat_bot.delete(0, END)
                self.sat_bot.insert(0, str(max(0,hsv[1]-1)))

                self.sat_top.delete(0, END)
                self.sat_top.insert(0, str(min(255,hsv[1]+1)))
            else:
                if hsv[1]<int(self.sat_bot.get()):
                    self.sat_bot.delete(0, END)
                    self.sat_bot.insert(0, str(hsv[1]))
                elif hsv[1]>int(self.sat_top.get()):
                    self.sat_top.delete(0, END)
                    self.sat_top.insert(0, str(hsv[1]))

            #Change Val:
            if abs(int(self.val_bot.get()) - int(self.val_top.get())) <= 1:
                self.val_bot.delete(0, END)
                self.val_bot.insert(0, str(max(0, hsv[2] - 1)))

                self.val_top.delete(0, END)
                self.val_top.insert(0, str(min(255, hsv[2] + 1)))
            else:
                if hsv[2]<int(self.val_bot.get()):
                    self.val_bot.delete(0, END)
                    self.val_bot.insert(0, str(hsv[2]))
                elif hsv[2]>int(self.val_top.get()):
                    self.val_top.delete(0, END)
                    self.val_top.insert(0, str(hsv[2]))

            self.update_show()

        elif not bool(event.state & 0x0001) and not bool(event.state & 0x0004):
            if math.sqrt((X - self.Datas_generales[self.Current_img]["Scale"][0][0]) ** 2 + (Y - self.Datas_generales[self.Current_img]["Scale"][0][1]) ** 2) < 20:
                self.pt_selected = 1
            elif math.sqrt((X - self.Datas_generales[self.Current_img]["Scale"][1][0]) ** 2 + (Y - self.Datas_generales[self.Current_img]["Scale"][1][1]) ** 2) < 20:
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
                    mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()][0], -1, (255), -1)

                cv2.circle(mask, (int(X), int(Y)),self.tool_size, (color), -1)
                New_cnts = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts
                self.last_pt=[int(X), int(Y)]
            self.modif_image(show=[int(X), int(Y)])


    def right_click(self, pos, event):
        self.pressed_can(pos, event, invert=True)

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
            mask = cv2.drawContours(mask, self.Datas_generales[self.Current_img][self.which_tool.get()][0], -1, (255), -1)
        pts = np.array(self.pt_Poly, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.drawContours(mask, [pts], -1, color, -1)
        New_cnts = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        self.Datas_generales[self.Current_img][self.which_tool.get()] = New_cnts

        self.pt_Poly = []
        self.pt_selected = None
        self.modif_image([X,Y])


    def close(self):
        self.projectmenu.entryconfig(2, state="disabled")
        self.projectmenu.entryconfig(3, state="disabled")
        self.projectmenu.entryconfig(4, state="disabled")

        self.prepare_GUI_without_proj()

        self.project_open=False




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
            self.canvas_main_img.name = self.Images_names[self.Current_img]
            self.modif_image()

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
            self.canvas_main_img.name = self.Images_names[self.Current_img]
            self.modif_image()

    def affiche_mouse(self, pos):
        try:
            if len(self.Images) > 0:
                X = pos[0]
                Y = pos[1]

                rgb = np.uint8([[self.Images[self.Current_img][Y,X]]])  # shape: (1,1,3)
                hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[0,0]
                hsv = np.uint16(hsv)

                self.position_mouse_x.set("X="+str(X))
                self.position_mouse_y.set("Y=" + str(Y))
                self.position_mouse_h.set("Hue=" + str(hsv[0]*2))
                self.position_mouse_s.set("Sat=" + str(hsv[1]))
                self.position_mouse_v.set("Val=" + str(hsv[2]))

        except:
            pass

    def save(self, *args):
        Params=[self.hue_bot.get(), self.hue_top.get(), self.sat_bot.get(), self.sat_top.get(),self.val_bot.get(),self.val_top.get(),self.distance.get()]
        with open(self.file_project_save, 'wb') as fp:
            pickle.dump((self.Datas_generales, self.Images_names, Params, self.param_find_targets), fp)

    def save_as(self):
        self.file_project_save = filedialog.asksaveasfilename(defaultextension=".rfd")
        self.root.title(os.path.basename(self.file_project_save)[0:-4] + " - ColCal")
        self.save()

    def open_file(self):
        self.canvas_main_img.unbindings()

        self.file_project_save = filedialog.askopenfilename()
        with open(self.file_project_save, 'rb') as fp:
            self.Datas_generales, self.Images_names, Params, Params_target = pickle.load(fp)

        load_frame = Loading.Loading(self.frame_main)  # Progression bar
        load_frame.show_load(0)
        self.load_images(load_frame)
        load_frame.destroy()

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

        self.param_find_targets=Params_target
        self.distance.set(Params[6])

        if len(self.Images_names)>0:
            self.canvas_main_img.name=self.Images_names[self.Current_img]
            self.canvas_main_img.update_image(self.Images[self.Current_img])
        else:
            self.canvas_main_img.name="No image"
            self.canvas_main_img.update_image(self.blank)

        self.update_show()
        self.afficher_min()
        self.update()
        self.prepare_GUI_with_proj()

        self.canvas_main_img.bindings()


    def prepare_GUI_with_proj(self):
        self.project_open = True
        self.root.title(os.path.basename(self.file_project_save)[0:-4] + " - ColCal")
        self.projectmenu.entryconfig(2, state="active")
        self.projectmenu.entryconfig(3, state="active")
        self.projectmenu.entryconfig(4, state="active")

        self.canvas_main_img.grid(row=0, column=0, sticky="nswe")
        self.Can_Miniature_img.grid(row=0, column=0, sticky="nsew")

        self.menubar.entryconfig("Images", state="active")

        if len(self.Images)>0:
            self.menubar.entryconfig("Detection", state="active")
            self.Current_img=0
        else:
            self.menubar.entryconfig("Detection", state="disabled")
            self.Current_img = 0

    def prepare_GUI_without_proj(self):
        self.project_open = False
        self.root.title(os.path.basename(self.file_project_save)[0:-4] + " - ColCal")
        self.projectmenu.entryconfig(2, state="disabled")
        self.projectmenu.entryconfig(3, state="disabled")
        self.projectmenu.entryconfig(4, state="disabled")

        self.canvas_main_img.grid_forget()
        self.Can_Miniature_img.grid_forget()

        self.menubar.entryconfig("Images", state="disabled")
        self.menubar.entryconfig("Detection", state="disabled")

        self.Entry_dist.delete(0, END)
        self.Entry_dist.insert(0, "1")
        self.Current_img = 0

    def remove_image(self):
        self.Images_names.pop(self.Current_img)
        self.Datas_generales.pop(self.Current_img)

        load_frame = Loading.Loading(self.frame_main)  # Progression bar
        load_frame.show_load(0)
        self.load_images(load_frame)
        load_frame.destroy()


    def remove_selection(self,selected_indices):
        for i in sorted(selected_indices, reverse=True):
            self.Images_names.pop(i)
            self.Datas_generales.pop(i)

        load_frame = Loading.Loading(self.frame_main)  # Progression bar
        load_frame.show_load(0)
        self.load_images(load_frame)
        load_frame.destroy()

    def remove_images(self):
        newWindow = Toplevel(self.root)
        interface = Vid_list.Interface_vid_list(parent=newWindow, list_vids=self.Images_names, on_confirm=self.remove_selection)



    def add_images(self):
        self.canvas_main_img.unbindings()
        files = filedialog.askopenfilenames()

        load_frame = Loading.Loading(self.frame_main)  # Progression bar
        load_frame.show_load(0)

        done=0
        for file in files:
            load_frame.show_load((done/len(files))*0.1)
            file=str(file)
            if os.path.isfile(file) and imghdr.what(file):
                self.Images_names.append(file)

            Actual_fish_cnt = [[],[]]
            pt1, pt2 = [[25,50],[100,50]]
            Actual_particles = []
            Actual_yellow_scale = []
            Actual_blue_scale = []
            Actual_red_scale = []
            Actual_white_scale = []
            self.Datas_generales.append(
                {"Target": Actual_fish_cnt, "Particles": Actual_particles, "Scale": [pt1, pt2],
                 "Yellow": Actual_yellow_scale, "Blue": Actual_blue_scale,
                 "Red": Actual_red_scale, "White": Actual_white_scale, "File": file})
            done+=1

        self.load_images(load_frame)
        self.modif_image()
        self.afficher_min()
        self.update()

        self.prepare_GUI_with_proj()

        self.canvas_main_img.grid(row=0, column=0, sticky="nsew")
        self.Can_Miniature_img.grid(row=0, column=0, sticky="nsew")
        self.modif_image()
        self.canvas_main_img.bindings()



    def load_images(self,load_frame):
        self.Images = []
        first = True
        compteur = -1
        count=0
        if len(self.Images_names)>0:
            for file in self.Images_names:
                load_frame.show_load(0.5+0.5*(count/len(self.Images_names)))
                compteur = compteur + 1
                ImG = cv2.imread(file)
                ImG = cv2.cvtColor(ImG, cv2.COLOR_BGR2RGB)
                self.Images.append(ImG)

                min_width=400

                if first:
                    ImG = self.transfo_img(compteur)
                    ratio=ImG.shape[1]/min_width
                    ImG=cv2.resize(ImG,[min_width,int(ImG.shape[0]/ratio)])
                    self.Miniature = ImG
                    first = False
                else:
                    ImG = self.transfo_img(compteur)
                    ratio=ImG.shape[1]/min_width
                    ImG=cv2.resize(ImG,[min_width,int(ImG.shape[0]/ratio)])
                    self.Miniature = np.concatenate((self.Miniature, ImG), axis=0)
                count+=1

            self.Current_img = 0
            self.SizeMin = self.Miniature.shape
            self.cutted_Miniature = self.Miniature[0:250, 0:self.SizeMin[1]]
            self.SizeMin_cut = self.cutted_Miniature.shape
            self.scale_tool_size.configure(to=self.SizeMin[0] - 1)
            self.afficher_min()
        load_frame.destroy()

    def automated_findings(self):
        newWindow = Toplevel(self.root.master)
        interface = Auto_detection.Auto_param_interface(parent=newWindow, list_vids=self.Images_names, boss=self, curr_vid=self.Current_img)


    def find_hue_range(self, all_Hs, p1=1,p2=99):
        bins = [i for i in range(11, 1, -1) if 180 % i == 0]
        bin_pos = 0
        minimum_fund = False
        while not minimum_fund:
            hist_data = np.histogram(all_Hs, bins[bin_pos], [0, 180])
            nb_min = np.sum(hist_data[0] == np.min(hist_data[0]))
            if nb_min <= 1:
                minimum_fund = True
                to_add = int(hist_data[1][np.argmin(hist_data[0])] + bins[bin_pos])
            elif bin_pos == len(bins) - 1:
                to_add = 0
                minimum_fund = True
            bin_pos += 1

        all_Hs = np.array(all_Hs)  # convert to numpy array if it is currently a list
        all_Hs[all_Hs < to_add] += 180

        mean_h = np.mean(all_Hs)
        if mean_h >= 180:
            mean_h = mean_h - 180

        low_h = np.percentile(all_Hs, p1)
        if low_h >= 180:
            low_h = low_h - 180
        high_h = np.percentile(all_Hs, p2)
        if high_h >= 180:
            high_h = high_h - 180

        split_range = low_h > high_h

        return (split_range, [low_h, high_h], mean_h)

    def save_particles(self):
        Extracting_particles.save_particles(self, self.Datas_generales, self.distance, self.Images)

window = Tk()
window.title("No project - ColCal")
interface = Interface(window)
interface.mainloop()
