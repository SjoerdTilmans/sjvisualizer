from sjvisualizer.Canvas import _from_rgb, sub_plot, format_date, truncate, calc_spacing, load_image
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

min_slice = 0.0
min_slice_image = 0.075
min_slice_percentage_display = 0.055
decimal_places = 0
text_font = "Microsoft JhengHei UI"
min_color = 20
max_color = 225
UNDERLINE = 0
LINE_END_SPACING = 20
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

class stacked_bar_chart(sub_plot):
    """
        Class to construct an animated stack bar chart

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

        :param unit: unit of the values visualized, default is ""
        :type unit: str

        :param font_color: font color, default is (0,0,0)
        :type font_color: tuple of length 3 with integers

        :param number_of_bars: number of horizontal bars to display in the animation, default is 10.
        :type number_of_bars: int
        """
    def draw(self, time):
        self.bar_time_spacing = (self.df.index[-1 - 600] - self.df.index[0]) / (self.number_of_bars - 1)
        self.current_number_of_bars = 0

        if not hasattr(self, "x_ticks"):
            self.x_ticks = 10

        if not hasattr(self, "y_ticks"):
            self.y_ticks = 5

        if self.time_indicator == "year":
            text = str(time.year)
        elif self.time_indicator == "month":
            text = str(f"{months[time.month]} {time.year}")
        elif self.time_indicator == "day":
            text = str(f"{time.day} {months[time.month]} {time.year}")

        self.font_size = int(10 + self.height/50 / SCALEFACTOR)
        self.font = font.Font(family=text_font, size=self.font_size, weight="bold")

        self.total_time = self.df.index[-1-600] - self.df.index[0]
        time_fraction = (time - self.df.index[0]) / self.total_time
        self.x_axis_line = self.canvas.create_line(self.x_pos, self.y_pos + self.height, self.x_pos + self.width * time_fraction, self.y_pos + self.height, fill="grey", width=int(self.height/400)+1)
        self.end_size = int(self.height/150)
        self.end = self.canvas.create_line(self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height, self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size, fill=_from_rgb(self.font_color), width=int(self.height/400)+1)
        self.start = self.canvas.create_line(self.x_pos + (int(self.height/400)+1)/2, self.y_pos + self.height, self.x_pos + (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size, fill=_from_rgb(self.font_color), width=int(self.height/400)+1)

        # write first and last labels on x_axis
        self.start_text = self.canvas.create_text(self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size + self.font_size, font=self.font, text=text, fill=_from_rgb(self.font_color))
        self.end_text = self.canvas.create_text(self.x_pos + (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size+ self.font_size, font=self.font, text=text, fill=_from_rgb(self.font_color))

        self._calc_next_tick(time)

        self.draw_y_ticks(time)

        data = self._get_data_for_frame(time)

        self.bars = [stacked_bar_graph_bar(canvas=self.canvas, number=0, number_of_bars=self.number_of_bars, data=data, colors=self.colors, max_value=data.sum(), width=self.width, height=self.height, x_pos=self.x_pos, y_pos=self.y_pos)]

    def draw_y_ticks(self, time):
        self._calc_max_value()
        self.y_tick_spacing = truncate(self.max_value / self.y_ticks, 1 - len(str(int(truncate(self.max_value / self.y_ticks, 0)))))

        self.current_max_value = self._get_data_for_frame(time).sum()

        y = self.y_tick_spacing
        self.y_ticks_list = []
        for i in range(self.y_ticks):
            self.y_ticks_list.append(bar_graph_y_tick(self.canvas, y, self.current_max_value, self.width, self.height, self.x_pos, self.y_pos, self.unit, self.font_size, font_color=self.font_color))
            y = y + self.y_tick_spacing

    def _calc_max_value(self):
        self.max_value = 0
        for index, row in self.df.iterrows():
            if row.sum() > self.max_value:
                self.max_value = row.sum()

    def update(self, time):
        time_fraction = (time - self.df.index[0]) / self.total_time
        self.canvas.coords(self.x_axis_line, self.x_pos, self.y_pos + self.height, self.x_pos + self.width * time_fraction, self.y_pos + self.height)
        self.canvas.coords(self.end, self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height, self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size)

        if self.time_indicator == "year":
            text = str(time.year)
        elif self.time_indicator == "month":
            text = str(f"{months[time.month]} {time.year}")
        elif self.time_indicator == "day":
            text = str(f"{time.day} {months[time.month]} {time.year}")

        self.canvas.coords(self.end_text, self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size + self.font_size)
        self.canvas.itemconfig(self.end_text, text="")

        if time >= self.next_xtick:
            self.canvas.itemconfig(self.end_text, text=text)
            self.end_text = self.canvas.create_text(self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size + self.font_size, font=self.font, text=text, fill=_from_rgb(self.font_color))
            self.end = self.canvas.create_line(self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height, self.x_pos + self.width * time_fraction - (int(self.height/400)+1)/2, self.y_pos + self.height + self.end_size, fill=_from_rgb(self.font_color), width=int(self.height / 400) + 1)
            self._calc_next_tick(time)

        if self._get_data_for_frame(time).sum() > self.current_max_value:
            self.current_max_value = self._get_data_for_frame(time).sum()

        for y_tick in self.y_ticks_list:
            y_tick.update(self.current_max_value, time_fraction)

        for bar in self.bars:
            bar.update(self.current_max_value)

        if time >= self.df.index[0] + self.bar_time_spacing * self.current_number_of_bars:
            data = self._get_data_for_frame(time)
            self.bars.append(stacked_bar_graph_bar(canvas=self.canvas, number=self.current_number_of_bars, number_of_bars=self.number_of_bars, data=data, colors=self.colors, max_value=self.current_max_value, width=self.width, height=self.height, x_pos=self.x_pos, y_pos=self.y_pos))
            self.current_number_of_bars = self.current_number_of_bars + 1



    def _calc_next_tick(self, time):
        dt = self.total_time / (self.x_ticks - 1) - datetime.timedelta(days=1)

        for i in range(self.x_ticks):
            if time == self.df.index[0]:
                self.next_xtick = self.df.index[0] + dt
                return
            elif time < self.df.index[0] + i*dt:
                self.next_xtick = self.df.index[0] + i * dt
                return

        self.next_xtick = self.df.index[-1]

class stacked_bar_graph_bar():

    def __init__(self, canvas, number, number_of_bars, data, colors, max_value, width, height, x_pos, y_pos):
        self.number = number
        self.number_of_bars = number_of_bars
        self.data = data
        self.colors = colors
        self.max_value = max_value
        self.canvas = canvas

        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos

        self.bars = []
        self.bar_values = []

        self.scale = 0

        self.stiffness = 0.05
        self.damping = 0.3
        self.mass = 1.0

        self.v = 0
        self.a = 0

        self.draw()

    def draw(self):
        F = self.stiffness * (1 - self.scale) - self.damping * self.v

        self.a = F / self.mass
        self.v = self.v + self.a
        self.scale = self.scale + self.v

        current_y = self.y_pos + self.height

        self.bar_width = (self.width - (self.number_of_bars - 1) * 3) / self.number_of_bars
        self.x1 = self.x_pos + self.number * (self.bar_width + 3)
        self.x2 = self.x1 + self.bar_width
        for name, value in self.data.items():
            fraction = value / self.data.sum()
            if fraction > min_slice and not name == "Others":
                new_y = current_y + value / self.max_value * self.height * self.scale
                if name in self.colors:
                    color = _from_rgb(tuple(self.colors[name]))
                else:
                    color = _from_rgb((20,20,100))
                self.bars.append(self.canvas.create_rectangle(self.x1, current_y, self.x2, new_y, fill=color, outline=""))
                current_y = new_y
                self.bar_values.append(value)

        self.bars.append(self.canvas.create_rectangle(self.x1, current_y, self.x2, self.y_pos+self.height, fill="grey", outline=""))
        self.bar_values.append(None)

    def update(self, current_max_value):

        if abs(self.a) > 0.0 and abs(self.v) > 0.0:
            F = self.stiffness * (1 - self.scale) - self.damping * self.v

            self.a = F / self.mass
            self.v = self.v + self.a
            self.scale = self.scale + self.v

            current_y = self.y_pos + (current_max_value - self.data.sum()) / current_max_value * self.height
            current_y = self.scale * current_y + (1 - self.scale) * (self.y_pos + self.height)
        else:
            current_y = self.y_pos + (current_max_value - self.data.sum()) / current_max_value * self.height

        for bar, value in zip(self.bars, self.bar_values):
            self.canvas.tag_raise(bar)
            if value:
                new_y = current_y + value / current_max_value * self.height * self.scale
            else:
                new_y = self.y_pos + self.height
            self.canvas.coords(bar, self.x1, current_y, self.x2, new_y)
            current_y = new_y

class bar_graph_y_tick():

    def __init__(self, canvas, value, max_value, width, height, x_pos, y_pos, unit, font_size, font_color=(0, 0, 0)):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.value = value
        self.unit = unit
        self.font_size = font_size
        self.font = font.Font(family=text_font, size=self.font_size, weight="bold")
        self.font_color = font_color

        self.draw(max_value)

    def draw(self, max_value, fraction=0):

        if self.value < max_value:
            self.line = self.canvas.create_line(self.x_pos, self.y_pos + self.height - self.value / max_value * self.height, self.x_pos + fraction * self.width, self.y_pos + self.height - self.value / max_value * self.height, fill="grey", dash=(3, 1))
            self.text = self.canvas.create_text(self.x_pos, self.y_pos + self.height - self.value / max_value * self.height, text=format(self.value, ",.0f") + self.unit, anchor="e", font=self.font)
        else:
            self.line = self.canvas.create_line(self.x_pos, self.y_pos + self.height - self.value / max_value * self.height, self.x_pos + self.width, self.y_pos + self.height - self.value / max_value * self.height, fill="", dash=(3, 1))
            self.text = self.canvas.create_text(self.x_pos,
                                                self.y_pos + self.height - self.value / max_value * self.height,
                                                text=format(self.value, f",.{decimal_places}f") + self.unit, anchor="e", fill=_from_rgb(self.font_color), font=self.font)

    def update(self, max_value, fraction):
        if self.value < max_value:
            self.canvas.coords(self.line, self.x_pos, self.y_pos + self.height - self.value / max_value * self.height, self.x_pos + fraction * self.width, self.y_pos + self.height - self.value / max_value * self.height)
            self.canvas.itemconfig(self.line, fill = "grey")
            self.canvas.tag_raise(self.line)
            self.canvas.coords(self.text, self.x_pos, self.y_pos + self.height - self.value / max_value * self.height)
            self.canvas.itemconfig(self.text, fill = _from_rgb(self.font_color))
            self.canvas.tag_raise(self.text)
        else:
            self.canvas.itemconfig(self.line, fill = "")
            self.canvas.itemconfig(self.text, fill = "")