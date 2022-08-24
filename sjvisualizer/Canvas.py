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

class canvas():
    """Canvas to which all the graphs will be drawn

    :param bg: Background color in RGB, defaults to (255, 255, 255) (white)
    :type bg: tuple of length 3 with integers"""
    def __init__(self, width=None, height=None, bg=(255, 255, 255), colors={}):
        """


        """
        self.tk = Tk()
        if not width:
            width = WIDTH
        else:
            width = width

        if not height:
            height = HEIGHT
        else:
            height = height

        self.canvas = Canvas(self.tk, width=width, height=height, bg=_from_rgb(bg))
        self.canvas.config(highlightthickness=0)
        self.tk.attributes("-fullscreen", True)

        self.colors = colors

        self.canvas.pack()

        self.width = width
        self.height = height

        self.sub_canvas = []

        if not os.path.isdir('assets'):
            os.mkdir('assets')

    def update(self, time):
        """
        Update function that gets called every frame of the animation.

        :param time: time object that corresponds to the frame
        :type time: datetime object
        """
        for sub in self.sub_canvas:
            sub.update(time)

        self.canvas.pack()
        self.tk.update()

    def add_sub_plot(self, sub_plot):
        """
        Function to add sub plots to this canvas

        :param sub_plot: sub_plot object
        :type sub_plot: sjvisualizer.Canvas.sub_plot
        """
        sub_plot.set_root(self.tk)
        self.sub_canvas.append(sub_plot)

    def set_decimals(self, decimals):
        global decimal_places
        decimal_places = decimals

    def play(self, df=None, fps=30):
        """
        Main loop of the animation. This function will orchestrate the animation for each time step set in the pandas df

        :param df: pandas data frame to be animated
        :type df: pandas.DataFrame

        :param fps: frame rate of the animation, defaults to 30 frames per second
        :type fps: int

        """
        if not df:
            for sub in self.sub_canvas:
                if not sub.df is None:
                    df = sub.df

        for i, date_time in enumerate(df.index):
            start = time.time()

            self.update(date_time)
            if i == 0:
                time.sleep(1)

            while time.time() - start < 1 / fps:
                pass

            time_used = time.time() - start
            print("FPS: {}".format(format(1/time_used, ",.{}f".format(decimal_places))))

    def add_title(self, text, color=(0, 0, 0)):
        """
        Helper function to add a title to your animation.

        :param text: title to be displayed at the top of the visualization
        :type text: str

        :param color: title color in RGB, defaults to (0, 0, 0) black
        :type color: tuple of length 3 with integers

        """
        title_font = font.Font(family=text_font, size=int(HEIGHT/30/ SCALEFACTOR), weight="bold")
        self.canvas.create_text(WIDTH/2, HEIGHT/20, font=title_font, text=text, fill=_from_rgb(color))

    def add_sub_title(self, text, color=(0, 0, 0)):
        """
        Helper function to add a sub title to your animation.

        :param text: sub title to be displayed at the top of the visualization
        :type text: str

        :param color: sub title color in RGB, defaults to (0, 0, 0) black
        :type color: tuple of length 3 with integers

        """
        title_font = font.Font(family=text_font, size=int(HEIGHT/45/ SCALEFACTOR), weight="bold")
        self.canvas.create_text(WIDTH/2, HEIGHT/11, font=title_font, text=text, fill=_from_rgb(color))

    def add_time(self, df, time_indicator="year", color=(150, 150, 150)):
        """
        Helper function to add a timestamp to the visualization

        :param df: pandas dataframe that holds the timestamps as the index
        :type df: pandas.DataFrame

        :param time_indicator: determine the format of the timestamp, possible values: "day", "month", "year", defaults to "year"
        :type time_indicator: str

        :param color: text color in RGB, defaults to (150, 150, 150)
        :type color: tuple of length 3 with integers
        """
        from sjvisualizer import Date
        sub_plot = Date.date(canvas=self.canvas, start_time=list(df.index)[0], width=0, height=HEIGHT/12,
                                       x_pos=WIDTH/10, y_pos=HEIGHT*0.85, time_indicator=time_indicator,
                                       font_color=color)
        self.add_sub_plot(sub_plot)

    def add_logo(self, logo):
        """
        Helper function to add a logo

        :param logo: image name of your logo, absolute or relative path
        :type str
        """
        from sjvisualizer import StaticImage
        img = StaticImage.static_image(canvas=self.canvas, width=int(WIDTH/15), height=int(WIDTH/15), x_pos=WIDTH*0.95,
                                           y_pos=HEIGHT*0.00,
                                           file=logo, root=self.tk, anchor="ne")
        self.add_sub_plot(img)

