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

class xy(cv.sub_plot):
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

            :param df_x: pandas dataframe that holds the data for x-axis
            :type df_x: pandas.DataFrame

            :param df_y: pandas dataframe that holds the data for y-axis
            :type df_y: pandas.DataFrame

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

        # get the data for the given time step
        y_data = self._get_data_for_frame_y(time)
        x_data = self._get_data_for_frame_x(time)

        # create y-axis
        self.y_axis = Axis.axis(canvas=self.canvas, n=self.y_ticks, orientation="vertical", x=self.x_pos,
                               y=self.y_pos + self.height*0.85, length=self.height*0.85, width=self.width, allow_decrease=False,
                               is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=True,
                               unit=self.unit)
        self.y_axis.draw(min=min(y_data), max=max(y_data))

        # create x-axis
        self.x_axis = Axis.axis(canvas=self.canvas, n=self.x_ticks, orientation="horizontal", x=self.x_pos, y=self.y_pos + self.height*0.85, length=self.width, width=0.85*self.height,
                                allow_decrease=False, is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=True)
        self.x_axis.draw(min=min(x_data), max=max(x_data))

        # create list to hold series data
        self.series_objs = []
        self.add_series(self.df_x, self.df_y, self.label)

    def _get_data_for_frame_x(self, time, df_x=None):
        if not isinstance(df_x, pd.DataFrame):
            df_x = self.df_x
        return df_x.loc[time]

    def _get_data_for_frame_y(self, time, df_y=None):
        if not isinstance(df_y, pd.DataFrame):
            df_y = self.df_y
        return df_y.loc[time]

    def update(self, time):
        """This function gets executed every frame"""
        # get the data for the given time step
        y_max = max([max(y._get_data_for_frame_y(time)) for y in self.series_objs])
        x_max = max([max(y._get_data_for_frame_x(time)) for y in self.series_objs])

        y_min = min([min(y._get_data_for_frame_y(time)) for y in self.series_objs])
        x_min = min([min(y._get_data_for_frame_x(time)) for y in self.series_objs])

        if y_min > self.default_min_value:
            self.y_axis.update(min=0, max=y_max)
        else:
            self.y_axis.update(min=y_min, max=y_max)

        if x_min > self.default_min_value:
            self.x_axis.update(min=0, max=x_max)
        else:
            self.x_axis.update(min=x_min, max=x_max)

        for series_obj in self.series_objs:
            series_obj.update(time)

    def add_series(self, df_x, df_y, label=""):
        self.series_objs.append(series(df_x, df_y, self, label))

class series():

    def __init__(self, df_x, df_y, chart, label = ""):
        self.df_x = df_x
        self.df_y = df_y
        self.chart = chart
        self.label = label
        if isinstance(self.chart.colors, dict):
            if label in self.chart.colors:
                self.color = cv._from_rgb(colors[label])
            else:
                self._set_color()
        else:
            self._set_color()
        self.graph_elements = {}
        self.draw(self.chart.start_time)

    def draw(self, time):
        y_data = self._get_data_for_frame_y(time)
        x_data = self._get_data_for_frame_x(time)
        # create line object
        self.line = self.chart.canvas.create_line(0, 0, 0, 0, fill=self.color, width=int(self.chart.marker_size / 3))
        # loop over all values in the row
        for i, (name, d) in enumerate(y_data.items()):
            self.graph_elements[name] = graph_element(name=name, canvas=self.chart.canvas, value=d, unit=self.chart.unit,
                                                      color=self.color, chart=self.chart,
                                                      text_font=self.chart.text_font, font_size=self.chart.font_size)

        # create label
        font_obj = font.Font(family=self.chart.text_font, size=int(self.chart.font_size))
        self.label_obj = self.chart.canvas.create_text(0, 0, text=self.label, anchor="w", font=font_obj,
                                                 fill=self.color)

    def update(self, time):
        y_data = self._get_data_for_frame_y(time)
        x_data = self._get_data_for_frame_x(time)
        # loop over all values in the row
        for i, (name, d) in enumerate(y_data.items()):
            y_value = d
            x_value = x_data[name]
            self.graph_elements[name].update(x_value=x_value, y_value=y_value)

        self.update_line()
        self.update_label()

    def update_line(self):
        coords = [coord for obj in self.graph_elements.values() for coord in obj.coords]
        self.chart.canvas.coords(self.line, coords)

    def update_label(self):
        coords = list(self.graph_elements.values())[-1].coords
        self.chart.canvas.coords(self.label_obj, coords[0] + 10, coords[1])

    def _get_data_for_frame_x(self, time, df_x=None):
        if not isinstance(df_x, pd.DataFrame):
            df_x = self.df_x
        return df_x.loc[time]

    def _get_data_for_frame_y(self, time, df_y=None):
        if not isinstance(df_y, pd.DataFrame):
            df_y = self.df_y
        return df_y.loc[time]

    def _set_color(self):
        if self.chart.sjcanvas and self.chart.sjcanvas.color_palette:
            color = self.chart.sjcanvas.color_palette[0]
            self.chart.sjcanvas.color_palette.pop(0)
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                           random.randint(min_color + 30, max_color)))

        self.color = cv._from_rgb(color)
        self.chart.colors[self.label] = color

