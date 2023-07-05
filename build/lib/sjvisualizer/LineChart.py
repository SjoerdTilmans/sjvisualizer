from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import *
from sjvisualizer import Axis
from sjvisualizer import Legend
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
MAX_POINTS = 100

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class line_chart(cv.sub_plot):
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

            :param draw_points: if set to True, the script will draw markers for each line, this may impact performance
            :type draw_points: boolean

            :param time_indicator: format of the timestamp, "day", "month", "year", default is "year"
            :type time_indicator: str

            :parem events: dictionary to add additional context to the line chart. For example to indicate events in time. Example:
            events = {
                "{EVENT NAME}": ["START DATE DD/MM/YYYY", "END DATE DD/MM/YYYY"],
                "Event 1": ["28/01/2017", "28/01/2018"],
                "Event 2": ["28/01/2019", "28/01/2020"],
                "Last event": ["28/05/2020", "28/01/2021"]
            }
            :type events: dict

            :param draw_all_events: by default only the label will be added to the most recent event. Set this value to True to keep the labels for all events
            :type draw_all_events: boolean

            """

    def draw(self, time):
        if hasattr(self, "font_size"):
            self.font_size = font_size / SCALEFACTOR
        else:
            self.font_size = self.height / 33 / SCALEFACTOR

        if not hasattr(self, "draw_points"):
            self.draw_points = True

        if not hasattr(self, "events"):
            self.events = {}

        if not hasattr(self, "draw_all_events"):
            self.draw_all_events = False

        if not hasattr(self, "default_min_value"):
            self.default_min_value = 0

        if not hasattr(self, "x_ticks"):
            self.default_min_value = 3

        if not hasattr(self, "y_ticks"):
            self.default_min_value = 3

        # making room for legend
        if self.sjcanvas:
            self.x_pos = self.x_pos - self.width / 10

        data = self._get_data_for_frame(time)

        self.axis1 = Axis.axis(canvas=self.canvas, n=self.x_ticks, orientation="horizontal", x=self.x_pos, y=self.y_pos+self.height, length=self.width, allow_decrease=False, is_date=True, time_indicator=self.time_indicator, font_size=self.font_size, color=self.font_color)

        self.min_time = time
        self.axis1.draw(min=self.min_time, max=self.min_time)

        self.axis2 = Axis.axis(canvas=self.canvas, n=self.y_ticks, orientation="vertical", x=self.x_pos, y=self.y_pos+self.height, length=self.height, width=self.width, allow_decrease=False, is_date=False, font_size=self.font_size, color=self.font_color, ticks_only=False, unit=self.unit)
        self.axis2.draw(min=min(data), max=max(data))

        self.lines = {}

        for name, d in data.items():
            self.lines[name] = line(name=name, canvas=self.canvas, value=d, time=time, font_color=self.font_color, colors=self.colors, xaxis=self.axis1, yaxis=self.axis2, draw_points=self.draw_points, chart=self)

        if self.sjcanvas:
            if len(self.df.columns) > 10:
                n_y = 10
            else:
                n_y = len(self.df.columns)
            self.legend = Legend.legend(canvas=self.canvas, height=self.height, width=500, x_pos=self.x_pos + self.width + 5*self.font_size, y_pos=self.y_pos, df=self.df, colors=self.colors, n=10, font_size=self.font_size, font_color=self.font_color)
            self.sjcanvas.add_sub_plot(self.legend)

        self.event_obj = []
        for name, dates in self.events.items():
            self.event_obj.append(event(name=name, canvas=self.canvas, start_date=dates[0], end_date=dates[1], font_color=self.font_color, font_size=self.font_size, parent=self))

    def update(self, time):
        self.max_time = time
        data = self._get_data_for_frame(time)
        self.axis1.update(min=self.min_time, max=self.max_time)
        if min(data) > self.default_min_value:
            self.axis2.update(min=0, max=max(data))
        else:
            self.axis2.update(min=min(data), max=max(data))

        if self.draw_points:
            total_points = sum([len(line.points) for name, line in self.lines.items()])

        for name, d in data.items():
            if MAX_POINTS < total_points:
                self.lines[name].point_radius = self.lines[name].point_radius - 0.25
            if self.lines[name].point_radius < 0:
                self.lines[name].remove_points()
            self.lines[name].update(d, time)

        for e in self.event_obj:
            if self.draw_all_events:
                e.draw_label = True
            e.update(time)

class event():

    def __init__(self, name=None, canvas=None, start_date=None, end_date=None, color=(225,225,225), font_color=(0,0,0), font_size=12, text_font="Microsoft JhengHei UI", parent=None):
        self.name = name
        self.canvas = canvas
        self.start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
        self.end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")
        self.color = cv._from_rgb(color)
        self.font_color = font_color
        self.font_size = font_size
        self.text_font = text_font
        self.font = font.Font(family=self.text_font, size=int(self.font_size))
        self.parent = parent

        self.drawn = False
        self.draw_label = False

        self.draw()

    def draw(self):
        self.rect = self.canvas.create_rectangle(-1000, -1000, -1000, -1000, fill=self.color, outline="")
        self.label = self.canvas.create_text(-1000, -1000, text=self.name, font=self.font, fill=cv._from_rgb(self.font_color), anchor="s")

    def update(self, date):
        if date > self.start_date:
            if not self.drawn:
                self.drawn = True
                for e in self.parent.event_obj:
                    e.draw_label = False
                self.draw_label = True

            pos1 = self.parent.axis1.calc_positions((self.start_date - datetime.datetime(1800,1,1)).days) + self.parent.x_pos
            if self.end_date > date:
                pos2 = self.parent.axis1.calc_positions(
                    (date - datetime.datetime(1800, 1, 1)).days) + self.parent.x_pos
            else:
                pos2 = self.parent.axis1.calc_positions((self.end_date - datetime.datetime(1800,1,1)).days) + self.parent.x_pos

            if self.draw_label:
                self.canvas.coords(self.label, (pos1 + pos2) / 2, self.parent.y_pos - 3)
            else:
                self.canvas.itemconfig(self.label, text="")

            self.canvas.coords(self.rect, pos1, self.parent.y_pos, pos2, self.parent.y_pos + self.parent.height)


class line():

    def __init__(self, name=None, canvas=None, value=0, unit=None, font_color=(0,0,0), colors=None, time=None, xaxis=None, yaxis=None, chart=None, draw_points=False):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.chart = chart
        self.draw_points = draw_points
        self.point_radius = int(2 + self.chart.height/150)
        self.line_width = int(1 + self.chart.height/200)

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

        self.line = None

        self.points = []

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

            if self.draw_points:
                try:
                    self.canvas.coords(self.points[i], coords[-2] - self.point_radius, coords[-1] - self.point_radius, coords[-2] + self.point_radius, coords[-1] + self.point_radius)
                except IndexError:
                    self.points.append(self.canvas.create_oval(coords[-2] - self.point_radius, coords[-1] - self.point_radius, coords[-2] + self.point_radius, coords[-1] + self.point_radius, fill=self.color))

        if not self.line:
            self.line = self.canvas.create_line(*coords, width=self.line_width, fill=self.color)
        else:
            self.canvas.coords(self.line, *coords)

    def remove_points(self):
        for p in self.points:
            self.canvas.delete(p)

        self.points = []
        self.draw_points = False