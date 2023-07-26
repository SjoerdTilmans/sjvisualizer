from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
from sjvisualizer import Axis
from sjvisualizer import Legend
from sjvisualizer import LineChart
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

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class area_chart(cv.sub_plot):
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

        :param time_indicator: format of the timestamp, "day", "month", "year", default is "year"
        :type time_indicator: str

        :param x_ticks: number of ticks on the x axis
        :type x_ticks: int

        :param y_ticks: number of ticks on the y axis
        :type y_ticks: int

        :parem events: dictionary to add additional context to the line chart. For example to indicate events in time. Example:
            events = {
                "{EVENT NAME}": ["START DATE DD/MM/YYYY", "END DATE DD/MM/YYYY"],
                "Event 1": ["28/01/2017", "28/01/2018"],
                "Event 2": ["28/01/2019", "28/01/2020"],
                "Last event": ["28/05/2020", "28/01/2021"]
            }
        :type events: dict

        :param event_color: color of the event indication, default is (225,225,225)
        :type event_color: tuple
        """

    def draw(self, time):
        if hasattr(self, "font_size"):
            self.font_size = self.font_size / SCALEFACTOR
        else:
            self.font_size = self.height / 33 / SCALEFACTOR

        if not hasattr(self, "draw_points"):
            self.draw_points = True

        if not hasattr(self, "x_ticks"):
            self.x_ticks = 3

        if not hasattr(self, "y_ticks"):
            self.y_ticks = 3

        # making room for legend
        if self.sjcanvas:
            self.x_pos = self.x_pos - self.width/10

        if not hasattr(self, "event_color"):
            self.event_color = (225,225,225)

        if not hasattr(self, "events"):
            self.events = {}

        if not hasattr(self, "draw_all_events"):
            self.draw_all_events = False

        data = self._get_data_for_frame(time)

        self.axis1 = Axis.axis(canvas=self.canvas, orientation="horizontal", n=self.x_ticks, x=self.x_pos, y=self.y_pos+self.height, length=self.width, allow_decrease=False, is_date=True, time_indicator="year", font_size=self.font_size, color=self.font_color)

        self.min_time = time
        self.axis1.draw(min=self.min_time, max=self.min_time)

        self.axis2 = Axis.axis(canvas=self.canvas, orientation="vertical", n=self.y_ticks, x=self.x_pos, y=self.y_pos+self.height, length=self.height, width=self.width, allow_decrease=False, is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=False, time_indicator=self.time_indicator)
        self.axis2.draw(min=min(data), max=max(data))

        self.areas = {}

        for name, d in data.items():
            self.areas[name] = area(name=name, canvas=self.canvas, value=d, time=time, font_color=self.font_color, colors=self.colors, xaxis=self.axis1, yaxis=self.axis2, draw_points=self.draw_points, chart=self)

        if self.sjcanvas:
            if len(self.df.columns) > 10:
                n_y = 10
            else:
                n_y = len(self.df.columns)
            self.legend = Legend.legend(canvas=self.canvas, height=self.height, width=500, x_pos=self.x_pos + self.width + 5*self.font_size, y_pos=self.y_pos, df=self.df, colors=self.colors, n=10, font_size=self.font_size, font_color=self.font_color)
            self.sjcanvas.add_sub_plot(self.legend)

        self.event_obj = []
        for name, dates in self.events.items():
            self.event_obj.append(
                LineChart.event(name=name, canvas=self.canvas, start_date=dates[0], end_date=dates[1], font_color=self.font_color,
                      font_size=self.font_size, parent=self, event_color=self.event_color))

    def update(self, time):
        self.max_time = time
        data = self._get_data_for_frame(time)
        self.axis1.update(min=self.min_time, max=self.max_time)
        self.axis2.update(min=0, max=sum(data))

        area_height = sum(data)
        for name, d in data.items():
            self.areas[name].update(area_height, time)
            area_height = area_height - d

        for e in self.event_obj:
            if self.draw_all_events:
                e.draw_label = True
            e.update(time)

class area():

    def __init__(self, name=None, canvas=None, value=0, unit=None, font_color=(0,0,0), colors=None, time=None, xaxis=None, yaxis=None, chart=None, draw_points=False):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.chart = chart
        self.draw_points = draw_points
        self.point_radius = 5

        self.x_values = []
        self.y_values = []

        if isinstance(colors, dict):
            if name in colors:
                self.color = cv._from_rgb(colors[name])
            else:
                color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                               random.randint(min_color + 30, max_color)))
                self.color = cv._from_rgb(color)
                colors[name] = color
        else:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color),
                           random.randint(min_color + 30, max_color)))
            self.color = cv._from_rgb(color)

        self.draw(value, time)

    def draw(self, value, time):
        self.x_values.append((time - datetime.datetime(1800,1,1)).days)
        self.y_values.append(value)

        self.area = None

    def update(self, value, time):
        if time.hour == 0 and time.minute == 0 and time.second == 0:
            self.x_values.append((time - datetime.datetime(1800,1,1)).days)
            self.y_values.append(value)

        x_values_to_draw = self.x_values.copy()
        x_values_to_draw.append((time - datetime.datetime(1800,1,1)).days)
        y_values_to_draw = self.y_values.copy()
        y_values_to_draw.append(value)

        coords = []

        for i, (x, y) in enumerate(zip(x_values_to_draw, y_values_to_draw)):
            coords.append(self.chart.x_pos + self.xaxis.calc_positions(x))
            coords.append(self.chart.y_pos + self.chart.height - self.yaxis.calc_positions(y))

        coords.append(self.xaxis.x + self.xaxis.length)
        coords.append(self.xaxis.y)
        coords.append(self.xaxis.x)
        coords.append(self.xaxis.y)

        if not self.area:
            self.area = self.canvas.create_polygon(*coords, width=2, fill=self.color, outline="black")
        else:
            self.canvas.coords(self.area, *coords)