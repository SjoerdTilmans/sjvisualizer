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

class bar_race(cv.sub_plot):
    """
    Class to construct a bar race

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

    :param back_ground_color: color of the background. To hide bars that fall outside of the top X, a square is drawn
    at the bottom of the visualization. Typically you want this square to match the color of the background. Default is (255,255,255)
    :type back_ground_color: tuple of length 3 with integers

    :param font_color: font color, default is (0,0,0)
    :type font_color: tuple of length 3 with integers

    :param sort: should the values of this plot be softed? True/False, default is True
    :type sort: boolean

    :param number_of_bars: number of bars to display in the animation, default is 10 unless you have less than 10 data categories
    :type number_of_bars: int
    """
    def draw(self, time):
        self.distance = self.height / (self.number_of_bars+(self.number_of_bars+1)*0.5)
        self.bars = {}

        if not hasattr(self, "mode"):
            self.mode = None
            self.min_slice_size = 1
        else:
            self.min_slice_size = min_slice

        if not hasattr(self, "shift"):
            self.shift = 0

        if not hasattr(self, "font_scale"):
            self.font_scale = 1

        if self.invert:
            data = self._get_data_for_frame(time).sort_values(ascending=True)
            names = []
            values = []
            for name, value in data.iteritems():
                if abs(value) > 0:
                    names.append(name)
                    values.append(value)
                else:
                    names.append(name)
                    values.append(10 ** 80)
            data = pd.Series(values, index=names).sort_values(ascending=True)

        else:
            data = self._get_data_for_frame(time).sort_values(ascending=False)

        if self.mode == "Other":
            sum = data.sum()
            for name, d in data.iteritems():
                if d / sum > min_slice:
                    data[name] = 0

        if isinstance(self.multi_color_df, pd.DataFrame):
            data_multi_color = self._get_data_for_frame(time, df=self.multi_color_df)
            self.multi_colors = {}
            for index in data_multi_color.index:
                color_name = index.split("_")[-1]
                self.multi_colors[color_name] = self.colors[color_name]
        else:
            data_multi_color = None
            self.multi_colors = None

        self.stripes = bar_stripes(self.canvas, self.y_pos, self.y_pos + self.height, data, self.x_pos + self.width/5, self.width*0.75, self.height, self.number_of_bars, self.invert, allow_decrease=self.allow_decrease)

        current_height = self.distance/2 + self.y_pos
        bar_number = 0
        for i, (name, value) in enumerate(data.iteritems()):
            if not self.invert:
                fraction = value / data.max()
                self.current_max = data.max()
            else:
                fraction = value / data.iloc[self.number_of_bars]
                self.current_max = data.iloc[self.number_of_bars]

            if name in self.colors:
                color = self.colors[name]
            else:
                color = None

            if fraction > 0.0000001 and bar_number < self.number_of_bars and not name == "Other":
                self.bars[name] = bar(name=name, canvas=self.canvas, x=self.x_pos + self.width/5, target_y=current_height, color=color, root=self.root, size=int(self.distance), width=fraction*self.width*0.75, radius=0, value=value, unit=self.unit, display_value=self.display_value, multi_colors=self.multi_colors, color_data=data_multi_color, font_color=self.font_color, mode=self.mode, colors=self.colors, decimal_places=self.decimal_places, font_scale=self.font_scale)
                current_height = current_height + 3 * self.distance / 2
                bar_number = bar_number + 1
            else:
                if self.origin == "n":
                    self.bars[name] = bar(name=name, canvas=self.canvas, x=self.x_pos + self.width / 5,
                                          target_y=-500, color=color, root=self.root,
                                          size=int(self.distance), width=fraction*self.width*0.75, radius=0, unit=self.unit, display_value=self.display_value, multi_colors=self.multi_colors, color_data=data_multi_color, font_color=self.font_color, mode=self.mode, colors=self.colors, decimal_places=self.decimal_places, font_scale=self.font_scale)
                elif self.origin == "s":
                    self.bars[name] = bar(name=name, canvas=self.canvas, x=self.x_pos + self.width / 5,
                                          target_y=self.distance/2 + self.y_pos + (self.number_of_bars) * 3 * self.distance / 2 + self.shift, color=color, root=self.root,
                                          size=int(self.distance), width=fraction*self.width*0.75, radius=0, unit=self.unit, display_value=self.display_value, multi_colors=self.multi_colors, color_data=data_multi_color, font_color=self.font_color, mode=self.mode, colors=self.colors, decimal_places=self.decimal_places, font_scale=self.font_scale)

        self.rec = self.canvas.create_rectangle(self.x_pos - 125, self.y_pos + self.height + self.shift, self.x_pos + self.width, self.y_pos + self.height + 1.35 * self.distance + self.shift, fill = cv._from_rgb(self.back_ground_color), outline="")


    def update(self, time):
        if self.invert:
            data = self._get_data_for_frame(time).sort_values(ascending=True)
            names = []
            values = []

            for name, value in data.iteritems():
                if abs(value) > 0:
                    names.append(name)
                    values.append(value)
                else:
                    names.append(name)
                    values.append(10 ** 80)
            data = pd.Series(values, index=names).sort_values(ascending=True)
        else:
            data = self._get_data_for_frame(time).sort_values(ascending=False)

        if self.mode == "Other":
            sum = data.sum()
            for name, d in data.iteritems():
                if d / sum > min_slice or name == "Other":
                    data[name] = 0

        current_height = self.distance / 2 + self.y_pos
        self.stripes.update(data)

        if isinstance(self.multi_color_df, pd.DataFrame):
            data_multi_color = self._get_data_for_frame(time, df=self.multi_color_df)
        else:
            data_multi_color = None

        bar_number = 0
        for i, (name, value) in enumerate(data.iteritems()):
            if i < 1.5 * self.number_of_bars:
                if not self.invert:
                    if self.allow_decrease:
                        fraction = value / data.max()
                    else:
                        if self.current_max < data.max():
                            self.current_max = data.max()

                        fraction = value / self.current_max
                else:
                    if self.allow_decrease:
                        fraction = value / data.iloc[self.number_of_bars]
                    else:
                        if self.current_max < data.iloc[self.number_of_bars]:
                            self.current_max = data.iloc[self.number_of_bars]

                        fraction = value / self.current_max

                if fraction > 0.00000001 and bar_number < self.number_of_bars and not name == "Other":
                    self.bars[name].update(target_y=current_height, width=fraction*self.width*0.75, value=value, color_data=data_multi_color)
                    current_height = current_height + 3 * self.distance / 2
                    bar_number = bar_number + 1
                else:
                    if self.origin == "s":
                        self.bars[name].update(target_y=self.distance/2 + self.y_pos + (self.number_of_bars) * 3 * self.distance / 2 +  + self.shift, width=fraction*self.width*0.75, color_data=data_multi_color, value=value)
                    elif self.origin == "n":
                        self.bars[name].update(target_y=-500, width=fraction*self.width*0.75, color_data=data_multi_color, value=value)
            else:
                self.bars[name].delete()

        self.canvas.tag_raise(self.rec)

