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

class static_text(cv.sub_plot):
    """
        Class to add a static text to the visualization

        :param text: text to be displayed, for example a title
        :type text: str

        :param anchor: Anchors are used to define where text is positioned relative to a reference point. Possible values correspond wind directions:
            NW
            N
            NE
            W
            CENTER
            E
            SW
            S
            SE
        :type anchor: str

        :param canvas: tkinter canvas to draw the graph to
        :type canvas: tkinter.Canvas

        :param width: width of the plot in pixels, default depends on screen resolution
        :type width: int

        :param height: height of the text, closely resembles font size
        :type height: int

        :param x_pos: the x location of the top left pixel in this plot, default depends on screen resolution
        :type x_pos: int

        :param y_pos: the y location of the top left pixel in this plot, default depends on screen resolution
        :type y_pos: int

        :param font_color: font color, default is (0,0,0)
        :type font_color: tuple of length 3 with integers


        """

    def draw(self, *args, **kwargs):
        if hasattr(self, "align"):
            if self.align == "left":
                self.font = font.Font(family=text_font, size=int(0.65 * self.height / SCALEFACTOR), underline=UNDERLINE,
                                      weight="bold")
                self.text = self.canvas.create_text(self.x_pos, self.height / 2 + self.y_pos,
                                                    text=self.text, font=self.font, fill=cv._from_rgb(self.font_color),
                                                    anchor=self.anchor)
            else:
                self.font = font.Font(family=text_font, size=int(0.65 * self.height / SCALEFACTOR), underline=UNDERLINE,
                                      weight="bold")
                self.text = self.canvas.create_text(self.width / 2 + self.x_pos, self.height / 2 + self.y_pos,
                                                    text=self.text, font=self.font, fill=cv._from_rgb(self.font_color),
                                                    anchor=self.anchor)


        else:
            self.font = font.Font(family=text_font, size=int(0.65*self.height/ SCALEFACTOR), underline=UNDERLINE, weight="bold")
            self.text = self.canvas.create_text(self.width/2 + self.x_pos, self.height/2 + self.y_pos, text=self.text, font=self.font, fill=cv._from_rgb(self.font_color), anchor=self.anchor)

    def update(self, *args, **kwargs):
        self.canvas.tag_raise(self.text)