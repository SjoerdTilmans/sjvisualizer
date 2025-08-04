from tkinter import *
import tkinter
import sjvisualizer
from PIL import Image, ImageGrab
# import pyautogui
# from mss import mss
import numpy as np
import cv2
import time
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

color_palette = [
    (31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40), (148, 103, 189),
    (140, 86, 75), (227, 119, 194), (127, 127, 127), (188, 189, 34), (23, 190, 207),
    (188, 18, 86), (206, 162, 98), (139, 85, 35), (204, 121, 167), (75, 75, 75),
    (102, 194, 165), (210, 245, 60), (77, 172, 38), (196, 58, 250), (141, 68, 172),
    (255, 166, 254), (241, 167, 254), (69, 177, 58), (177, 69, 124), (91, 69, 177),
    (168, 113, 170), (44, 227, 219), (94, 95, 67), (164, 131, 22), (78, 43, 15),
    (229, 114, 12), (78, 15, 98), (152, 61, 98), (250, 190, 190), (38, 252, 79),
    (208, 97, 71), (229, 82, 49), (78, 147, 58), (107, 15, 98), (221, 119, 207),
    (115, 75, 177), (82, 22, 228), (65, 59, 83), (132, 172, 91), (119, 77, 52),
    (154, 187, 252), (207, 148, 64), (178, 250, 168), (141, 196, 133), (250, 215, 160),
    (229, 81, 69), (119, 215, 246), (162, 38, 98), (205, 215, 169), (98, 162, 125),
    (106, 207, 89), (248, 86, 169), (249, 79, 133), (240, 224, 89), (105, 222, 99),
    (248, 249, 48), (50, 148, 66), (229, 81, 201), (162, 132, 76), (121, 129, 65),
    (229, 111, 111), (189, 100, 179), (79, 114, 129), (209, 63, 42), (129, 41, 159),
    (129, 92, 41), (158, 116, 45), (55, 162, 192), (79, 141, 76), (110, 129, 59),
    (114, 79, 159), (159, 41, 68), (179, 127, 94), (63, 92, 40), (255, 89, 71),
    (41, 197, 149), (41, 159, 151), (100, 118, 121), (179, 79, 141), (69, 116, 161),
    (208, 73, 152), (209, 191, 66), (189, 130, 61), (161, 60, 60), (60, 104, 173),
    (200, 57, 49), (179, 169, 53), (78, 73, 58), (166, 58, 250), (122, 122, 121),
    (61, 116, 79), (48, 77, 52), (133, 163, 125), (132, 173, 144), (165, 100, 99),
    (189, 102, 185), (174, 60, 60), (99, 138, 159), (117, 102, 129), (164, 127, 39),
    (56, 83, 119), (138, 60, 60), (124, 127, 53), (114, 133, 59), (60, 138, 60),
    (152, 84, 152), (93, 138, 60), (84, 82, 63)
]

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
FRAMES_PER_VIDEO_WRITE = 10

monitor = get_monitors()[0]
HEIGHT = monitor.height
WIDTH = monitor.width

