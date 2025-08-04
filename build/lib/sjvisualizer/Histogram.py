from sjvisualizer import Canvas as cv
from sjvisualizer import Axis
from sjvisualizer.Canvas import *
from tkinter import *
from PIL import Image
import io
import datetime
import time
import math
from PIL import Image, ImageTk
import copy
import pandas as pd
from tkinter import font
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

format_str = '%d-%m-%Y'  # The format

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class histogram(cv.sub_plot):
    """Example class to create custom data animations this class is derived from the sub_plot class

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

            :param unit: unit of the values visualized, default is ""
            :type unit: str

            :param text_font: selected font, defaults to Microsoft JhengHei UI
            :type text_font: str
            """

    def draw(self, time):
        """This function gets executed only once at the start of the animation"""
        self.default_min_value = 0
        # get the data for the given time step
        data = self._get_data_for_frame(time)

        # create a dictionary to hold all graph_element objects
        self.graph_elements = {}

        # create axis
        self.axis = Axis.axis(canvas=self.canvas, n=self.y_ticks, orientation="vertical", x=self.x_pos,
                               y=self.y_pos + self.height*0.85, length=self.height*0.85, width=self.width, allow_decrease=False,
                               is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=False,
                               unit=self.unit)
        self.axis.draw(min=min(data), max=max(data))

        # loop over all values in the row
        spacing = self.width / (len(data))
        bar_width = spacing * 0.75
        x_pos = self.x_pos + spacing / 2
        for i, (name, d) in enumerate(data.items()):
            self.graph_elements[name] = graph_element(name=name, pos=x_pos, canvas=self.canvas, value=d, unit=self.unit, font_color=self.font_color, colors=self.colors, chart=self, text_font=self.text_font, font_size=self.font_size, bar_width=bar_width)
            x_pos = x_pos + spacing
    def update(self, time):
        """This function gets executed every frame"""
        # get the data for the given time step
        data = self._get_data_for_frame(time)

        if min(data) > self.default_min_value:
            self.axis.update(min=0, max=max(data))
        else:
            self.axis.update(min=min(data), max=max(data))
        # loop over all values in the row
        for i, (name, d) in enumerate(data.items()):
            self.graph_elements[name].update(d)


class graph_element():

    def __init__(self, name=None, pos=0, canvas=None, value=0, unit=None, font_color=(0,0,0), colors={}, font_size=12, chart=None, text_font="Microsoft JhengHei UI", bar_width=10):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart
        self.colors = colors
        self.text_font = text_font
        self.pos = pos
        self.bar_width = bar_width

        if isinstance(colors, dict):
            if name in colors:
                self.color = cv._from_rgb(colors[name])
            else:
                self._set_color()
        else:
            self._set_color()

        self.draw(value)

    def _set_color(self):
        if self.chart.sjcanvas and self.chart.sjcanvas.color_palette:
            color = self.chart.sjcanvas.color_palette[0]
            self.chart.sjcanvas.color_palette.pop(0)
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                           random.randint(min_color + 30, max_color)))

        self.color = cv._from_rgb(color)
        self.colors[self.name] = color

    def draw(self, value):
        # here we can add the options to draw objects to the screen using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        font_obj = font.Font(family=self.text_font, size=int(self.font_size))
        self.rect = self.canvas.create_rectangle(50, 50, 500, 500, fill=self.color, outline="")
        self.label = self.canvas.create_text(self.pos, self.chart.y_pos + 0.85*self.chart.height, text=self.name, anchor="nw", font=font_obj, fill=cv._from_rgb(self.font_color), angle=-35)
        # self.value = self.canvas.create_text(0, 0, text=cv.format_value(value), anchor="w", font=font_obj, fill=cv._from_rgb(self.font_color))

    def update(self, value):
        # here we can update the size and location of the elements on the screen by using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        # self.canvas.coords(self.label, 10, 10)

        # we can also update the value
        # self.canvas.itemconfig(self.value, text=cv.format_value(value))
        y1 = self.chart.axis.calc_positions(0)
        y2 = self.chart.axis.calc_positions(value)
        self.canvas.coords(self.rect, self.pos - self.bar_width/2, self.chart.y_pos+0.85*self.chart.height-y1, self.pos + self.bar_width/2, self.chart.y_pos+0.85*self.chart.height-y2)

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df = DataHandler.DataHandler(excel_file="data/Area Dev.xlsx", number_of_frames=60*30).df

    canvas = Canvas.canvas()

    eq = histogram(canvas=canvas, df=df, font_size=25, font_color=(0, 0, 0))
    canvas.add_sub_plot(eq)

    canvas.play(fps=60)