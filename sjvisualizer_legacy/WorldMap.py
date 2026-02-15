import sjvisualizer
from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
from tkinter import *
import io
from tkinter import font
import datetime
import time
import math
from PIL import Image, ImageTk, ImageDraw
import copy
import pandas as pd
import random
import operator
import os
import ctypes
import json

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
decimal_places = 0
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
UPDATE_INTERVAL = 1 #after how many frames a country gets updated

with open(os.path.join(os.path.dirname(sjvisualizer.__file__), "world.json")) as f:
    WORLD_COORDS = json.load(f)
MAP_SIZE = (2000, 1142.5758125835168)

class world_map(cv.sub_plot):
    """:param canvas: tkinter canvas to draw the graph to
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

            :param font_color: font color, default is (0,0,0)
            :type font_color: tuple of length 3 with integers

            :param font_size: font size, in pixels
            :type font_size: int

            :param min_value: minimum value to appear on color bar, defaults to 0
            :type min_value: float

            :param color_bar_color: list that holds start and end color of color bar in RGB values, example: color_bar_color=[[210,210,210], [100,40,10]]
            :type color_bar_color: list[lists]

            :param unit: unit of the values visualized, default is ""
            :type unit: str"""
    def draw(self, time):
        if not hasattr(self, "min_value"):
            self.min_value = 0

        if hasattr(self, "font_size"):
            self.font_size = self.font_size / SCALEFACTOR
        else:
            self.font_size = self.height / 20 / SCALEFACTOR

        self.i = 0
        self.current_max_value = 0

        row = self._get_data_for_frame(time)
        self.countries = []
        # self.canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height)
        self._map_coords()
        for name, data in WORLD_COORDS.items():
            coords = data["Polygons"]
            self.countries.append(country(name=name, canvas=self.canvas, coords=coords, colors=self.color_bar_color, min_value=self.min_value))

        self._create_color_bar(row)

    def update(self, time):
        row = self._get_data_for_frame(time)
        self.color_bar.update(row)

        self._calc_max_value(row)

        for country in self.countries[int(self.i*len(self.countries)/UPDATE_INTERVAL):int((self.i+1)*len(self.countries)/UPDATE_INTERVAL)]:
            country.update(row, self.current_max_value)

        if self.i >= UPDATE_INTERVAL - 1:
            self.i = 0
        else:
            self.i = self.i + 1

    def _calc_max_value(self, data):
        if data.max() > self.current_max_value:
            self.current_max_value = data.max()
        elif self.allow_decrease:
            self.current_max_value = data.max()

    def _create_color_bar(self, data):
        self.color_bar = color_bar(self.canvas, self.color_bar_color, self.map_width / 4 + self.x_shift, self.y_pos + self.height + self.height / 20, self.map_width / 4 * 3 + self.x_shift, self.y_pos + self.height + self.height / 8, data=data, unit=self.unit, min_value=self.min_value, font_color=self.font_color, allow_decrease=self.allow_decrease, parent=self)

    def _map_coords(self):
        self.ratio = self.height / MAP_SIZE[1]
        self.map_width = MAP_SIZE[0] * self.ratio

        self.x_shift = self.x_pos + self.width / 2 - self.map_width / 2
        self.y_shift = self.y_pos

        for name, data in WORLD_COORDS.items():
            self._calc_new_coords(data["Polygons"])

    def _calc_new_coords(self, coords):
        if isinstance(coords[0], list):
            for c in coords:
                self._calc_new_coords(c)
        else:
            coords[0] = coords[0] * self.ratio + self.x_shift
            coords[1] = coords[1] * self.ratio + self.y_shift

