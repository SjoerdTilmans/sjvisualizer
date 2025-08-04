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

class area_plot(cv.sub_plot):

    def draw(self, time):
        # self.canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height)
        self.time = self.canvas.create_text(self.x_pos, self.y_pos, text=str(time))

        data = self._get_data_for_frame(time)

        self.current_max = data.sum()

        self.max_value_obj = self.canvas.create_text(self.x_pos + self.width, self.y_pos, text=str(data.sum()))

        # create y_ticks
        self.y_ticks_objs = []
        # -600 because additional rows are added to the data
        dt = (self.df.index[-600] - time) / (self.y_ticks - 1)
        for i in range(0, self.y_ticks):
            self.y_ticks_objs.append(y_ticks(self.canvas, time, time + i*dt, self.x_pos, self.y_pos, self.width, self.height, self.unit, self.time_indicator))

        # draw area plot
        self.areas = []
        self.areas.append(area(name="Other", canvas=self.canvas, value=data.sum(), time=time, unit=self.unit, font_color=self.font_color, colors=self.colors, current_max=self.current_max, x_pos=self.x_pos, y_pos=self.y_pos, width=self.width, height=self.height))

    def update(self, time):

        data = self._get_data_for_frame(time)
        if data.sum() > self.current_max:
            self.current_max = data.sum()

        self.canvas.itemconfig(self.time, text=str(time))

        data = self._get_data_for_frame(time).sort_values(ascending=False)
        self.canvas.itemconfig(self.max_value_obj, text=str(data.sum()))

        for y_tick in self.y_ticks_objs:
            y_tick.update(time, data)

        for area in self.areas:
            if area.name == "Other":
                area.update(time, data.sum())

class area():

    def __init__(self, name=None, canvas=None, value=0, time=None, unit=None, font_color=(0,0,0), colors=None, current_max=0, x_pos=0, y_pos=0, width=0, height=0, previous_y=0):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.current_max = current_max

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height

        self.begin_time = time

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

        self.points = []
        self.times = []
        self.values = []

        self.draw(value, previous_y=previous_y)

    def draw(self, value, previous_y=0):
        if value:
            x = self.x_pos + self.width
            self.times.append(self.begin_time)
            self.values.append(value)
            self.points = self.points + [x, previous_y + self.y_pos, x, previous_y + self.y_pos + int(self._calc_height(value, self.current_max))]
            self.shape = self.canvas.create_polygon(self.points, outline="black")

    def update(self, time, value, previous_y=0):

        if value > self.current_max:
            self.current_max = value

        # update existing points
        self.points = []
        if self.values:
            for v, t in zip(self.values, self.times):
                try:
                    x = self.x_pos + (self.begin_time - t) / (time - t) * self.width
                except ZeroDivisionError:
                    x = self.x_pos
                self.points = self.points + [x, previous_y, x, previous_y + self._calc_height(value, self.current_max)]

    def _calc_height(self, value, current_max):
        return value / current_max * self.height

class y_ticks():

    def __init__(self, canvas, t0, begin_time, x_pos, y_pos, width, height, unit, time_indicator="year"):
        self.begin_time = begin_time
        self.t0 = t0
        self.canvas = canvas
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.unit = unit
        self.time_indicator = time_indicator

        self.font_size = int(self.height / 40)

        self.font = font.Font(family=text_font, size=self.font_size, weight="bold")

        self.draw()

    def draw(self):
        self.line = self.canvas.create_line(-1, -1, -1, -1, fill=cv._from_rgb((150,150,150)), width=2)
        self.drawn = False

        self.date = self.canvas.create_text(-1, -1, text="", anchor="e", font=self.font, fill=cv._from_rgb((150, 150, 150)))
        self.total = self.canvas.create_text(-1, -1, text="", anchor="e", font=self.font, fill=cv._from_rgb((150, 150, 150)))

    def update(self, time, data):
        if time > self.begin_time and self.drawn == False:
            fraction = (self.begin_time - self.t0) / (time - self.t0)
            x = self.x_pos + fraction * self.width
            self.canvas.coords(self.line, x, self.y_pos - 0.1 * self.height, x, self.y_pos + 1.1 * self.height)

            self.canvas.itemconfig(self.date, text=cv.format_date(time, self.time_indicator))
            self.canvas.itemconfig(self.total, text=format(data.sum(), ",.{}f".format(decimal_places)) + str(self.unit))

            self.canvas.coords(self.total, x - 2, self.y_pos - 0.05 * self.height)
            self.canvas.coords(self.date, x - 2, self.y_pos + 1.05 * self.height)

            self.drawn = True
        elif self.drawn:
            fraction = (self.begin_time - self.t0) / (time - self.t0)
            x = self.x_pos + fraction * self.width
            self.canvas.coords(self.line, x, self.y_pos - 0.1 * self.height, x, self.y_pos + 1.1 * self.height)

            self.canvas.coords(self.total, x - 2, self.y_pos - 0.05 * self.height)
            self.canvas.coords(self.date, x - 2, self.y_pos + 1.05 * self.height)