class bar():

    def __init__(self, name=None, canvas=None, color=None, root=None, target_y=0, x=100, size=10, width=0, radius=0, value=0, unit=None, display_value=True, multi_colors=None, color_data=None, font_color=(0,0,0), mode=None, colors=None, decimal_places=decimal_places, font_scale=1):
        self.mass = 2
        self.stiffness = 0.2 * size / 100
        self.damping = 0.6

        self.display_value = display_value

        if unit and "$" in unit:
            self.unit = unit.replace("$", "")
            self.money = "$"
        elif unit:
            self.unit = unit
            self.money = ""
        else:
            self.unit = ""
            self.money = ""

        self.decimal_places = decimal_places

        self.radius = radius
        self.colors = colors
        self.font_scale = font_scale

        self.name = name
        self.canvas = canvas
        self.color = color
        self.root = root
        self.x = x

        self.multi_colors = multi_colors

        self.size = size

        self.font_color = font_color


        self.font_size = int(size/2 / SCALEFACTOR * font_scale)
        self.font = font.Font(family=text_font, size=self.font_size, weight="bold")

        self.target_y = target_y
        self.y = copy.copy(target_y)
        self.v = 0
        self.a = 0

        try:
            if self.name == "USSR/Russia":
                img = cv.load_image(os.path.join("assets", "Russia".replace("*", "") + ".png"), int(1.15 * self.size),
                                    int(1.15 * self.size), root, name)
            else:
                img = cv.load_image(os.path.join("assets", self.name.replace("*", "") + ".png"), int(1.15*self.size), int(1.15*self.size), root, name)
        except:
            print("No image for {}".format(self.name))
            img = None

        if not self.color:
            color = tuple((random.randint(min_color, max_color), random.randint(min_color, max_color), random.randint(min_color + 30, max_color)))
            self.color = cv._from_rgb(color)

            if colors:
                colors[name] = color
        else:
            self.color = cv._from_rgb(tuple(color))

        self.image_obj = img

        self.draw(target_y=target_y, width=width, img=img, value=value, color_data=color_data)

    def draw(self, target_y=0, width=0, img=None, value=0, color_data=None):
        self.last_width = width
        self.last_value = value

        if not isinstance(color_data, pd.core.series.Series):
            self.has_multi_color_data = False
            self.bar = self._round_rectangle(self.x, self.y + self.size*0.15, self.x + width, self.y + self.size*1.3, fill=self.color, width=0)
            # self.canvas.tag_lower(self.bar)
        else:
            self.has_multi_color_data = False
            for index in color_data.index:
                if self.name == index.split("_")[0]:
                    self.has_multi_color_data = True

            if self.has_multi_color_data:
                self.bars = []
                current_x = self.x
                for index in color_data.index:
                    if index.split("_")[0] == self.name:
                        color = cv._from_rgb(tuple(self.multi_colors[index.split("_")[-1]]))
                        self.bars.append(self.canvas.create_rectangle(current_x, self.y + self.size*0.15, current_x + width * color_data[index] / 100, self.y + self.size*1.3, fill=color, width=0))
                        current_x = current_x + width * color_data[index] / 100
            else:
                self.bar = self._round_rectangle(self.x, self.y + self.size * 0.15, self.x + width,
                                                 self.y + self.size * 1.3, fill=self.color, width=0)

        if img:
            self.img = self.canvas.create_image(self.x + width + 10, self.y + self.size*0.15, image=img, anchor="nw")
        else:
            self.img = None

        if self.display_value:
            if int(self.font_size * len(str(value)) / 1.5) < int(width):
                self.draw_in_bar = True
                self.frame_in_bar = 0
                self.frame_not_in_bar = 0
                self.value = self.canvas.create_text(self.x + width - self.size*0.25, target_y + (self.size)/3, text=str(self.money) + format(value, ",.{}f".format(self.decimal_places)) + str(self.unit), anchor="ne", font=self.font, fill=cv._from_rgb((255,255,255)))
            else:
                self.draw_in_bar = False
                self.frame_not_in_bar = 0
                self.frame_in_bar = 0
                if self.img:
                    self.value = self.canvas.create_text(self.x + width + 0.5 * self.size + self.image_obj.width(), self.y + (self.size) / 3,
                                                         text=str(self.money) + format(value, ",.{}f".format(
                                                             self.decimal_places)) + str(self.unit), anchor="nw", font=self.font,
                                                         fill=cv._from_rgb(self.font_color))
                else:
                    self.value = self.canvas.create_text(self.x + width + 0.25 * self.size, self.y + (self.size) / 3,
                                                         text=str(self.money) + format(value, ",.{}f".format(
                                                             self.decimal_places)) + str(self.unit), anchor="nw",
                                                         font=self.font,
                                                         fill=cv._from_rgb(self.font_color))

        self.text = self.canvas.create_text(self.x - 10, self.y + (self.size) / 3, text=self.name, anchor="ne",
                                            font=self.font, fill=cv._from_rgb(self.font_color))

    def _round_rectangle(self, x1, y1, x2, y2, **kwargs):

        if x2 - x1 < 1:
            radius = (x2 - x1) / 2
            x2 = x1 + 1
        elif x2 - x1 < self.radius*2:
            radius = (x2 - x1)/2
        else:
            radius = self.radius

        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def _update_round_rectangle(self, x1, y1, x2, y2, **kwargs):

        if x2 - x1 < 1:
            radius = (x2 - x1) / 2
            x2 = x1 + 1
        elif x2 - x1 < self.radius * 2:
            radius = (x2 - x1) / 2
        else:
            radius = self.radius

        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]

        self.canvas.coords(self.bar, points)

    def update(self, target_y=0, width=0, value=0, color_data=None):
        if value and self.bar:
            F = self.stiffness * (target_y - self.y) - self.damping * self.v
            self.a = F / self.mass
            self.v = self.v + self.a
            self.y = self.y + self.v

            self.last_frame = str(self.money) + format(value, ",.{}f".format(self.decimal_places)) + str(self.unit) + str(self.x + width + self.size*1.5)

            self.canvas.coords(self.text, self.x - 10, self.y + (self.size)/3 + (1 - self.font_scale) * self.size / 2)

            if self.display_value:
                # when the value should be drawn in the bar
                if self.canvas.bbox(self.value)[2] - self.canvas.bbox(self.value)[0] < 0.75 * width:
                    self.canvas.coords(self.value, self.x + width - self.size*0.25, self.y + (self.size)/3+ (1 - self.font_scale) * self.size / 2)
                    self.canvas.itemconfig(self.value, fill=cv._from_rgb((255, 255, 255)), anchor="ne")
                # when the value should be drawn outside of the bar
                else:
                    if self.img:
                        self.canvas.coords(self.value, self.x + width + 0.5 * self.size + self.image_obj.width(), self.y + (self.size) / 3+ (1 - self.font_scale) * self.size / 2)
                    else:
                        self.canvas.coords(self.value, self.x + width + 0.25 * self.size, self.y + (self.size) / 3+ (1 - self.font_scale) * self.size / 2)
                    self.canvas.itemconfig(self.value, fill=cv._from_rgb(self.font_color), anchor="nw")

                if not self.last_value == value:
                    self.canvas.itemconfig(self.value, text=str(self.money) + format(value, ",.{}f".format(self.decimal_places)) + str(self.unit))

            if abs(target_y - self.y) > 1 or not self.last_width == width:
                if not self.has_multi_color_data:
                    self._update_round_rectangle(self.x, self.y + self.size*0.15, self.x + width, self.y + self.size*1.3)
                else:
                    current_x = self.x
                    i = 0
                    for index in color_data.index:
                        if index.split("_")[0] == self.name:
                            self.canvas.coords(self.bars[i], current_x, self.y + self.size * 0.15, current_x + width * color_data[index] / 100, self.y + self.size * 1.3)
                            current_x = current_x + width * color_data[index] / 100
                            i = i + 1
            elif self.has_multi_color_data:
                current_x = self.x
                i = 0
                for index in color_data.index:
                    if index.split("_")[0] == self.name:
                        self.canvas.coords(self.bars[i], current_x, self.y + self.size * 0.15,
                                           current_x + width * color_data[index] / 100, self.y + self.size * 1.3)
                        current_x = current_x + width * color_data[index] / 100
                        i = i + 1

            self.last_width = width
            self.last_value = value

            if self.img:
                self.canvas.coords(self.img, self.x + width + 10, self.y + self.size*0.15)

        elif value and self.bar == None:
            self.draw(target_y=target_y, width=width, img=self.image_obj, value=value, color_data=None)

        elif value == 0:
            self.delete()

    def delete(self):
        if not self.value == None:
            self.canvas.delete(self.value)
            self.value = None
        if not self.text == None:
            self.canvas.delete(self.text)
            self.text = None
        if not self.img == None:
            self.canvas.delete(self.img)
            self.img = None
        if not self.bar == None:
            self.canvas.delete(self.bar)
            self.bar = None

