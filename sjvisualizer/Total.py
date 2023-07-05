from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
from sjvisualizer import Axis
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

class total(sub_plot):

    def draw(self, time):
        if not hasattr(self, "prefix"):
            self.prefix = ""

        if hasattr(self, "font_size"):
            self.font_size = self.font_size / SCALEFACTOR
        else:
            self.font_size = self.height / 33 / SCALEFACTOR

        if not hasattr(self, "text_font"):
            self.text_font = text_font

        if not hasattr(self, "decimal_places"):
            self.decimal_places = decimal_places

        total = self._get_data_for_frame(time).sum()
        self.font = font.Font(family=self.text_font, size=int(self.font_size))
        self.text = self.canvas.create_text(self.x_pos, self.y_pos, text=self.prefix + format(total, ",.{}f".format(self.decimal_places)), font=self.font, fill=cv._from_rgb(self.font_color))
        if "$" in self.unit:
            self.unit = self.unit.replace("$", "")
            self.money = "$"
        else:
            self.unit = self.unit
            self.money = ""

    def update(self, time):
        total = self._get_data_for_frame(time).sum()
        self.canvas.itemconfig(self.text, text=self.prefix + self.money + format(total, ",.{}f".format(self.decimal_places)) + self.unit)
