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
text_font = "Microsoft JhengHei UI Light"
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

class static_image(sub_plot):
    """
    Use this to add static images to your visualization.

    :param canvas: tkinter canvas to draw the graph to
    :type canvas: tkinter.Canvas

    :param width: width of the image in pixels
    :type width: int

    :param height: height of the image in pixels
    :type height: int

    :param x_pos: the x location of the top left pixel of this image
    :type x_pos: int

    :param y_pos: the y location of the top left pixel of this image
    :type y_pos: int

    :param file: file location of the image you want to add the canvas, only png files are support
    :type file: str

    :param on_top: set this to True to always draw this image on top
    :type on_top: boolean
    """

    def draw(self, *args, **kwargs):
        img = cv.load_image(self.file, self.width, self.height, self.root, self.file)
        self.img = self.canvas.create_image(self.width/2 + self.x_pos, self.height/2 + self.y_pos, image=img, anchor=self.anchor)

    def update(self, *args, **kwargs):
        if hasattr(self, "on_top"):
            if self.on_top:
                self.canvas.tag_raise(self.img)
            else:
                self.canvas.tag_lower(self.img)
        else:
            self.canvas.tag_lower(self.img)