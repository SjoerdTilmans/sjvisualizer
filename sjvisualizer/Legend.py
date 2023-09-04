from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
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

min_slice = 0.03
min_slice_image = 0.055
min_slice_percentage_display = 0.055
decimal_places = 2
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
text_font = "Microsoft JhengHei UI"

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class legend(cv.sub_plot):
    """Class to construct an animated area graph

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

        :param font_color: font color, default is (0,0,0)
        :type font_color: tuple of length 3 with integers

        :param font_size: font size, in pixels
        :type font_size: int

        :param sort: should the elements of this graph be sorted based on the value? default is True
        :type sort: boolean
        """

    def draw(self, time):
        if hasattr(self, "font_size"):
            self.font_size = self.font_size
        else:
            self.font_size = self.height / 33 / SCALEFACTOR

        if not hasattr(self, "n"):
            if len(self.df.columns) > 10:
                n = 10
            else:
                n = len(self.df.columns)

        if not hasattr(self, "orientation"):
            self.orientation = "vertical"

        self.font = font.Font(family=text_font, size=int(self.font_size))

        if self.sort:
            data = self._get_data_for_frame(time).sort_values(ascending=False)
        else:
            data = self._get_data_for_frame(time)

        self.elems = {}

        self._get_positions()

        for i, (name, d) in enumerate(data.items()):
            if i < self.n:
                self.elems[name] = elem(name=name, canvas=self.canvas, font_color=self.font_color, font=self.font, parent=self, colors=self.colors, y=self.positions[i])
            else:
                self.elems[name] = elem(name=name, canvas=self.canvas, font_color=self.font_color, font=self.font,
                                        parent=self, colors=self.colors)

    def update(self, time):
        if self.sort:
            data = self._get_data_for_frame(time).sort_values(ascending=False)
        else:
            data = self._get_data_for_frame(time)

        for i, (name, d) in enumerate(data.items()):
            if i < self.n:
                self.elems[name].update(self.x_pos, self.positions[i], True)
            else:
                self.elems[name].update(0, 0, False)

    def _get_positions(self):
        if self.orientation == "vertical":
            self.positions = [self.y_pos + (i + 0.5) * self.height / (self.n) for i in range(self.n)]
        else:
            raise f"{self.orientation} orientation is not supported"

class elem():

    def __init__(self, name=None, canvas=None, y=0, unit=None, font_color=(0,0,0), colors=None, font=None, parent=None):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.font = font
        self.parent = parent

        # dynamic constants
        self.m = 2
        self.k = 40 / (self.parent.height)
        self.d = 0.3

        self.y = y
        self.v_y = 0
        self.a_y = 0

        # load image
        try:
            self.img = cv.load_image(os.path.join("assets", self.name.replace("*", "") + ".png"), 4*int(self.parent.font_size), 4*int(self.parent.font_size), self.parent.root, name)
        except:
            print(f"No image for {self.name}")
            self.img = None

        if isinstance(colors, dict):
            if name in colors:
                self.color = cv._from_rgb(colors[name])
            else:
                color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                               random.randint(min_color + 30, max_color)))
                self.color = cv._from_rgb(color)
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                           random.randint(min_color + 30, max_color)))
            self.color = cv._from_rgb(color)

        self.draw()

    def draw(self):
        self.label = self.canvas.create_text(500, 500, text=self.name, font=self.font, fill=cv._from_rgb(self.font_color), anchor="w")
        self.shape = self.canvas.create_rectangle(400 - self.parent.font_size, 400 - self.parent.font_size, 400 + self.parent.font_size, 400 + self.parent.font_size, fill=self.color)
        if self.img:
            self.image_on_canvas = self.canvas.create_image(400, 400, image=self.img, anchor="w")

    def update(self, x, y, draw):
        if draw and self.shape:
            self.calc_position(y)
            self.canvas.coords(self.label, x, self.y)
            if self.img:
                text_box = self.canvas.bbox(self.label)
                self.canvas.coords(self.image_on_canvas, text_box[2] + self.parent.font_size, self.y)
            self.canvas.coords(self.shape, x - 3 * self.parent.font_size, self.y - self.parent.font_size, x - self.parent.font_size, self.y + self.parent.font_size)
        elif draw and not self.shape:
            self.y = y
            self.v_y = 0
            self.a_y = 0
            self.draw()
            self.update(x, y, draw)
        else:
            self.canvas.delete(self.label)
            self.canvas.delete(self.shape)
            if self.img:
                self.canvas.delete(self.image_on_canvas)
            self.shape = None
            self.label = None
            self.image_on_canvas = None

    def calc_position(self, target_y):
        F = self.k * (target_y - self.y) - self.d * self.v_y
        self.a_y = F / self.m
        self.v_y = self.v_y + self.a_y
        self.y = self.y + self.v_y