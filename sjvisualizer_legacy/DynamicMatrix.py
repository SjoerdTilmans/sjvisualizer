from sjvisualizer import Canvas as cv
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

class dynamic_matrix(cv.sub_plot):
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

            :param text_font: selected font, defaults to Microsoft JhengHei UI
            :type text_font: str

            :param level_count: defines the number of discrete sentiment levels displayed in the chart. If set to 3 the chart will display --- to +++, defaults to 2
            :type level_count: int

            :param neutral_string: string to indicate a neutral value, by default set to 0
            :type neutral_string: str

            :param color_range: list of 2 lists indicating the rgb values for fully negative to fully positive, defaults to [(255, 40, 60), (3, 175, 81)]
            :type color_range: list(list)
            """

    def draw(self, time):
        """This function gets executed only once at the start of the animation"""
        # get the data for the given time step
        data = self._get_data_for_frame(time)

        # create a dictionary to hold all graph_element objects
        self.graph_elements = {}

        self.spacing = self.height / len(data) / 2

        if not hasattr(self, "neutral_string"):
            self.neutral_string = "0"

        if not hasattr(self, "font_size"):
            self.font_size = self.spacing

        if not hasattr(self, "level_count"):
            self.level_count = 2

        if not hasattr(self, "color_range"):
            self.color_range = None

        y = self.y_pos + self.spacing

        # keep track of label widths
        self.max_label_width = 0

        # loop over all values in the row
        for i, (name, d) in enumerate(data.items()):
            self.graph_elements[name] = graph_element(name=name, y=y, canvas=self.canvas, value=d, unit=self.unit, font_color=self.font_color, colors=self.colors, chart=self, text_font=self.text_font, font_size=self.font_size)
            y = y + 2 * self.spacing
            if i < len(data) - 1:
                self.canvas.create_line(self.x_pos, y - self.spacing, self.x_pos + self.width, y - self.spacing, fill=cv._from_rgb((200, 200, 200)))
            x1, y1, x2, y2 = self.canvas.bbox(self.graph_elements[name].label)
            label_width = x2 - x1
            if label_width > self.max_label_width:
                self.max_label_width = label_width

        self._draw_boxes()

    def _draw_boxes(self):
        spacing = 0
        font_obj_bold = font.Font(family=self.text_font, size=int(self.font_size / SCALEFACTOR), weight="bold")
        labels = self._generate_sentiment_levels(self.level_count)
        self.box_width = (self.width - self.max_label_width * 1.1) / len(labels)
        for label in labels:
            self.canvas.create_line(self.x_pos + self.max_label_width * 1.1 + spacing, self.y_pos, self.x_pos + self.max_label_width * 1.1 + spacing, self.y_pos + self.height, fill=cv._from_rgb((200, 200, 200)))
            self.canvas.create_text(self.x_pos + self.max_label_width * 1.1 + spacing + self.box_width / 2, self.y_pos, text=label,
                                    anchor="s", font=font_obj_bold, fill=cv._from_rgb(self.font_color))

            spacing = spacing + self.box_width

    def _generate_sentiment_levels(self, level_count: int) -> list[str]:
        """
        Generates a list of sentiment level strings based on the given level_count.

        Args:
            level_count (int): An integer >= 1. Defines the maximum sentiment depth.
                               The output will range from -level_count to +level_count, centered at '0'.
                               For example:
                                   2 -> ['--', '-', '0', '+', '++']
                                   3 -> ['---', '--', '-', '0', '+', '++', '+++']

        Returns:
            List[str]: A list of sentiment strings from negative to positive.
        """
        if level_count < 1:
            raise ValueError("level_count must be an integer ≥ 1.")

        levels = []
        for i in range(-level_count, level_count + 1):
            if i == 0:
                levels.append(self.neutral_string)
            elif i < 0:
                levels.append("-" * abs(i))
            else:
                levels.append("+" * i)
        return levels

    def update(self, time):
        """This function gets executed every frame"""
        # get the data for the given time step
        data = self._get_data_for_frame(time)
        # loop over all values in the row
        for i, (name, d) in enumerate(data.items()):
            self.graph_elements[name].update(d)


class graph_element():

    def __init__(self, name=None, y=0, canvas=None, value=0, unit=None, font_color=(0,0,0), colors={}, font_size=12, chart=None, text_font="Microsoft JhengHei UI"):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart
        self.colors = colors
        self.text_font = text_font
        self.y = y

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
        font_obj = font.Font(family=self.text_font, size=int(self.font_size / SCALEFACTOR))
        font_obj_bold = font.Font(family=self.text_font, size=int(self.font_size / SCALEFACTOR), weight="bold")
        self.bar = self.canvas.create_rectangle(50, 50, 500, 500, fill=self.color, outline="")
        if not "+" in self.name:
            self.label = self.canvas.create_text(self.chart.x_pos, self.y, text=self.name, anchor="w", font=font_obj_bold, fill=cv._from_rgb(self.font_color))
        else:
            tabs = self.name.count("+")
            self.label = self.canvas.create_text(self.chart.x_pos, self.y, text=tabs * "      " + self.name.replace("+",""), anchor="w",
                                                 font=font_obj, fill=cv._from_rgb(self.font_color))

        # self.value = self.canvas.create_text(0, self.y, text=cv.format_value(value), anchor="w", font=font_obj, fill=cv._from_rgb(self.font_color))

    def update(self, value):
        # here we can update the size and location of the elements on the screen by using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        # we can also update the value
        # self.canvas.itemconfig(self.value, text=cv.format_value(value))
        x = self._calc_x(value)
        self.canvas.coords(self.bar, x, self.y - self.chart.spacing / 2 * 1.5, x + self.chart.box_width, self.y + self.chart.spacing / 2 * 1.5)
        self.canvas.tag_raise(self.bar)
        self._calc_color(value)
    def _calc_x(self, value):
        min_pos = self.chart.x_pos + self.chart.max_label_width * 1.1
        max_pos = self.chart.x_pos + self.chart.width - self.chart.box_width
        if value <= -self.chart.level_count:
            x = min_pos
        elif value >= self.chart.level_count:
            x = max_pos
        else:
            fraction = (value + self.chart.level_count) / (self.chart.level_count * 2)
            x = fraction * max_pos + (1- fraction) * min_pos
        return x

    def _calc_color(self, value):
        # default settings
        if self.chart.level_count == 2 and not self.chart.color_range:
            colors = [(255, 40, 60), (224, 85, 105), (210, 210, 210), (147, 209, 81), (3, 175, 81)]
            if value <= - 2:
                color = colors[0]
            elif value < -1:
                fraction = value + 2
                color = [a + b for a, b in zip([int(x * fraction) for x in colors[1]], [int(x * (1 - fraction)) for x in colors[0]])]
            elif value < 0:
                fraction = value + 1
                color = [a + b for a, b in zip([int(x * fraction) for x in colors[2]], [int(x * (1 - fraction)) for x in colors[1]])]
            elif value < 1:
                fraction = value
                color = [a + b for a, b in zip([int(x * fraction) for x in colors[3]], [int(x * (1 - fraction)) for x in colors[2]])]
            elif value < 2:
                fraction = value - 1
                color = [a + b for a, b in zip([int(x * fraction) for x in colors[4]], [int(x * (1 - fraction)) for x in colors[3]])]
            elif value >= 2:
                color = colors[-1]
        # when a custom color range is given, or when more levels are defined
        else:
            if self.chart.color_range:
                colors = self.chart.color_range
            else:
                colors = [(255, 40, 60), (3, 175, 81)]
            if value <= -self.chart.level_count:
                color = colors[0]
            elif value >= self.chart.level_count:
                color = colors[1]
            elif value <= 0:
                fraction = abs(value) / self.chart.level_count
                color = [a + b for a, b in zip([int(x * (1 - fraction)) for x in (210, 210, 210)], [int(x * fraction) for x in colors[0]])]
            elif value > 0:
                fraction = abs(value) / self.chart.level_count
                color = [a + b for a, b in zip([int(x * fraction) for x in colors[1]],
                                               [int(x * (1 - fraction)) for x in (210, 210, 210)])]

        self.canvas.itemconfig(self.bar, fill=cv._from_rgb(color))

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df = DataHandler.DataHandler(excel_file="data/DynamicMatrix.xlsx", number_of_frames=60*10).df

    canvas = Canvas.canvas()

    empty_chart = dynamic_matrix(canvas=canvas, font_size=25, df=df, neutral_string="Neutral", level_count=3)
    canvas.add_sub_plot(empty_chart)

    canvas.add_time(df=df, time_indicator="day")
    canvas.add_title("Dynamic Matrix")

    canvas.play(fps=60)