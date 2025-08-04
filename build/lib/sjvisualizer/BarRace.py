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
from sjvisualizer import Axis

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

class bar_race(cv.sub_plot):
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

            :param number_of_bars: number of bars to be displayed in the chart
            :type text_font: int

            :param decimal_places: number of decimal places to be displayed on the y-axis
            :type decimal_places: int
            """

    def draw(self, time):
        """This function gets executed only once at the start of the animation"""
        # draw boudning box
        # self.canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height)

        # get the data for the given time step
        data = self._get_data_for_frame(time)

        # create a dictionary to hold all graph_element objects
        self.graph_elements = {}

        # calculate desired bar_height
        bar_height = int(self.height / self.number_of_bars * 0.75)

        # loop over all values in the row
        for i, (name, d) in enumerate(data.items()):
            self.graph_elements[name] = bar(name=name, canvas=self.canvas, value=d, unit=self.unit, font_color=self.font_color, colors=self.colors, chart=self, text_font=self.text_font, font_size=self.font_size, bar_height=bar_height)

        # create axis
        data = self._get_data_for_frame(time)
        self.axis1 = Axis.axis(canvas=self.canvas, decimal_places=self.decimal_places, n=4, orientation="horizontal", x=self.x_pos + int(1/4 * self.width),
                  y=self.y_pos, length=self.width - int(1/4 * self.width), allow_decrease=False, is_date=False,
                  font_size=int(self.font_size / SCALEFACTOR / 1.5), color=self.font_color, anchor="n", width=self.height)
        self.axis1.draw(min=min(data), max=max(data))

    def update(self, time):
        """This function gets executed every frame"""
        # get the data for the given time step
        data = self._get_data_for_frame(time)
        # loop over all values in the row
        bar_y_pos = self.y_pos + (self.height / self.number_of_bars) / 2
        if self.sort:
            data = self._get_data_for_frame(time).sort_values(ascending=False)
        for i, (name, d) in enumerate(data.items()):
            if d:
                if i == self.number_of_bars:
                    bar_y_pos = HEIGHT + (self.height / self.number_of_bars)
                if i < self.number_of_bars + 1:
                    self.graph_elements[name].update(d, bar_y_pos)
                else:
                    self.graph_elements[name].delete()
                bar_y_pos = bar_y_pos + (self.height / self.number_of_bars)
            else:
                self.graph_elements[name].delete()

        # update axis
        self.axis1.update(min=min(data), max=max(data))


class bar():

    def __init__(self, name=None, canvas=None, value=0, font_color=(0,0,0), colors={}, font_size=12, chart=None, text_font="Microsoft JhengHei UI", bar_height=50, unit=""):
        self.name = name
        self.canvas = canvas
        self.unite = unit
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart
        self.colors = colors
        self.text_font = text_font
        self.exists = False
        self.bar_height = bar_height
        self.unit = unit

        self.mass = 2
        self.stiffness = 0.1
        self.damping = 0.6

        self.v = 0
        self.a = 0

        try:
            self.img = cv.load_image(os.path.join("assets", self.name.replace("*", "") + ".png"), int(bar_height), int(bar_height), self.chart.root, name)
        except:
            print("No image for {}".format(self.name))
            self.img = None

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
        self.rect = self.canvas.create_rectangle(50, 50, 500, 500, fill=self.color, outline="")
        self.label = self.canvas.create_text(0, 0, text=self.name, anchor="e", font=font_obj, fill=cv._from_rgb(self.font_color))
        self.value = self.canvas.create_text(0, 0, text=cv.format_value(value, decimal=self.chart.decimal_places), anchor="w", font=font_obj, fill=cv._from_rgb(self.font_color))
        if self.img:
            self.img_obj = self.canvas.create_image(-1000, -1000, image=self.img, anchor="w")
        self.exists = True

    def update(self, value, bar_y_pos):
        # here we can update the size and location of the elements on the screen by using standard tkinter functions
        # in reality you want the size and position of the elements to be derived from the value
        if value:
            if self.exists:
                self.canvas.coords(self.label, 10, 10)
                if not hasattr(self, "y"):
                    self.y = bar_y_pos

                # calculate correct position
                F = self.stiffness * (bar_y_pos - self.y) - self.damping * self.v
                self.a = F / self.mass
                self.v = self.v + self.a
                self.y = self.y + self.v

                # change bar based on value
                self.canvas.coords(self.rect,
                                   self.chart.axis1.calc_positions(0) + self.chart.x_pos + int(1 / 4 * self.chart.width),
                                   self.y - self.bar_height / 2,
                                   self.chart.axis1.calc_positions(value) + self.chart.x_pos + int(
                                       1 / 4 * self.chart.width), self.y + self.bar_height / 2)

                # we can also update the value
                rect_bbox = self.canvas.coords(self.rect)
                self.canvas.itemconfig(self.value, text=cv.format_value(value, decimal=self.chart.decimal_places) + self.unit)

                # check if value text fits inside bar
                value_bbox = self.canvas.bbox(self.value)
                if (rect_bbox[2] - rect_bbox[0]) * 0.75 > (value_bbox[2] - value_bbox[0]):
                    self.canvas.coords(self.value, rect_bbox[2] - 10, self.y)
                    self.canvas.itemconfig(self.value, anchor="e")
                else:
                    self.canvas.coords(self.value, rect_bbox[2] + 10, self.y)
                    self.canvas.itemconfig(self.value, anchor="w")

                # update label
                self.canvas.coords(self.label, self.chart.x_pos + int(1/4 * self.chart.width) - 10, self.y)

                value_bbox = self.canvas.bbox(self.value)
                # update img
                if self.img:
                    self.canvas.coords(self.img_obj, value_bbox[2] + 20, self.y)

            else:
                self.y = bar_y_pos
                self.v = 0
                self.a = 0
                self.draw(value)
                self.update(value, bar_y_pos)
        else:
            self.delete()

    def delete(self):
        self.canvas.delete(self.label)
        self.canvas.delete(self.value)
        self.canvas.delete(self.rect)
        if self.img:
            self.canvas.delete(self.img_obj)
        self.exists = False

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df = DataHandler.DataHandler(excel_file="data/Neg Number Bar Dev.xlsx", number_of_frames=0.25*60*60).df

    canvas = Canvas.canvas()

    bar_chart = bar_race(canvas=canvas, df=df, decimal_places=3)
    canvas.add_sub_plot(bar_chart)

    canvas.play(fps=60, record=False)