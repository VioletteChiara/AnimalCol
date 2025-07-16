from tkinter import *
import numpy as np
import cv2
import time
import PIL.Image, PIL.ImageTk
import os
import math
from PIL import ImageFont, ImageDraw, Image
import copy



class Image_show(Frame):
    """
    A class inherited from TkFrame that will contain the video reader.
    It allows to visualize the video, zoom in/out, move in the video time space (with a time-bar) and interact with its
    containers (higher level classes) through bindings on the image canvas.
    """

    def __init__(self, parent, boss, img, name, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(borderwidth=0, highlightthickness=0, background="blue")
        self.img=img
        self.last_img=self.img
        self.boss=boss
        self.no_zoom=False
        self.name=name

        self.canvas_video = Canvas(self, highlightthickness=0, borderwidth=0, background="pink")
        self.canvas_video.grid(row=0, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)

        self.canvas_video.focus_set()

        #For zoom:
        self.zoom_strength = 1.25
        self.zoom_sq = [0, 0, self.img.shape[1], self.img.shape[0]]#We want to show the whole frames if we are in the cropping process
        self.Size=self.img.shape

        self.ratio = 1#How much do we zoom in
        self.ZinSQ = [-1, ["NA", "NA"]]#used to zoom in a particular area

        self.bindings()


    def update_ratio(self, *args):
        '''Calculate the ratio between the original size of the video and the displayed image'''
        self.ratio=max((self.zoom_sq[2]-self.zoom_sq[0])/self.canvas_video.winfo_width(),(self.zoom_sq[3]-self.zoom_sq[1])/self.canvas_video.winfo_height())


    def update_image(self, img):
        self.img=img
        self.zoom_sq = [0, 0, self.img.shape[1], self.img.shape[0]]
        self.boss.modif_image()


    def Zoom(self, event, Zin=True):
        '''When the user hold <Ctrl> and click on the frame, zoom on the image.
        If <Ctrl> and right click, zoom out'''
        if not bool(event.state & 0x1):
            self.new_zoom_sq = [0, 0, self.Size[1], self.Size[0]]
            event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
            event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
            PX = event.x / self.Size[1]
            PY = event.y / self.Size[0]

            if self.ZinSQ[0]<3:
                if Zin:
                    new_total_width = self.Size[1] / self.ratio * self.zoom_strength
                    new_total_height = self.Size[0] / self.ratio * self.zoom_strength
                else:
                    new_total_width = self.Size[1] / self.ratio / self.zoom_strength
                    new_total_height = self.Size[0] / self.ratio / self.zoom_strength

                if new_total_width>self.canvas_video.winfo_width():
                    missing_px=new_total_width - (self.canvas_video.winfo_width()-5)
                    ratio_old_new=self.Size[1]/new_total_width
                    self.new_zoom_sq[0] = int(PX * missing_px*ratio_old_new)
                    self.new_zoom_sq[2] = int(self.Size[1] - ((1 - PX) * missing_px*ratio_old_new))

                if new_total_height>self.canvas_video.winfo_height():
                    missing_px=new_total_height - (self.canvas_video.winfo_height()-5)
                    ratio_old_new=self.Size[0]/new_total_height
                    self.new_zoom_sq[1] = int(PY * missing_px*ratio_old_new)
                    self.new_zoom_sq[3] = int(self.Size[0] - ((1 - PY) * missing_px*ratio_old_new))

                if self.new_zoom_sq[3]-self.new_zoom_sq[1] > 50 and self.new_zoom_sq[2]-self.new_zoom_sq[0]>50:
                    self.zoom_sq = self.new_zoom_sq
                    self.update_ratio()
                    self.boss.modif_image()

            elif event.x>=0 and event.x<=self.Size[1] and event.y>=0 and event.y<=self.Size[0] and self.ZinSQ[1][0]>=0 and self.ZinSQ[1][0]<=self.Size[1] and self.ZinSQ[1][1]>=0 and self.ZinSQ[1][1]<=self.Size[0]:
                zoom_sq = [min(self.ZinSQ[1][0], event.x), min(self.ZinSQ[1][1], event.y) , max(self.ZinSQ[1][0], event.x), max(self.ZinSQ[1][1], event.y)]
                if not self.no_zoom:
                    if (zoom_sq[2] - zoom_sq[0]) > 50 and (zoom_sq[3] - zoom_sq[1])>50:
                        self.zoom_sq=zoom_sq
                        self.update_ratio()
                        self.boss.modif_image()
                else:
                    try:
                        self.boss.select_no_zoom(zoom_sq)
                    except:
                        pass

                self.ZinSQ = [-1, ["NA", "NA"]]

            self.canvas_video.delete("Rect")



    def Sq_Zoom_beg(self, event):
        event_t_x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event_t_y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        self.ZinSQ=[0,[event_t_x,event_t_y],[event.x,event.y]]
        self.canvas_video.delete("Rect")


    def Sq_Zoom_mov(self,event):
        self.canvas_video.delete("Rect")

        event_t_x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event_t_y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        zoom_sq = [min(self.ZinSQ[1][0], event_t_x), min(self.ZinSQ[1][1], event_t_y), max(self.ZinSQ[1][0], event_t_x),max(self.ZinSQ[1][1], event_t_y)]
        if not self.no_zoom:
            colors = ["white","red","black"]
        else:
            colors = ["green","green","black"]

        if (zoom_sq[2] - zoom_sq[0]) > 50 and (zoom_sq[3] - zoom_sq[1])>50 and event_t_x>=0 and event_t_x<=self.Size[1] and event_t_y>=0 and event_t_y<=self.Size[0] and self.ZinSQ[1][0]>=0 and self.ZinSQ[1][0]<=self.Size[1] and self.ZinSQ[1][1]>=0 and self.ZinSQ[1][1]<=self.Size[0]:
            self.canvas_video.create_rectangle(self.ZinSQ[2][0], self.ZinSQ[2][1], event.x, event.y, outline=colors[0], tags="Rect")
        else:
            self.canvas_video.create_rectangle(self.ZinSQ[2][0], self.ZinSQ[2][1], event.x, event.y, outline=colors[1], tags="Rect")
        self.canvas_video.create_rectangle(self.ZinSQ[2][0],self.ZinSQ[2][1],event.x,event.y, dash=(3,3), outline=colors[2], tags="Rect")

        if self.ZinSQ[0]>=0:
            self.ZinSQ[0]+=1



    def bindings(self):
        '''Make all the bindings'''
        self.canvas_video.bind("<Control-B1-Motion>", self.Sq_Zoom_mov)
        self.canvas_video.bind("<Control-B1-ButtonRelease>", lambda x: self.Zoom(event=x,Zin=True))
        self.canvas_video.bind("<Control-B3-ButtonRelease>", lambda x: self.Zoom(event=x,Zin=False))
        self.canvas_video.bind("<Configure>", lambda x: self.boss.modif_image())
        self.boss.root.bind("<Map>", lambda x: self.afficher_img(self.last_img))
        # Visualisation de la video
        self.canvas_video.bind("<space>", self.boss.Change_add)

        self.canvas_video.bind("<Shift-B1-Motion>", lambda x: self.callback_move(event=x,Shift=True))
        self.canvas_video.bind("<B1-Motion>", self.callback_move)
        self.canvas_video.bind("<B3-Motion>", self.callback_move_right)
        self.canvas_video.bind("<Motion>", self.mouse_over)
        self.canvas_video.bind("<B1-ButtonRelease>", self.release)
        self.canvas_video.bind("<B3-ButtonRelease>", self.release_right)
        self.canvas_video.bind("<Button-3>", self.right_click)
        self.canvas_video.bind("<Button-1>", self.callback)

    def unbindings(self):
        '''Remove all the bindings'''
        try:
            self.canvas_video.unbind("<Control-1>")
            self.canvas_video.unbind("<Control-3>")
            self.canvas_video.unbind("<Shift-1>")
            self.canvas_video.unbind("<Configure>")

            self.canvas_video.unbind("<Motion>")
            self.canvas_video.unbind("<Button-1>")
            self.canvas_video.unbind("<B1-Motion>")
            self.canvas_video.bind("<B1-ButtonRelease>")
            self.canvas_video.bind("<B3-ButtonRelease>")

        except:
            pass

    def mouse_over(self, event):
        try:
            event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
            event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
            self.boss.mouse_over([event.x,event.y])
        except:#IF teh parent does not have a mouse_over function
            pass

    def callback(self, event):
        '''When we press on the frame, the info about where the frame was clicked is sent to the Video Reader container'''
        if not bool(event.state & 0x1) and bool(event.state & 0x4):
            self.Sq_Zoom_beg(event)

        else:
            event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
            event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
            self.boss.pressed_can((event.x,event.y), event)


    def callback_move_right(self, event, *args):
        '''The info about where the frame was clicked is sent to the Video Reader container'''
        self.last_event_move = copy.copy(event)
        event.x = self.ratio * (event.x - (self.canvas_video.winfo_width() - self.shape[1]) / 2) + self.zoom_sq[0]
        event.y = self.ratio * (event.y - (self.canvas_video.winfo_height() - self.shape[0]) / 2) + self.zoom_sq[1]

        if event.x < 0:
            event.x = 0

        if event.y < 0:
            event.y = 0

        if event.x >= self.Size[1]:
            event.x = self.Size[1]

        if event.y >= self.Size[0]:
            event.y = self.Size[0]

        self.boss.moved_can_right((event.x, event.y), event)


    def callback_move(self, event=None, Shift=False, *args):
        '''The info about where the frame was clicked is sent to the Video Reader container'''
        self.last_event_move=copy.copy(event)
        event.x = self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2) + self.zoom_sq[0]
        event.y = self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2) + self.zoom_sq[1]

        if event.x<0:
            event.x=0

        if event.y < 0:
            event.y=0

        if event.x>=self.Size[1]:
            event.x=self.Size[1]

        if event.y >= self.Size[0]:
            event.y = self.Size[0]

        self.boss.moved_can((event.x,event.y), event)

    def right_click(self, event):
        if not (event.state & 0x4):
            '''The info about where the frame was clicked is sent to the Video Reader container'''
            event.x = self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2) + self.zoom_sq[0]
            event.y = self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2) + self.zoom_sq[1]
            if  event.x >= 0 and event.y >= 0 and event.x <= self.Size[1] and event.y <= self.Size[0]:
                self.boss.right_click((event.x,event.y), event)

    def release_right(self, event):
        self.release(event, invert=True)

    def release(self, event, invert=False):
        '''The info about where the frame was clicked is sent to the Video Reader container'''
        event.x = self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2) + self.zoom_sq[0]
        event.y = self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2) + self.zoom_sq[1]
        try:
            self.boss.released_can((event.x,event.y),invert)
        except:
            pass
        self.moving_pt_interest=False


    def afficher_img(self, img):
        '''Once the image is adapted by the video container, it is here resized and displayed'''
        self.update_ratio()
        self.last_img=img.copy()
        if not self.Size==img.shape:
            self.Size = img.shape
            self.zoom_sq = [0, 0, self.Size[1], self.Size[0]]  # If not, we show the cropped frames

        image_to_show2 = img[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        width=int((self.zoom_sq[2]-self.zoom_sq[0])/self.ratio)
        height=int((self.zoom_sq[3]-self.zoom_sq[1])/self.ratio)


        TMP_image_to_show2 = cv2.resize(image_to_show2,(width, height))
        self.shape= TMP_image_to_show2.shape

        img2=TMP_image_to_show2

        img2 = cv2.putText(img2, os.path.basename(self.name), (10, img2.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                              (255, 255, 255), 3, cv2.LINE_AA)
        img2 = cv2.putText(img2, os.path.basename(self.name), (10, img2.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                              (0, 0, 0), 1, cv2.LINE_AA)

        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2))
        self.can_import = self.canvas_video.create_image((self.canvas_video.winfo_width()-self.shape[1])/2, (self.canvas_video.winfo_height()-self.shape[0])/2, image=self.image_to_show3, anchor=NW)
        self.canvas_video.config(height=self.shape[1],width=self.shape[0])
        self.canvas_video.itemconfig(self.can_import, image=self.image_to_show3)
        self.update_idletasks()


