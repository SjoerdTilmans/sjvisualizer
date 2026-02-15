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

class bubble_chart(cv.sub_plot):
    """Class to create bubble animations this class is derived from the sub_plot class

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

            :param df_x: pandas dataframe that holds the data for x-axis
            :type df_x: pandas.DataFrame

            :param df_y: pandas dataframe that holds the data for y-axis
            :type df_y: pandas.DataFrame

            :param df_size: pandas dataframe that holds data for the size of the bubbles (optional)
            :type df_size: pandas.DataFrame

            :param color: list or tuple holding rgb color value for the line, default is (31, 119, 180)
            :type colors: list

            :param font_color: font color, default is (0,0,0)
            :type font_color: tuple of length 3 with integers

            :param font_size: font size, in pixels
            :type font_size: int

            :param unit: unit of the values visualized, default is ""
            :type unit: str

            :param text_font: selected font, defaults to Microsoft JhengHei UI
            :type text_font: str

            :param marker_size: size of the markers
            :type marker_size: int

            :param x_log: plot x values on log scale?
            :type x_log: bool

            :param y_log: plot y values on log scale?
            :type y_log: bool

            :param decimal_places: number of decimal places to be displayed on the y-axis
            :type decimal_places: int
            """

    def draw(self, time):
        """This function gets executed only once at the start of the animation"""
        self.default_min_value = 0

        if not hasattr(self, "marker_size"):
            self.marker_size = 15

        if not hasattr(self, "color"):
            self.color = (31, 119, 180)

        if not hasattr(self, "label"):
            self.label = ""

        if not hasattr(self, "display_label"):
            self.display_label = True

        if not hasattr(self, "df_size"):
            self.df_size = None

        if not hasattr(self, "x_log"):
            self.x_log = False

        if not hasattr(self, "y_log"):
            self.y_log = False

        # get the data for the given time step
        y_data = self._get_data_for_frame_y(time)
        x_data = self._get_data_for_frame_x(time)

        # create y-axis
        if self.x_log:
            ticks_only = False
        else:
            ticks_only = True
        self.y_axis = Axis.axis(canvas=self.canvas, n=self.y_ticks, orientation="vertical", x=self.x_pos,
                               y=self.y_pos + self.height*0.85, length=self.height*0.85, width=self.width, allow_decrease=False,
                               is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=ticks_only,
                               unit=self.unit, is_log_scale=self.y_log, decimal_places=self.decimal_places)
        self.y_axis.draw(min=min(y_data), max=max(y_data))

        # create x-axis
        if self.x_log:
            ticks_only = False
        else:
            ticks_only = True
        self.x_axis = Axis.axis(canvas=self.canvas, n=self.x_ticks, orientation="horizontal", x=self.x_pos, y=self.y_pos + self.height*0.85, length=self.width, width=0.85*self.height,
                                allow_decrease=False, is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=ticks_only, is_log_scale=self.x_log, decimal_places=self.decimal_places)
        self.x_axis.draw(min=min(x_data), max=max(x_data))

        # create (hidden) axis for bubble size
        if isinstance(self.df_size, pd.DataFrame):
            size_data = self._get_data_for_frame_size(time)
            self.size_axis = Axis.axis(canvas=self.canvas, n=self.x_ticks, orientation="horizontal", x=-100, y=-100, length=0.15 * self.height, width=0.85*self.height,
                                    allow_decrease=False, is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=True)
            self.size_axis.draw(min=min(size_data), max=max(size_data))

        # create list to hold series data
        self.bubbles = []
        for i, (name, d) in enumerate(y_data.items()):
            self.bubbles.append(bubble(name=name, canvas=self.canvas, colors=self.colors, value=0, unit="", font_color=self.font_color, font_size=self.font_size, chart=self, text_font=self.text_font))

    def _get_data_for_frame_x(self, time, df_x=None):
        if not isinstance(df_x, pd.DataFrame):
            df_x = self.df_x
        return df_x.loc[time]

    def _get_data_for_frame_y(self, time, df_y=None):
        if not isinstance(df_y, pd.DataFrame):
            df_y = self.df_y
        return df_y.loc[time]

    def _get_data_for_frame_size(self, time, df_size=None):
        if not isinstance(df_size, pd.DataFrame):
            df_size = self.df_size
        return df_size.loc[time]

    def update(self, time):
        """This function gets executed every frame"""
        x_values = self._get_data_for_frame_x(time)
        y_values = self._get_data_for_frame_y(time)

        # get the data for the given time step
        y_max = max(y_values)
        x_max = max(x_values)

        y_min = min(y_values)
        x_min = min(x_values)

        if not self.y_log and y_min > self.default_min_value:
            self.y_axis.update(min=0, max=y_max)
        else:
            y_min = self._closest_lower_decade(y_min)
            self.y_axis.update(min=y_min, max=y_max)

        if not self.x_log and x_min > self.default_min_value:
            self.x_axis.update(min=0, max=x_max)
        else:
            x_min = self._closest_lower_decade(x_min)
            self.x_axis.update(min=x_min, max=x_max)

        # create (hidden) axis for bubble size
        if isinstance(self.df_size, pd.DataFrame):
            size_values = self._get_data_for_frame_size(time)
            self.size_axis.update(min=0, max=abs(max(size_values)))

        for b in self.bubbles:
            if isinstance(self.df_size, pd.DataFrame):
                b.update(x_value=x_values[b.name], y_value=y_values[b.name], size_value=size_values[b.name])
            else:
                b.update(x_value=x_values[b.name], y_value=y_values[b.name])

    def _closest_lower_decade(self, x):
        if x <= 0:
            raise ValueError("Input must be a positive number.")
        return 10 ** math.floor(math.log10(x))