class bar_stripes():

    def __init__(self, canvas, y_min, y_max, row, x, width, height, number_of_bars, invert, allow_decrease=True):
        self.N = 2
        self.color = cv._from_rgb((50, 50, 50))
        self.canvas = canvas
        self.number_of_bars = number_of_bars
        self.invert = invert

        self.allow_decrease = allow_decrease

        self.y_min = y_min
        self.y_max = y_max

        self.font = font.Font(family=text_font, size=int(height/60/SCALEFACTOR), weight="bold")

        self.width = width

        self.lines = {}
        self.lines["lines"] = []
        self.lines["text"] = []

        self.x = x

        self.draw(row)

    def draw(self, row):
        if self.invert:
            max = row.iloc[self.number_of_bars]
        else:
            max = row.max()

        self.current_max = max

        self.spacing = cv.truncate(max / self.N, 1 - len(str(int(cv.truncate(max / self.N, 0)))))

        for i in range(1, self.N * 2 + 1):
            value = i * self.spacing
            fraction = value / max
            x_pos = self.x + fraction * self.width

            if value > max:
                self.lines["lines"].append(
                    self.canvas.create_line(x_pos, self.y_min, x_pos, self.y_max, fill=""))
                self.lines["text"].append(self.canvas.create_text(x_pos, self.y_min, text="", fill="", anchor="s", font=self.font))
            else:
                self.lines["lines"].append(self.canvas.create_line(x_pos, self.y_min, x_pos, self.y_max, fill=self.color))
                self.lines["text"].append(self.canvas.create_text(x_pos, self.y_min, text=format(value, ",.{}f".format(decimal_places)), fill=self.color, anchor="s", font=self.font))

    def update(self, row):
        if self.invert:
            if row.iloc[self.number_of_bars] > self.current_max:
                self.current_max = row.iloc[self.number_of_bars]
            max = self.current_max
        else:
            if row.max() > self.current_max:
                self.current_max = row.max()

            max = self.current_max


        self.spacing = cv.calc_spacing(max, self.spacing, self.N)
        # self.spacing = 5

        for i in range(1, self.N * 2 + 1):
            value = i * self.spacing
            if max == 0:
                fraction = 0
            else:
                if self.allow_decrease:
                    fraction = value / row.max()
                else:
                    fraction = value / max
            x_pos = self.x + fraction * self.width

            if fraction > 1:
                self.canvas.itemconfig(self.lines["lines"][i-1], fill="")
                self.canvas.itemconfig(self.lines["text"][i-1], fill="")
            else:
                self.canvas.itemconfig(self.lines["lines"][i-1], fill=self.color)
                self.canvas.itemconfig(self.lines["text"][i-1], text=format(value, ",.{}f".format(decimal_places)), fill=self.color)

            self.canvas.coords(self.lines["lines"][i-1], x_pos, self.y_min, x_pos, self.y_max)
            self.canvas.coords(self.lines["text"][i-1], x_pos, self.y_min)

            # self.canvas.tag_lower(self.lines["lines"][i-1])
            # self.canvas.tag_lower(self.lines["text"][i-1])