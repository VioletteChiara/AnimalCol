from os import stat_result
from scipy.stats.contingency import crosstab
from tkinter import *
import PIL
import PIL.ImageTk, PIL.Image
import cv2
import numpy as np
import math
from scipy.interpolate import splprep, splev
import os


import Loading

class Auto_param_interface(Frame):
    """ This is a small Frame in which the user can define the nomber of targets per arena, in the case the number is variable between arenas."""
    def __init__(self, parent, list_vids, boss, curr_vid, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)

        self.percentile_bot=0.5
        self.percentile_top = 99.5

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.grid(sticky="nsew")

        parent.grab_set()  # Prevents interaction with other windows
        parent.focus_set()  # Sets keyboard focus to this window

        self.boss=boss
        self.list_vids=list_vids
        self.parent=parent



        Grid.rowconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 1, weight=1000)
        Grid.rowconfigure(self, 2, weight=1000)
        Grid.columnconfigure(self, 0, weight=5)
        Grid.columnconfigure(self, 1, weight=1)


        #List of images:
        self.holder=StringVar()
        Optn_vids=OptionMenu(self, self.holder, *list_vids, command=self.change_img)
        Optn_vids.grid(row=0,column=0,columnspan=2)
        self.holder.set(list_vids[curr_vid])
        self.img_name=self.holder.get()


        #Image to show results
        self.Image_can=Canvas(self)
        self.Image_can.grid(row=1,column=0, rowspan=2, sticky="nsew")
        self.Image_can.bind("<Button-1>", self.callback)

        self.change_img(list_vids[0], show=False)
        self.all_Hs = self.boss.param_find_targets[6][0]
        self.all_Ss = self.boss.param_find_targets[6][1]
        self.all_Vs = self.boss.param_find_targets[6][2]

        params=self.boss.param_find_targets


        #Parameters
        Image_param=Frame(self)
        Image_param.grid(row=1,column=1, sticky="nsew")
        Grid.columnconfigure(Image_param, 0, weight=1)

        Label(Image_param, text="Parameters", font=("Arial", 18), background="Royalblue").grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.ero1=IntVar()
        self.ero1.set(params[0])
        Scale_Ero1=Scale(Image_param,variable=self.ero1, from_=0, to=20, orient=HORIZONTAL, label="Erosion 1", command=self.update_target)
        Scale_Ero1.grid(row=1, column=0, sticky="nsew")

        self.dil=IntVar()
        self.dil.set(params[1])
        Scale_Dil=Scale(Image_param,variable=self.dil, from_=0, to=20, orient=HORIZONTAL, label="Dilation", command=self.update_target)
        Scale_Dil.grid(row=2, column=0, sticky="nsew")

        self.ero2=IntVar()
        self.ero2.set(params[2])
        Scale_Ero2=Scale(Image_param,variable=self.ero2, from_=0, to=20, orient=HORIZONTAL, label="Erosion 2", command=self.update_target)
        Scale_Ero2.grid(row=3, column=0, sticky="nsew")

        self.min_size=IntVar()
        self.min_size.set(params[3])
        Scale_MinSize=Scale(Image_param,variable=self.min_size, from_=0, to=int((self.image_or.shape[1]*self.image_or.shape[0])/25), orient=HORIZONTAL, label="Min size", command=self.update_target)
        Scale_MinSize.grid(row=4, column=0, sticky="nsew")

        self.max_size=IntVar()
        self.max_size.set(params[4])
        Scale_MaxSize=Scale(Image_param,variable=self.max_size, from_=0, to=self.image_or.shape[1]*self.image_or.shape[0], orient=HORIZONTAL, label="Max size", command=self.update_target)
        Scale_MaxSize.grid(row=5, column=0, sticky="nsew")

        self.smooth=DoubleVar()
        self.smooth.set(params[5])
        Scale_smooth=Scale(Image_param,variable=self.smooth, from_=0, to=10, resolution=0.1, orient=HORIZONTAL, label="Smoothing", command=self.update_target)
        #Scale_smooth.grid(row=6, column=0, columnspan=2, sticky="nsew")

        #Backrpund half
        Label(Image_param, text="Background color", font=("Arial", 14)).grid(row=1, column=1, sticky="nsew")
        self.Canvas_back_col = Canvas(Image_param, background="red", width=50, height=100)
        self.Canvas_back_col.grid(row=2, rowspan=3, column=1, sticky="nsew")
        Button(Image_param, text="Reset", command=self.reset_back).grid(row=5, column=1, sticky="nsew")


        #List of videos
        Video_list = Frame(self)
        Grid.columnconfigure(Video_list, 0, weight=1)
        Grid.rowconfigure(Video_list, 0, weight=1)  # Make row 1 expandable for the canvas
        Grid.rowconfigure(Video_list, 1, weight=1)  # Make row 1 expandable for the canvas
        Grid.rowconfigure(Video_list, 2, weight=100)  # Make row 1 expandable for the canvas
        Grid.rowconfigure(Video_list, 3, weight=1)  # Make row 1 expandable for the canvas
        Video_list.grid(row=2, column=1, sticky="nsew")

        Label(Video_list, text="Videos", font=("Arial", 18), background="Royalblue").grid(row=0, column=0, columnspan=2, sticky="nsew")
        Button(Video_list, text="Select all", command=self.select_all).grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Create canvas and scrollbar
        Canvas_liste = Canvas(Video_list, width=300, height=150)
        Canvas_liste.grid(row=2, column=0, sticky="nsew")

        scrollbar = Scrollbar(Video_list, orient="vertical", command=Canvas_liste.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")

        Canvas_liste.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the checkbuttons
        checkbutton_frame = Frame(Canvas_liste)

        # Create window inside canvas
        canvas_window = Canvas_liste.create_window((0, 0), window=checkbutton_frame, anchor='nw')

        self.vid_buttons = []
        for pos_row, Vid in enumerate(list_vids):
            var = BooleanVar()
            self.vid_buttons.append(var)
            chk = Checkbutton(checkbutton_frame, text=os.path.basename(Vid), variable=var)
            chk.grid(row=pos_row, column=0, sticky="w")

        self.vid_buttons[curr_vid].set(True)
        Button(Video_list, text="Validate", font=("Arial", 18), background="green", command=self.validate).grid(row=3, column=0, columnspan=2, sticky="nsew")

        # Update scrollregion when the frame changes size
        def on_frame_configure(event):
            Canvas_liste.configure(scrollregion=Canvas_liste.bbox("all"))

        # Optional: Make canvas expand with window resize
        def on_canvas_configure(event):
            # Update the inner frame's width to fill canvas
            canvas_width = event.width
            Canvas_liste.itemconfig(canvas_window, width=canvas_width)

        checkbutton_frame.bind("<Configure>", on_frame_configure)
        Canvas_liste.bind("<Configure>", on_canvas_configure)
        self.after(200, lambda: (
            self.change_img(self.holder.get()),
            self.update_img()
        ))
        self.update_idletasks()
        self.update()
        self.parent.bind("<Configure>", self.change_size)


    def change_size(self, *args):
        self.update_img()

    def show_col(self):
        if len(self.all_Hs)>0:
            empty=np.zeros([100,100,3], np.uint8)
            
            split_range, ranges_hue, _ = self.boss.find_hue_range(self.all_Hs.copy(), self.percentile_bot, self.percentile_top)
            if not split_range:
                mean=np.mean([ranges_hue[0],ranges_hue[1]])
            else:
                mean=ranges_hue[0]+((180-ranges_hue[0])+ranges_hue[1])/2
                if mean>180:
                    mean=mean-180

            empty[:, :, 0] = mean

            min_S=int(np.percentile(self.all_Ss,self.percentile_bot))
            max_S=int(np.percentile(self.all_Ss,self.percentile_top))
            values = np.uint8(np.linspace(min_S, max_S, 100))  # 100 values from min_V to max_V
            empty[:, 0:99, 1] = np.tile(values[:, np.newaxis], (1, 99))  # Repeat across columns

            min_V=int(np.percentile(self.all_Vs,self.percentile_bot))
            max_V=int(np.percentile(self.all_Vs,self.percentile_top))
            values = np.uint8(np.linspace(min_V, max_V, 100))  # 100 values from min_V to max_V
            empty[:, 0:99, 2] = np.tile(values[:, np.newaxis], (1, 99))  # Repeat across columns

            vertical_col_band = np.zeros([10, 100, 3], np.uint8)
            vertical_col_band[:, :, 1] = int(
                np.mean([int(np.percentile(self.all_Ss, self.percentile_bot)), int(np.percentile(self.all_Ss, self.percentile_top))]))
            vertical_col_band[:, :, 2] = int(
                np.mean([int(np.percentile(self.all_Vs, self.percentile_bot)), int(np.percentile(self.all_Vs, self.percentile_top))]))

            if not split_range:
                values = np.uint8(np.linspace(ranges_hue[0], ranges_hue[1], 100))  # 100 values from min_H to max_H
            else:
                prop1 = (180 - ranges_hue[0]) / ((180 - ranges_hue[0]) + ranges_hue[1])
                line1 = np.linspace(ranges_hue[0], 180, round(100 * prop1))
                line2 = np.linspace(0, ranges_hue[1], 100 - round(100 * prop1))
                values = np.concatenate([line1, line2])

            # Fill horizontal hue gradient across 100 columns
            vertical_col_band[:, :, 0] = np.tile(values, (10, 1))  # Repeat the gradient row-wise
            empty = np.vstack([empty, vertical_col_band])
            empty=cv2.cvtColor(empty, cv2.COLOR_HSV2RGB)

        else:
            empty = np.zeros([110, 100, 3], np.uint8)
            empty[:, :] = [255, 0, 0]  # HSV or BGR depending on context

        self.back_col = cv2.resize(empty, (int(self.Canvas_back_col.winfo_width()), int(self.Canvas_back_col.winfo_height())))
        self.back_col2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.back_col))
        self.Canvas_back_col.create_image(0, 0, image=self.back_col2, anchor=NW)
        self.Canvas_back_col.update()
        self.update()


    def select_all(self):
        nb_ok=np.sum([val.get() for val in self.vid_buttons])
        if nb_ok==len(self.vid_buttons):
            state=False
        else:
            state=True

        for check in self.vid_buttons:
            check.set(state)

    def validate(self):
        load_frame = Loading.Loading(self.parent)  # Progression bar
        load_frame.show_load(0)
        for vid in range(len(self.vid_buttons)):
            if self.vid_buttons[vid].get():
                img, cnt = self.find_target(img=cv2.imread(self.list_vids[vid]))
                self.boss.Datas_generales[vid]["Target"] = [[cnt],[[[-1,-1,-1,-1]]]]
                self.boss.Datas_generales[vid]["Particles"] = [[],[]]
            load_frame.show_load(vid/len(self.vid_buttons))

        load_frame.destroy()

        self.boss.param_find_targets=[self.ero1.get(),self.dil.get(),self.ero2.get(),self.min_size.get(),self.max_size.get(),self.smooth.get(), [self.all_Hs, self.all_Ss, self.all_Vs]]

        self.boss.afficher_min()
        self.boss.update_show()
        self.parent.grab_release()  # Prevents interaction with other windows
        self.parent.destroy()

    def update_target(self, *args):
        self.image_to_show, _ = self.find_target(self.image_or.copy())
        self.update_img()

    def reset_back(self):
        self.all_Hs=[]
        self.all_Ss=[]
        self.all_Vs=[]
        self.update_target()

    def change_img(self, im_name, show=True):
        self.image_or=cv2.imread(im_name)
        self.hsv=cv2.cvtColor(self.image_or,cv2.COLOR_BGR2HSV)
        self.image_to_show=self.image_or.copy()
        if show:
            self.update_target()


    def update_img(self, *args):
        img=self.image_to_show

        # Step 2: Get canvas size
        canvas_width = self.Image_can.winfo_width()
        canvas_height = self.Image_can.winfo_height()
        good_ratio = 1

        # Wait until canvas is fully rendered if width or height is 1
        if canvas_width < 2 or canvas_height < 2:
            self.Image_can.update()
            canvas_width = self.Image_can.winfo_width()
            canvas_height = self.Image_can.winfo_height()

        ratio_w=img.shape[1]/canvas_width
        ratio_h=img.shape[0]/canvas_height
        self.scale_ratio= max(ratio_w,ratio_h)

        if int(img.shape[1]/self.scale_ratio)>1 and int(img.shape[0]/self.scale_ratio)>1:
            # Step 3: Resize image to fit canvas
            img = cv2.resize(img, (int(img.shape[1]/self.scale_ratio), int(img.shape[0]/self.scale_ratio)), interpolation=cv2.INTER_AREA)

            # Step 4: Convert BGR (OpenCV) to RGB (PIL)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_image = PIL.Image.fromarray(img_rgb)
            tk_image = PIL.ImageTk.PhotoImage(image=pil_image)

            # Step 5: Display the image on the canvas
            self.Image_can.image = tk_image  # Keep a reference to avoid garbage collection
            self.Image_can.create_image(0, 0, image=tk_image, anchor=NW)

            self.show_col()


    def smooth_contour_spline(self, contour, smoothness=5.0, num_points=100, closed=True):
        points = contour[:, 0, :].astype(np.float32)

        if closed:
            points = np.vstack([points, points[0]])

        m = len(points)
        if m < 2:
            return contour  # Can't do anything
        k = min(3, m - 1)  # Adjust spline degree to number of points

        try:
            tck, u = splprep(points.T, s=smoothness, per=int(closed), k=k)
            u_fine = np.linspace(0, 1, num_points)
            x_fine, y_fine = splev(u_fine, tck)
            smoothed = np.array([[[int(x), int(y)]] for x, y in zip(x_fine, y_fine)], dtype=np.int32)
            return smoothed
        except Exception as e:
            print(f"Spline smoothing failed: {e}")
            return contour


    def find_target(self, event=None, img=None):
        final_cnt=None
        if len(self.all_Hs)>0:
            if not img is None:
                img=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            else:
                img=self.hsv.copy()

            split_range, ranges_hue, _ = self.boss.find_hue_range(self.all_Hs.copy(),self.percentile_bot,self.percentile_top)

            if not split_range:
                lowers = np.array([ranges_hue[0],np.percentile(self.all_Ss,self.percentile_bot),np.percentile(self.all_Vs,self.percentile_bot)], dtype=np.uint8)
                uppers = np.array([ranges_hue[1],np.percentile(self.all_Ss,self.percentile_top),np.percentile(self.all_Vs,self.percentile_top)], dtype=np.uint8)
                Binary_image = cv2.inRange(img, lowers, uppers)
            else:
                lowers = np.array([ranges_hue[0],np.percentile(self.all_Ss,self.percentile_bot),np.percentile(self.all_Vs,self.percentile_bot)], dtype=np.uint8)
                uppers = np.array([180,np.percentile(self.all_Ss,self.percentile_top),np.percentile(self.all_Vs,self.percentile_top)], dtype=np.uint8)
                Binary_image1 = cv2.inRange(img, lowers, uppers)
                lowers = np.array([0,np.percentile(self.all_Ss,self.percentile_bot),np.percentile(self.all_Vs,self.percentile_bot)], dtype=np.uint8)
                uppers = np.array([ranges_hue[1],np.percentile(self.all_Ss,self.percentile_top),np.percentile(self.all_Vs,self.percentile_top)], dtype=np.uint8)
                Binary_image2 = cv2.inRange(img, lowers, uppers)

                Binary_image=cv2.bitwise_or(Binary_image1,Binary_image2)


            Binary_image = cv2.bitwise_not(Binary_image)

            kernel = np.ones((3,3), np.uint8)

            Binary_image = cv2.erode(Binary_image, kernel, iterations=self.ero1.get())
            Binary_image = cv2.dilate(Binary_image, kernel, iterations=self.dil.get())
            Binary_image = cv2.erode(Binary_image, kernel, iterations=self.ero2.get())


            cnts,_=cv2.findContours(Binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        else:
            cnts=[]

        new_cnts=[]
        dist_to_center=[]
        for cnt in cnts:
            surf=cv2.contourArea(cnt)
            if surf>self.min_size.get() and surf<self.max_size.get():

                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    new_cnts.append(cnt)
                    dist_to_center.append(math.sqrt(math.pow(cx-(self.image_or.shape[1]/2),2)+math.pow(cy-(self.image_or.shape[0]/2),2)))
                else:
                    # Contour area is zero (degenerate), fallback to another method
                    pass

        image_to_show=self.image_or.copy()
        if len(new_cnts)>0:
            final_cnt = new_cnts[dist_to_center.index(min(dist_to_center))]
            if self.smooth.get() > 0.000001:
                final_cnt = self.smooth_contour_spline(final_cnt, smoothness=self.smooth.get())
                final_cnt = self.smooth_contour_spline(final_cnt, smoothness=self.smooth.get())

            back = image_to_show.copy()
            cv2.drawContours(back, cnts, -1, (0, 0, 255), -1)
            cv2.drawContours(back, [final_cnt], 0, (255, 0, 255), -1)


            # blend with original image
            alpha = 0.25
            image_to_show = cv2.addWeighted(image_to_show, 1 - alpha, back, alpha, 0)
            cv2.drawContours(image_to_show, [final_cnt], 0, (255, 0, 255), 2)

        return(image_to_show, final_cnt)



    def callback(self, event):
        # Convert canvas coords to image coords
        x_img = int(event.x * self.scale_ratio)
        y_img = int(event.y * self.scale_ratio)

        #img
        mask=np.zeros((self.image_or.shape[0],self.image_or.shape[1]),np.uint8)
        mask=cv2.circle(mask, [x_img,y_img],10,255,-1)

        self.all_Hs=self.all_Hs+self.hsv[mask == 255, 0].tolist()
        self.all_Ss=self.all_Ss+self.hsv[mask == 255, 1].tolist()
        self.all_Vs=self.all_Vs+self.hsv[mask == 255, 2].tolist()

        self.update_target()
