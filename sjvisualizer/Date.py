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
    9: "Sep",
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

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class date(cv.sub_plot):
    """
    Use this to add a timestamp to your visualization.

    :param canvas: tkinter canvas to draw the graph to
    :type canvas: tkinter.Canvas

    :param width: width of the timestamp in pixels (doesn't change the font size), default depends on screen resolution
    :type width: int

    :param height: height of the timestamp in pixels, this settings also changes the font size, default depends on screen resolution
    :type height: int

    :param x_pos: the x location of the top left pixel of the timestamp, default depends on screen resolution
    :type x_pos: int

    :param y_pos: the y location of the top left pixel of the timestamp, default depends on screen resolution
    :type y_pos: int

    :param prefix: text to prefix the timestamp, default is "
    :type prefix: str

    :param time_indicator: format of the timestamp, "day", "month", "year", default is "year"
    :type time_indicator: str

    :param font_color: font color, default is (0,0,0)
    :type font_color: tuple of length 3 with integers
    """
    def draw(self, time):

        if not hasattr(self, 'prefix'):
            self.prefix = ""

        if self.time_indicator == "year":
            text = str(time.year)
        elif self.time_indicator == "month":
            text = str(f"{time.year} {months[time.month]}")
        elif self.time_indicator == "day":
            if self.format == "USA":
                text = str(f"{months[time.month]} {time.day} {time.year}")
            else:
                text = str(f"{time.day} {months[time.month]} {time.year}")

        if self.anchor == "se":
            position = (self.x_pos - self.width/2, self.y_pos - self.height/2)
        else:
            position = (self.x_pos + self.width/2, self.y_pos + self.height/2)
        self.obj_id = self.canvas.create_text(*position, text=self.prefix + text, font=font.Font(family=text_font, size=int(self.height*0.65/ SCALEFACTOR), weight="bold"), fill=cv._from_rgb(self.font_color), anchor=self.anchor)

    def update(self, time):
        if self.time_indicator == "year":
            text = str(time.year)
        elif self.time_indicator == "month":
            text = str(f"{months[time.month]} {time.year}")
        elif self.time_indicator == "day":
            if self.format == "USA":
                text = str(f"{months[time.month]} {time.day} {time.year}")
            else:
                text = str(f"{time.day} {months[time.month]} {time.year}")

        self.canvas.itemconfig(self.obj_id, text=self.prefix + text)
        self.canvas.tag_raise(self.obj_id)