class bubble():

    def __init__(self, name=None, canvas=None, value=0, unit=None, colors={}, font_color=(0,0,0), font_size=12, chart=None, text_font="Microsoft JhengHei UI"):
        self.name = name
        self.canvas = canvas
        self.unit = unit
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart
        self.text_font = text_font
        self.colors = colors

        self._set_color()

        self.draw(value)

    def _set_color(self):
        if not self.name in self.colors:
            if self.chart.sjcanvas and self.chart.sjcanvas.color_palette:
                color = self.chart.sjcanvas.color_palette[0]
                self.chart.sjcanvas.color_palette.pop(0)
            else:
                color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                               random.randint(min_color + 30, max_color)))

            self.color = cv._from_rgb(color)
            self.colors[self.name] = color
        else:
            self.color = cv._from_rgb(self.colors[self.name])

    def draw(self, value):
        # here we can add the options to draw objects to the screen using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        font_obj = font.Font(family=self.text_font, size=int(self.font_size/3*2))
        self.marker = self.canvas.create_oval(50, 50, 500, 500, fill=self.color, outline=self.color, width=3)

        if self.chart.display_label:
            self.label = self.canvas.create_text(0, 0, text=self.name, anchor="n", font=font_obj, fill=cv._from_rgb(self.font_color))
        # self.value = self.canvas.create_text(0, 0, text=cv.format_value(value), anchor="w", font=font_obj, fill=cv._from_rgb(self.font_color))

    def update(self, x_value, y_value, size_value=None):
        y = self.chart.y_pos+0.85*self.chart.height-self.chart.y_axis.calc_positions(y_value)
        x = self.chart.x_axis.calc_positions(x_value) + self.chart.x_pos
        if size_value:
            size = self.chart.size_axis.calc_positions(size_value)
            self.canvas.coords(self.marker, x - size / 2, y - size / 2,
                               x + size / 2, y + size / 2)
            if self.chart.display_label:
                self.canvas.coords(self.label, x, y + size / 2 + 5)
        else:
            self.canvas.coords(self.marker, x - self.chart.marker_size/2, y - self.chart.marker_size/2, x + self.chart.marker_size/2, y + self.chart.marker_size/2)
            if self.chart.display_label:
                self.canvas.coords(self.label, x, y + self.chart.marker_size/2 + 5)
        self.coords = (x,y)
        self.canvas.tag_raise(self.label)

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df_y = DataHandler.DataHandler(excel_file="data/Y_log.xlsx", number_of_frames=60*15).df
    df_x = DataHandler.DataHandler(excel_file="data/X_log.xlsx", number_of_frames=60*15).df
    df_size = DataHandler.DataHandler(excel_file="data/X2 - Copy.xlsx", number_of_frames=60*15).df

    canvas = Canvas.canvas()

    colors = {
        "Neg column": (255, 0, 0)
    }

    dc = bubble_chart(canvas=canvas, colors=colors, y_log=True, x_log=True, df_x=df_x, df_y=df_y, df_size=df_size, font_size=25, font_color=(0, 0, 0))
    canvas.add_sub_plot(dc)

    canvas.play(fps=60, record=False)