class country():

    def __init__(self, name=None, canvas=None, coords=[], value=0, unit=None, font_color=(0,0,0), colors=None, min_value=0):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.coords = coords
        # self.begin_color = (125, 100, 125) # dark
        self.begin_color = (255, 255, 255) # light
        self.current_color = self.begin_color
        self.colors = colors
        self.min_value = min_value

        self.polygons = []

        self.draw()

    def draw(self):
        for c in self.coords:
            self.polygons.append(self.canvas.create_polygon(c, fill=cv._from_rgb(self.current_color), outline=cv._from_rgb((200, 200, 200))))

    def update(self, data, current_max):
        if self.name in data:
            self._calc_color(data[self.name], current_max)
            for poly in self.polygons:
                self.canvas.itemconfig(poly, fill=cv._from_rgb(self.current_color))

                if self.name == "Russia":
                    if "USSR" in data:
                        if data["USSR"] > data[self.name]:
                            self._calc_color(data["USSR"], current_max)
                            self.canvas.itemconfig(poly, fill=cv._from_rgb(self.current_color))

                    elif "USSR/Russia" in data:
                        if data["USSR/Russia"] > data[self.name]:
                            self._calc_color(data["USSR/Russia"], current_max)
                            self.canvas.itemconfig(poly, fill=cv._from_rgb(self.current_color))


    def _calc_color(self, value, current_max):
        if value >= self.min_value:
            fraction = value / current_max
            min_color = self.colors[0]
            max_color = self.colors[1]
            self.current_color = (int((1 - fraction) * min_color[0] + fraction * max_color[0]), int((1 - fraction) * min_color[1] + fraction * max_color[1]), int((1 - fraction) * min_color[2] + fraction * max_color[2]))
        else:
            self.current_color = self.begin_color

        # if value > current_max:
        #     self.current_color = self.colors[1]
        # else:
        #     fraction = value / current_max
        #     min_color = self.colors[0]
        #     max_color = self.colors[1]
        #     self.current_color = (int((1 - fraction) * min_color[0] + fraction * max_color[0]), int((1 - fraction) * min_color[1] + fraction * max_color[1]), int((1 - fraction) * min_color[2] + fraction * max_color[2]))


class color_bar():

    def __init__(self, canvas, colors, x1, y1, x2, y2, data, unit="", min_value=0, font_color= (0, 0, 0), allow_decrease=False, parent=None):
        self.canvas = canvas
        self.colors = colors
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.unit = unit
        self.font_color = font_color

        self.allow_decrease = allow_decrease

        self.min_value = min_value

        self.parent = parent

        self.current_max_value = 0

        self.m = Image.new("RGB", (int(x2 - x1), int(y2 - y1)), (255, 255, 255, 0))
        self.d = ImageDraw.Draw(self.m)
        self.d.rectangle((int(0), int(0), int(x2-x1) - 1, int(y2-y1) - 1), outline=(0, 0, 0))
        # self.canvas.create_rectangle(x1, y1, x2, y2)
        self._calc_max_value(data)

        if self.parent:
            self.font = font.Font(family=text_font, size=int(self.parent.font_size))
        else:
            self.font = font.Font(family=text_font, size=int((y2 - y1) / 2 - 1))

        self.draw(data)

    def draw(self, data):
        for i in range(0, int(self.x2 - self.x1)):
            percentage = i / int(self.x2 - self.x1 + 1)
            min_color = self.colors[0]
            max_color = self.colors[1]

            current_color = (int((1 - percentage) * min_color[0] + percentage * max_color[0]), int((1 - percentage) * min_color[1] + percentage * max_color[1]), int((1 - percentage) * min_color[2] + percentage * max_color[2]))
            self.d.line((i + 1, 1, i + 1, int(self.y2 - self.y1) - 2), fill=current_color)
            # self.canvas.create_line(i, self.y1 + 1, i, self.y2, fill=cv._from_rgb(current_color))

        self.m = ImageTk.PhotoImage(self.m)
        self.canvas.create_image(self.x1, self.y1, image=self.m, anchor="nw")

        self.min = self.canvas.create_text(self.x1 - 5, (self.y1 + self.y2)/2, text=format(self.min_value, ",.{}f".format(decimal_places)), anchor="e", font=self.font, fill=cv._from_rgb(self.font_color))
        self.max = self.canvas.create_text(self.x2 + 5, (self.y1 + self.y2)/2, text=format(self.current_max_value, ",.{}f".format(decimal_places)) + str(self.unit), anchor="w", font=self.font, fill=cv._from_rgb(self.font_color))

    def update(self, data):
        self._calc_max_value(data)
        self.canvas.itemconfig(self.max, text=format(self.current_max_value, ",.{}f".format(decimal_places)) + str(self.unit))

    def _calc_max_value(self, data):
        if data.max() > self.current_max_value:
            self.current_max_value = data.max()
        elif self.allow_decrease:
            self.current_max_value = data.max()