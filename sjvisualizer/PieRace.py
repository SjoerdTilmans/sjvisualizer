from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
from sjvisualizer.Canvas import _from_rgb
from tkinter import *
from PIL import Image
import io
from tkinter import font
import datetime
import time
import math
from PIL import Image, ImageTk
import copy
import pandas as pd
import random
import operator
import os
import ctypes
import json
import platform

from screeninfo import get_monitors

months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

random_colors = [(102,155,188),(168,198,134),(243,167,18),(41,51,92),(228,87,46),(255,155,113),(255,253,130),(45,48,71),(237,33,124),(27,153,139),(245,213,71),(219,48,105),(20,70,160),(0,0,200),(0,200,0),(200,0,0),(66,217,200),(44,140,153),(50,103,113),(40,70,75),(147,22,33),(208,227,127),(221,185,103),(209,96,61),(34,29,35),(97,87,113),(81,70,99),(77,83,130),(202,207,133),(140,186,128),(101,142,156)]

if platform.system() == "Windows":
    SCALEFACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
elif platform.system() == "Darwin": # if OS is mac
    SCALEFACTOR = 1
elif platform.system() == "Linux": # if OS is linux
    SCALEFACTOR = 1
else: # if OS can't be detected
    SCALEFACTOR = 1

# SCALEFACTOR = 0.75

min_slice = 0.0001
min_slice_image = 0.001
min_slice_percentage_display = 0.01
decimal_places = 1
text_font = "Microsoft JhengHei UI"
min_color = 20
max_color = 225
UNDERLINE = 0
LINE_END_SPACING = 25
BUBBLE_CHART_INCREMENTS = 20
MAX_A = 4
BUBBLE_PICTURE_SIZE = 0.2
MIN_BUBBLE_DISTANCE = 0
MIN_BUBBLE_FONT = 10
BUBBLE_TOP = 20 # number of bubbles to display
format_str = '%d-%m-%Y'  # The format

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class pie_plot(sub_plot):
    """
    Class to construct a pie chart race

    :param canvas: tkinter canvas to draw the graph to
    :type canvas: tkinter.Canvas

    :param width: width of the plot in pixels, default depends on screen resolution
    :type width: int

    :param height: height of the plot in pixels, default depends on screen resolution
    :type height: int

    :param x_pos: the x location of the top left pixel in this plot, default depends on screen resolution
    :type x_pos: int

    :param y_pos: the y location of the top left pixel in this plot, default depends on screen resolution
    :type y_pos: int

    :param df: pandas dataframe that holds the data
    :type df: pandas.DataFrame

    :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
    corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
        {
            "United States": [
                23,
                60,
                225
            ]
        }, default is {}
    :type colors: dict

    :param back_ground_color: color of the background. To hide bars that fall outside of the top X, a square is drawn
    at the bottom of the visualization. Typically you want this square to match the color of the background. Default is (255,255,255)
    :type back_ground_color: tuple of length 3 with integers

    :param font_color: font color, default is (0,0,0)
    :type font_color: tuple of length 3 with integers

    :param sort: should the values of this plot be softed? True/False, default is True
    :type sort: boolean
    """

    def draw(self, time):
        self.pies = {}
        if self.sort:
            data = self._get_data_for_frame(time).sort_values(ascending=False)
        else:
            data = self._get_data_for_frame(time)

        if self.sort == True:
            scale_labels = True
        else:
            scale_labels = False

        start = 0
        for i, (name, value) in enumerate(data.items()):
            if not name == "Other" and not name == "Others":
                fraction = value/data.sum()
                if isinstance(self.colors, dict):
                    if name in self.colors:
                        color = self.colors[name]
                    else:
                        color = self._set_color(name)
                else:
                    color = self._set_color(name)

                if i < 200:
                    load_img = True
                else:
                    load_img = False

                self.pies[name] = pie(name=name, canvas=self.canvas, x1=self.x_pos + self.width/2 - 0.4*self.height, y1=self.y_pos + 0.1*self.height, x2=self.x_pos + self.width/2 + 0.4*self.height, y2=self.y_pos + 0.9*self.height, color=color, start=start, extent=360*fraction, root=self.root, display_percentages=self.display_percentages, display_label=self.display_label, colors=self.colors, load_img=load_img, font_color=self.font_color, scale_label=scale_labels)
                if fraction > min_slice:
                    start = start + fraction * 360

        self.pies["Other"] = pie(name="Other", canvas=self.canvas, x1=self.x_pos + self.width / 2 - 0.4 * self.height, y1=self.y_pos + 0.1 * self.height,
                               x2=self.x_pos + self.width / 2 + 0.4 * self.height, y2=self.y_pos + 0.9 * self.height,
                               color=(200, 200, 200), start=start, extent=360-start, root=self.root, display_percentages=self.display_percentages, display_label=self.display_label, font_color=self.font_color, scale_label=scale_labels)

        self.white = self.canvas.create_oval(self.x_pos + self.width / 2 - 0.2 * self.height, self.y_pos + 0.3 * self.height,
                                        self.x_pos + self.width / 2 + 0.2 * self.height, self.y_pos + 0.7 * self.height,
                                        fill=_from_rgb(self.back_ground_color), outline="")


    def _set_color(self, name):
        if self.sjcanvas and self.sjcanvas.color_palette:
            color = self.sjcanvas.color_palette[0]
            self.sjcanvas.color_palette.pop(0)
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                           random.randint(min_color + 30, max_color)))

        self.color = cv._from_rgb(color)
        self.colors[name] = color

        return color

    def update(self, time):
        if self.sort:
            data = self._get_data_for_frame(time).sort_values(ascending=False)
        else:
            data = self._get_data_for_frame(time)

        start = 0
        for name, value in data.items():
            if not name == "Other" and not name == "Others":
                fraction = value / data.sum()
                if fraction > min_slice:
                    self.pies[name].update(target_start=start, target_extent=360*fraction)
                    start = start + 360*fraction
                else:
                    self.pies[name].update(target_start=start, target_extent=0)

        self.pies["Other"].update(target_start=start, target_extent=360 - start)
        self.canvas.tag_raise(self.white)