class graph_element():

    def __init__(self, name=None, canvas=None, value=0, unit=None, font_color=(0,0,0), color=(0, 0, 0), font_size=12, chart=None, text_font="Microsoft JhengHei UI"):
        self.name = name
        self.canvas = canvas
        self.unit = unit
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart
        self.color = color
        self.text_font = text_font

        self.draw(value)

    def _set_color(self):
        self.color = cv._from_rgb(self.chart.color)

    def draw(self, value):
        # here we can add the options to draw objects to the screen using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        font_obj = font.Font(family=self.text_font, size=int(self.font_size))
        self.marker = self.canvas.create_oval(50, 50, 500, 500, fill=cv._from_rgb((255,255,255)), outline=self.color, width=3)
        # self.label = self.canvas.create_text(self.pos, self.chart.y_pos + 0.85*self.chart.height, text=self.name, anchor="nw", font=font_obj, fill=cv._from_rgb(self.font_color), angle=-35)
        # self.value = self.canvas.create_text(0, 0, text=cv.format_value(value), anchor="w", font=font_obj, fill=cv._from_rgb(self.font_color))

    def update(self, x_value, y_value):
        # here we can update the size and location of the elements on the screen by using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        # self.canvas.coords(self.label, 10, 10)

        # we can also update the value
        # self.canvas.itemconfig(self.value, text=cv.format_value(value))
        y = self.chart.y_pos+0.85*self.chart.height-self.chart.y_axis.calc_positions(y_value)
        x = self.chart.x_axis.calc_positions(x_value) + self.chart.x_pos
        self.canvas.coords(self.marker, x - self.chart.marker_size/2, y - self.chart.marker_size/2, x + self.chart.marker_size/2, y + self.chart.marker_size/2)
        self.coords = (x,y)
        self.canvas.tag_raise(self.marker)

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df_y = DataHandler.DataHandler(excel_file="data/Y.xlsx", number_of_frames=60*15).df
    df_x = DataHandler.DataHandler(excel_file="data/X.xlsx", number_of_frames=60*15).df

    canvas = Canvas.canvas()

    dc = xy(canvas=canvas, df_x=df_x, df_y=df_y, font_size=25, font_color=(0, 0, 0), label="Henkie")
    canvas.add_sub_plot(dc)

    # adding a second series
    df_y2 = DataHandler.DataHandler(excel_file="data/Y2.xlsx", number_of_frames=60 * 15).df
    df_x2 = DataHandler.DataHandler(excel_file="data/X2.xlsx", number_of_frames=60 * 15).df
    dc.add_series(df_x2, df_y2, label="Gekke Henkie")

    df_y3 = DataHandler.DataHandler(excel_file="data/Y3.xlsx", number_of_frames=60 * 15).df
    df_x3 = DataHandler.DataHandler(excel_file="data/X3.xlsx", number_of_frames=60 * 15).df
    dc.add_series(df_x3, df_y3, label="Gekke Henkie 2")

    canvas.play(fps=60, record=True)