class canvas():
    """Canvas to which all the graphs will be drawn

    :param bg: Background color in RGB, defaults to (255, 255, 255) (white)
    :type bg: tuple of length 3 with integers

    :param include_logo: Should the "Made with SJVisualizer" logo be included?, defaults to True
    :type include_logo: bool
    """
    def __init__(self, width=None, height=None, bg=(255, 255, 255), colors={}, include_logo=True):
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

        self.color_palette = color_palette

        self.canvas = Canvas(self.tk, width=width, height=height, bg=_from_rgb(bg))
        self.canvas.config(highlightthickness=0)
        self.tk.attributes("-fullscreen", True)

        self.include_logo = include_logo

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

    def play(self, df=None, fps=30, record=False, width=WIDTH, height=HEIGHT, file_name="output.mp4"):
        """
        Main loop of the animation. This function will orchestrate the animation for each time step set in the pandas df

        :param df: pandas data frame to be animated
        :type df: pandas.DataFrame

        :param fps: frame rate of the animation, defaults to 30 frames per second
        :type fps: int

        :param record: if set to True, the screen will be recorded, this will severely impact performance on high resolution screens
        :type record: boolean

        :param width: if record is set to True, this is the width of the window being recorded. Defaults to full screen.
        :type width: int

        :param height: if record is set to True, this is the height of the window being recorded. Defaults to full screen.
        :type height: int

        :param file_name: if record is set to True, this is the name of the output file. Defaults to output.mp4.
        :type file_name: str

        """
        if not df:
            for sub in self.sub_canvas:
                if not sub.df is None:
                    df = sub.df
                elif hasattr(self, "df_x") and not sub.df_x is None:
                    df = sub.df_x
                elif hasattr(self, "df_y") and not sub.df_y is None:
                    df = sub.df_y

        # prepare empty list to store animation frames
        if record:
            self.frames = []
            fourc = cv2.VideoWriter_fourcc(*"mp4v")
            capture_video = cv2.VideoWriter(file_name, fourc, fps, (width, height))

        if self.include_logo:
            self._add_sj_logo()

        # main loop of the animation
        for i, date_time in enumerate(df.index):
            start = time.time()
            self.update(date_time)
            if i == 0:
                time.sleep(1)

            # grab a screenshot for each of the frames
            if record and i > 1:
                img = ImageGrab.grab(bbox=(0, 0, width, height))

                self.frames.append(img)

                if len(self.frames) > FRAMES_PER_VIDEO_WRITE:
                    for f in self.frames:
                        img_np = np.array(f)
                        img_final = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                        capture_video.write(img_final)
                    self.frames = []

            while time.time() - start < 1 / fps:
                time.sleep(0.0001)

            time_used = time.time() - start
            print("FPS: {}".format(format(1/time_used, ",.{}f".format(decimal_places))))

        if record:
            time.sleep(1)
            self.tk.destroy()
            cv2.destroyAllWindows()

    def add_title(self, text, color=(0, 0, 0)):
        """
        Helper function to add a title to your animation.

        :param text: title to be displayed at the top of the visualization
        :type text: str

        :param color: title color in RGB, defaults to (0, 0, 0) black
        :type color: tuple of length 3 with integers

        """
        title_font = font.Font(family=text_font, size=int(self.height/30/ SCALEFACTOR), weight="bold")
        self.canvas.create_text(self.width/2, self.height/20, font=title_font, text=text, fill=_from_rgb(color))

    def add_sub_title(self, text, color=(0, 0, 0)):
        """
        Helper function to add a sub title to your animation.

        :param text: sub title to be displayed at the top of the visualization
        :type text: str

        :param color: sub title color in RGB, defaults to (0, 0, 0) black
        :type color: tuple of length 3 with integers

        """
        title_font = font.Font(family=text_font, size=int(self.height/45/ SCALEFACTOR))
        self.canvas.create_text(self.width/2, self.height/11, font=title_font, text=text, fill=_from_rgb(color))

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
        sub_plot = Date.date(canvas=self.canvas, start_time=list(df.index)[0], width=0, height=self.height/12,
                                       x_pos=self.width/20, y_pos=self.height*0.9, time_indicator=time_indicator,
                                       font_color=color, anchor="w")
        self.add_sub_plot(sub_plot)

    def add_logo(self, logo):
        """
        Helper function to add a logo

        :param logo: image name of your logo, absolute or relative path
        :type str
        """
        from sjvisualizer import StaticImage
        img = StaticImage.static_image(canvas=self.canvas, width=int(self.width/15), height=int(self.width/15), x_pos=self.width*0.95,
                                           y_pos=self.height*0.00,
                                           file=logo, root=self.tk, anchor="ne")
        self.add_sub_plot(img)

    def _add_sj_logo(self):
        from sjvisualizer import StaticImage
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Made with SJvisualzer.png")
        img = StaticImage.static_image(canvas=self.canvas, width=int(self.width / 45), height=int(self.width / 45),
                                       x_pos=self.width * 0.95,
                                       y_pos=self.height * 0.95,
                                       file=path, root=self.tk, anchor="se")
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
    def __init__(self, canvas=None, width=None, height=None, x_pos=None, y_pos=None, start_time=None, text=None, df=None, multi_color_df=None, anchor="c", sort=True, colors={}, root=None, display_percentages=True, display_label=True, title=None, invert=False, origin="s", display_value=True, font_color=(0,0,0), back_ground_color=(255,255,255), events={}, time_indicator="year", number_of_bars=None, unit="", x_ticks = 4, y_ticks = 4, log_scale=False, only_show_latest_event=True, allow_decrease=True, format="Europe", draw_points=True, area=True, font_size=25, color_bar_color=[[100, 100, 100], [255, 0, 0]], text_font="Microsoft JhengHei UI", **kwargs):
        """

        """
        self.__dict__.update(kwargs)
        if width == None:
            self.width = 0.65 * WIDTH
        else:
            self.width = width

        if not isinstance(df, pd.DataFrame):
            if hasattr(self, "df_x"):
                df = self.df_x
            elif hasattr(self, "df_y"):
                df = self.df_y

        if height == None:
            self.height = 0.65 * HEIGHT
            self.height_is_set = False
        else:
            self.height_is_set = True
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

        if not hasattr(self, "decimal_places"):
            self.decimal_places = decimal_places

        self.allow_decrease = allow_decrease


        if isinstance(canvas, tkinter.Canvas):
            self.canvas = canvas
            self.sjcanvas = None
        elif isinstance(canvas, sjvisualizer.Canvas.canvas):
            self.canvas = canvas.canvas
            self.sjcanvas = canvas
        else:
            raise "Please set the canvas to a tkinter.Canvas or sjvisualizer.Canvas"
        self.colors = colors
        self.root = root
        self.invert = invert
        self.origin = origin
        self.font_size = font_size
        self.text_font = text_font

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

def format_value(number, decimal=0):
    units = ['k', 'm', 'b', 't']
    unit_index = 0

    while abs(number) >= 1000 and unit_index < len(units):
        number /= 1000.0
        unit_index += 1

    formatted_number = "{:.{}f}".format(number, decimal).rstrip('.')

    # formatted_number = formatted_number.rstrip('0')

    if formatted_number.endswith('.'):
        formatted_number = formatted_number[:-1]

    if unit_index > 0:
        formatted_number += units[unit_index - 1]

    return formatted_number

def hex_to_rgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