class pie():

    def __init__(self, name=None, canvas=None, x1=0, y1=0, x2=0, y2=0, start=0, extent=0, color=None, root=None, display_percentages=True, display_label=True, colors = None, load_img=True, font_color=(0, 0, 0), scale_label=True):
        self.name = name
        self.canvas = canvas
        self.target_start = start
        self.target_extend = extent

        self.load_img = load_img

        self.colors = colors

        size = y2 - y1
        self.size = size

        self.display_label = display_label
        self.display_percentages = display_percentages

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.scale_label = scale_label

        self.start = start
        self.extent = extent
        self.v1 = 0
        self.v2 = 0
        self.a1 = 0
        self.a2 = 0

        self.stiffness = 0.06
        self.damping = 0.35
        self.mass = 1

        self.font_color = font_color

        if self.load_img:
            try:
                self.imgs = {}
                print("Loading images for {}".format(self.name))
                for i in range(int(self.size/7.5/min_slice_image*min_slice), int(self.size/7.5) + 1):
                    self.imgs[i] = load_image(os.path.join("assets", self.name.replace("*", "") + ".png"), i, i, root, name)
            except:
                self.imgs = None
        else:
            self.imgs = None


        if color:
            self.color1 = _from_rgb(tuple(color))
            self.color2 = _from_rgb(tuple((color[0] - 20, color[1] - 20, color[2] - 50)))
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color), random.randint(min_color + 30, max_color)))
            self.color1 = _from_rgb(color)
            self.color2 = _from_rgb(tuple((color[0] - 20, color[1] - 20, color[2] - 50)))

            if colors:
                colors[name] = color

        self.draw(start=self.start, extent=self.extent)

    def draw(self, start=0, extent=0):
        self.obj_ID1 = self.canvas.create_arc(self.x1, self.y1, self.x2, self.y2, fill=self.color1, start=start, extent=extent, outline="")
        self.obj_ID2 = self.canvas.create_arc(self.x1 + self.size / 5, self.y1 + self.size / 5, self.x2 - self.size / 5, self.y2 - self.size / 5,
                                              fill=self.color2, start=start, extent=extent, outline="")

        self.font = font.Font(family=text_font, size=int((12 + self.size / 75) / SCALEFACTOR), weight="bold")
        self.font2 = font.Font(family=text_font, size=int((8 + self.size / 100) / SCALEFACTOR), weight="bold")

        x_dir = math.sin((90 - (self.extent + 2 * self.start) / 2) / 360 * 2 * math.pi)
        y_dir = math.cos((90 - (self.extent + 2 * self.start) / 2) / 360 * 2 * math.pi)

        if self.extent > 360 * min_slice:
            if self.display_label:
                self.line = self.canvas.create_line((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 120) * x_dir,
                                                    (self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 120) * y_dir,
                                                    (self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 30) * x_dir,
                                                    (self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 30) * y_dir,
                                                    width=int(3 + self.size / 300), fill="grey")
                if self.extent > min_slice_percentage_display * 360 or not self.scale_label:
                    self.text = self.canvas.create_text(((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 10) * x_dir,
                                                         (self.y1 + self.y2) / 2 - (
                                                                     self.size / 2 + self.size / 10) * y_dir),
                                                        text=self.name, font=self.font, fill=_from_rgb(self.font_color))
                else:
                    self.font_temp = font.Font(family=text_font, size=int((16 + self.size / 100) / SCALEFACTOR * self.extent / (0.5 * min_slice_percentage_display * 360 + 0.5 * self.extent)),
                                          weight="bold")
                    self.text = self.canvas.create_text(
                        ((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 10) * x_dir,
                         (self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 10) * y_dir),
                        text=self.name, font=self.font_temp, fill=_from_rgb(self.font_color))

                if self.display_percentages:
                    if self.extent > min_slice_percentage_display * 360:
                        self.text2 = self.canvas.create_text(
                            (    (self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 10) * x_dir,
                             int((self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 10) * y_dir) + self.size / 30 + 15),
                                                             text=format(self.extent / 360 * 100,
                                                                         ",.{}f".format(decimal_places)) + "%",
                                                             font=self.font2, fill="grey")
                    else:
                        self.text2 = self.canvas.create_text(
                            ((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 30) * x_dir,
                             (self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 30) * y_dir),
                            text="", font=self.font2, fill="grey")
        else:
            if self.display_label:
                self.line = self.canvas.create_line(0, 0, 0, 0, width=int(3 + self.size / 300), fill="grey")
                self.text = self.canvas.create_text(((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 15) * x_dir,
                                                     (self.y1 + self.y2) / 2 - (
                                                                 self.size / 2 + self.size / 15) * y_dir),
                                                    text="", font=self.font, fill=_from_rgb(self.font_color))

                if self.display_percentages:
                    self.text2 = self.canvas.create_text(
                        ((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 15) * x_dir,
                         (self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 15) * y_dir),
                        text="", font=self.font2, fill="grey")
        if self.imgs:
            percentage = self.extent / 360
            if percentage > min_slice_image:
                self.image_file = self.imgs[int(self.size / 7.5)]
            elif percentage < min_slice:
                self.image_file = self.imgs[int(self.size/7.5/min_slice_image*(min_slice))]
            else:
                self.image_file = self.imgs[int(self.size/7.5/min_slice_image*(percentage))]
            if self.extent > 360 * min_slice:
                self.img = self.canvas.create_image((self.x1 + self.x2) / 2 + (self.size / 2.5) * x_dir,
                                                    (self.y1 + self.y2) / 2 - (self.size / 2.5) * y_dir,
                                                    image=self.image_file)
            else:
                self.img = self.canvas.create_image(-1000,
                                                    -1000,
                                                    image=self.image_file)

            # self.canvas.tag_lower(self.img)
        else:
            self.img = None

        # self.canvas.tag_lower(self.obj_ID2)
        # self.canvas.tag_lower(self.obj_ID1)

    def update(self, target_start=0, target_extent=0):
        # if pie already exists and it should be updated
        if target_extent and self.obj_ID1:
            F1 = self.stiffness * (target_start - self.start) - self.damping * self.v1
            F2 = self.stiffness * (target_extent - self.extent) - self.damping * self.v2

            self.a1 = F1 / self.mass
            self.a2 = F2 / self.mass

            self.v1 = self.v1 + self.a1
            self.v2 = self.v2 + self.a2

            self.start = self.start + self.v1
            self.extent = self.extent + self.v2

            if self.extent > 0.5:
                self.canvas.itemconfig(self.obj_ID1, start=self.start, extent=self.extent)
                self.canvas.itemconfig(self.obj_ID2, start=self.start, extent=self.extent)

                x_dir = math.sin((90 - (self.extent + 2 * self.start) / 2) / 360 * 2 * math.pi)
                y_dir = math.cos((90 - (self.extent + 2 * self.start) / 2) / 360 * 2 * math.pi)

                if self.display_label:
                    if self.extent > min_slice * 360:
                        self.canvas.coords(self.line, (self.x1 + self.x2) / 2 + (self.size/2 + self.size/120) * x_dir,
                                                            (self.y1 + self.y2) / 2 - (self.size/2 + self.size/120) * y_dir,
                                                            (self.x1 + self.x2) / 2 + (self.size/2 + self.size/30) * x_dir,
                                                            (self.y1 + self.y2) / 2 - (self.size/2 + self.size/30) * y_dir)

                        self.canvas.itemconfig(self.text, text=self.name)
                        if not self.extent > min_slice_percentage_display * 360 and self.scale_label:
                            self.font_temp = font.Font(family=text_font, size=int(
                                (12 + self.size / 150) / SCALEFACTOR * self.extent / ((0.5 * min_slice_percentage_display * 360 + 0.5 * self.extent))),
                                                       weight="bold")
                            self.canvas.itemconfig(self.text, font=self.font_temp)

                        self.canvas.coords(self.text, ((self.x1 + self.x2) / 2 + (self.size/2 + self.size/12 + len(self.name) * (15 + self.size/30) * self.size/7500 + (15 + self.size/50)) * x_dir,
                                                            (self.y1 + self.y2) / 2 - (self.size/2 + self.size/12) * y_dir))

                        if self.display_percentages:
                            if self.extent > min_slice_percentage_display * 360:
                                self.canvas.itemconfig(self.text2, text=format(self.extent/360*100, ",.{}f".format(decimal_places)) + "%")
                                self.canvas.coords(self.text2, ((self.x1 + self.x2) / 2 + (self.size / 2 + self.size / 12 + len(self.name) * (15 + self.size / 30) * self.size / 7500 + (15 + self.size / 50)) * x_dir,
                                                               int((self.y1 + self.y2) / 2 - (self.size / 2 + self.size / 12) * y_dir) + self.size/30 ))
                            else:
                                self.canvas.itemconfig(self.text2, text="")
                    else:
                        self.canvas.itemconfig(self.text, text="")
                        self.canvas.coords(self.line, 0, 0, 0, 0)

                        if self.display_percentages:
                            self.canvas.itemconfig(self.text2, text="")

                if self.imgs and self.extent > min_slice * 360:
                    percentage = self.extent / 360
                    if percentage >= min_slice_image:
                        self.image_file = self.imgs[int(self.size / 7.5)]
                    elif percentage < min_slice:
                        self.image_file = self.imgs[int(self.size / 7.5 / min_slice_image * (min_slice))]
                    else:
                        self.image_file = self.imgs[int(self.size / 7.5 / min_slice_image * (percentage))]
                    self.canvas.coords(self.img, (self.x1 + self.x2) / 2 + (self.size/2.5) * x_dir,
                                                        (self.y1 + self.y2) / 2 - (self.size/2.5) * y_dir)
                    self.canvas.itemconfig(self.img, image=self.image_file)

                elif self.imgs:
                    self.canvas.coords(self.img, -10000, -10000)

            else:
                self.canvas.itemconfig(self.obj_ID1, start=self.start, extent=0)
                self.canvas.itemconfig(self.obj_ID2, start=self.start, extent=0)

                if self.display_label:
                    self.canvas.itemconfig(self.text, text="")
                    self.canvas.coords(self.line, 0, 0, 0, 0)

                    if self.display_percentages:
                        self.canvas.itemconfig(self.text2, text="")

                if self.img:
                    self.canvas.coords(self.img, -10000, -10000)

        # delete pies when not needed anymore
        elif target_extent == 0 and self.obj_ID1:
            if self.obj_ID1:
                self.canvas.delete(self.obj_ID1)
                self.obj_ID1 = None
            if self.obj_ID2:
                self.canvas.delete(self.obj_ID2)
                self.obj_ID2 = None
            if self.img:
                self.canvas.delete(self.img)
                self.img = None
            if self.display_label and self.text:
                self.canvas.delete(self.text)
                self.text = None
            if self.display_percentages and self.text2:
                self.canvas.delete(self.text2)
                self.text2 = None
            if self.display_label and self.line:
                self.canvas.delete(self.line)
                self.line = None

        # redraw pies
        elif not target_extent == 0 and self.obj_ID1 == None:
            self.draw(target_start, target_extent)