class sub_plot():
    """
    Basic sub_plot class from which all chart types are inherited

    :param canvas: tkinter canvas to draw the graph to
    :type canvas: tkinter.Canvas

    :param width: width of the plot in pixels
    :type width: int

    :param height: height of the plot in pixels
    :type height: int

    :param x_pos: the x location of the top left pixel in this plot
    :type x_pos: int

    :param y_pos: the y location of the top left pixel in this plot
    :type y_pos: int

    :param font_color: font color
    :type font_color: tuple of length 3 with integers
    """
    def __init__(self, canvas=None, width=None, height=None, x_pos=None, y_pos=None, start_time=None, text=None, df=None, multi_color_df=None, anchor="c", sort=True, colors={}, root=None, display_percentages=True, display_label=True, title=None, invert=False, origin="s", display_value=True, font_color=(0,0,0), back_ground_color=(255,255,255), events=[], time_indicator="year", number_of_bars=None, unit="", x_ticks = 4, y_ticks = 4, log_scale=False, only_show_latest_event=True, allow_decrease=True, format="Europe", draw_points=True, area=True, color_bar_color=[[100, 100, 100], [255, 0, 0]], **kwargs):
        """

        """
        if width == None:
            self.width = 0.65 * WIDTH
        else:
            self.width = width

        if height == None:
            self.height = 0.65 * HEIGHT
        else:
            self.height = height

        if not start_time and isinstance(df, pd.DataFrame):
            self.start_time = list(df.index)[0]
        else:
            self.start_time = start_time

        if not number_of_bars and isinstance(df, pd.DataFrame):
            if len(df.columns) < 10:
                self.number_of_bars = len(df.columns)
            else:
                self.number_of_bars = 10
        else:
            self.number_of_bars = number_of_bars

        self.time_indicator = time_indicator

        if hasattr(self, "decimal_places"):
            self.decimal_places = decimal_places
        else:
            self.decimal_places = decimal_places

        self.allow_decrease = allow_decrease

        self.canvas = canvas
        self.colors = colors
        self.root = root
        self.invert = invert
        self.origin = origin

        self.format = format

        self.area = area

        self.events = events

        self.back_ground_color = back_ground_color

        self.only_show_latest_event = only_show_latest_event

        self.font_color = font_color

        self.display_label = display_label
        self.display_percentages = display_percentages

        if x_pos == None:
            self.x_pos = 0.175 * WIDTH
        else:
            self.x_pos = x_pos

        if y_pos == None:
            self.y_pos = 0.175 * HEIGHT
        else:
            self.y_pos = y_pos

        self.text = text
        self.df = df
        self.multi_color_df = multi_color_df

        self.anchor = anchor

        self.display_value = display_value

        self.sort = sort

        self.unit = unit

        self.__dict__.update(kwargs)

        self.x_ticks = x_ticks
        self.y_ticks = y_ticks

        self.log_scale = log_scale

        self.draw_points = draw_points

        self.color_bar_color = color_bar_color

        if title:
            self.canvas.create_text(x_pos + width/2, y_pos - height/18, anchor = "s", text=title, font=font.Font(family=text_font, size=int(15 + self.height/60/ SCALEFACTOR), weight="bold"), fill=_from_rgb(self.font_color))

        if self.root:
            self.draw(self.start_time)

    def set_root(self, root):
        if not self.root:
            self.root = root
            self.draw(self.start_time)

    def save_colors(self):
        with open("colors/colors.json", "w") as file:
            json.dump(self.colors, file, indent=4)

    def update(self, time):
        pass

    def load_image(self):
        pass

    def _get_data_for_frame(self, time, df=None):
        if not isinstance(df, pd.DataFrame):
            df = self.df
        return df.loc[time]


def format_date(time, time_indicator):
    if time_indicator == "year":
        return str(time.year)
    elif time_indicator == "month":
        return str("{} {}".format(months[time.month], time.year))
    elif time_indicator == "day":
        return str("{} {} {}".format(time.day, months[time.month], time.year))
    return None

def _from_rgb(rgb):
    rgb = list(rgb)
    for i, c in enumerate(rgb):
        if c < 0:
            rgb[i] = 0
    return "#%02x%02x%02x" % tuple(rgb)

def truncate(n, decimals=1):
    # decimals = len(str(n))
    multiplier = 10 ** decimals
    if not math.isnan(n):
        return round(n * multiplier) / multiplier
    else:
        return 0

def calc_spacing(value, current_spacing, n):
    if current_spacing * 4 < value:
        current_spacing = round(current_spacing * 2, -len(str(round(value)))+1)
    if not current_spacing:
        current_spacing = 1
    return current_spacing

def load_image(path, x, y, root, name):
    load = Image.open(path)
    load = load.resize((int(x * load.size[0]/load.size[1]), int(y)), resample=2)
    load = ImageTk.PhotoImage(load)
    i = 0
    while hasattr(root, name + str(i)):
        i = i + 1
    setattr(root, name + str(i), load)
    return load

def format_date(time, time_indicator, format="Europe"):
    # format date
    if time_indicator == "year":
        text = str(time.year)
    elif time_indicator == "month":
        text = str("{} {}".format(months[time.month], time.year))
    elif time_indicator == "day":
        if format == "USA":
            text = str("{} {} {}".format(months[time.month], time.day, time.year))
        else:
            text = str("{} {} {}".format(time.day, months[time.month], time.year))

    return text

def hex_to_rgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))