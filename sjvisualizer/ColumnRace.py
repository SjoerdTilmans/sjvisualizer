from sjvisualizer import Canvas as cv
from sjvisualizer import ColumnAxis
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

# Configurable image outside position and size adjustments
IMAGE_X_OFFSET = 39  # Shift image left/right
IMAGE_Y_OFFSET = -180  # Shift image up/down
IMAGE_SIZE_SCALE = 0.75  # Scale image size

# Configurable image inside position and size adjustments
IMAGE_INSIDE_SIZE_SCALE = 0.55  # Scale image size

class column_race(cv.sub_plot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns = {}
        self.internal_images = {}
        self.unit = kwargs.get('unit', ("", ""))
        self.number_of_columns = kwargs.get('number_of_columns', 4)
        self.decimal_places = kwargs.get('decimal_places', 2)
        self.font_color = kwargs.get('font_color', (0, 0, 0))
        self.colors = kwargs.get('colors', {})
        self.column_positions = []

    def draw(self, time):
        self.columns = {}
        self.internal_images = {}

        # Sort data in descending order and take top N columns
        data = self._get_data_for_frame(time).sort_values(ascending=False).head(self.number_of_columns)

        self.distance = self.width / (self.number_of_columns + (self.number_of_columns - 0.7) * 0.5)
        # Calculate positions based on sorted order
        self.column_positions = [self.x_pos + (i * self.distance * 1.06) + (self.distance / 2) - 20
                                 for i in range(self.number_of_columns)]

        # Use absolute values for scaling to handle negatives
        self.max_value = max(abs(data.max()), abs(data.min()), 1)
        self.axis_color = (0, 0, 0)
        self.font_size = self.height / 33

        self.y_axis = ColumnAxis.axis(
            canvas=self.canvas,
            n=5,
            orientation="vertical",
            x=self.x_pos,
            y=self.y_pos + self.height + 0.5,
            length=self.height,
            allow_decrease=False,
            is_date=False,
            font_size=self.font_size - 1,
            color=self.axis_color,
            ticks_only=False,
            unit=("$", ""),
            show_gridlines=True,
            gridline_color=(100, 100, 100),
            gridline_opacity=0.5
        )
        self.y_axis.draw(min=0, max=self.max_value)

        self.x_axis = ColumnAxis.axis(
            canvas=self.canvas,
            n=self.number_of_columns,
            orientation="horizontal",
            x=self.x_pos,
            y=self.y_pos + self.height + 0.5,
            length=self.width,
            allow_decrease=False,
            is_date=False,
            font_size=self.font_size,
            color=self.axis_color,
            ticks_only=False
        )
        self.x_axis.draw(min=0, max=self.number_of_columns + self.distance / self.width)

        self._draw_columns(data, self.max_value)

    def update(self, time):
        # Sort data in descending order and take top N columns
        data = self._get_data_for_frame(time).sort_values(ascending=False).head(self.number_of_columns)
        self.max_value = max(abs(data.max()), abs(data.min()), 1)
        self.y_axis.update(min=0, max=self.max_value)
        self._draw_columns(data, self.max_value)

    def _draw_columns(self, data, max_value):
        updated_names = set()

        # Iterate through sorted data
        for i, (name, value) in enumerate(data.items()):
            if pd.isna(value):
                continue

            fraction = abs(value) / max_value
            is_negative = value < 0
            target_height = fraction * self.height
            updated_names.add(name)

            # Get position based on sorted order
            fixed_x = self.column_positions[i] if i < len(self.column_positions) else self.column_positions[-1]

            if name in self.columns:
                self.columns[name].update(
                    target_x=fixed_x,
                    target_height=target_height,
                    value=value,
                    is_negative=is_negative
                )
                self._update_internal_image_position(name, fixed_x, target_height, is_negative)
            else:
                color = (255, 0, 0) if is_negative else self.colors.get(name)
                self.columns[name] = column(
                    name=name,
                    canvas=self.canvas,
                    x=fixed_x,
                    target_height=target_height,
                    color=color,
                    width=self.distance * 0.60,
                    value=value,
                    unit=self.unit,
                    font_color=self.font_color,
                    base_y=self.y_axis.y + 1.5,
                    root=self.root,
                    decimal_places=self.decimal_places,
                    is_negative=is_negative,
                    original_color=self.colors.get(name)
                )
                self._add_image_inside_column(name, fixed_x, target_height, is_negative)

        # Remove columns that are no longer in the top N
        for name in list(self.columns.keys()):
            if name not in updated_names:
                self.columns[name].delete()
                if name in self.internal_images:
                    self.canvas.delete(self.internal_images[name])
                    del self.internal_images[name]
                del self.columns[name]

    def _add_image_inside_column(self, name, x_pos, height, is_negative):
        try:
            img_path = os.path.join("asset1", name.replace("*", "") + ".png")
            img = cv.load_image(img_path, int(self.distance * 0.50), int(self.distance * 0.50), self.root, name)
            y_pos = self.y_axis.y - height / 2 if not is_negative else self.y_axis.y + height / 2
            self.internal_images[name] = self.canvas.create_image(
                x_pos + self.distance * 0.25,
                y_pos,
                image=img,
                anchor="center"
            )
        except Exception as e:
            print(f"No internal image for {name}: {e}")

    def _update_internal_image_position(self, name, x_pos, height, is_negative):
        if name in self.internal_images:
            y_pos = self.y_axis.y - height / 2 if not is_negative else self.y_axis.y + height / 2
            self.canvas.coords(
                self.internal_images[name],
                x_pos + 6.9 + self.distance * 0.25,
                y_pos
            )


class column():
    def __init__(self, name=None, canvas=None, x=0, target_height=0, color=None, width=50, value=0, size=40, unit=None,
                 font_color=(0, 0, 0), base_y=0, decimal_places=None, font_scale=1, root=None, is_negative=False, original_color=None):
        self.name = name
        self.canvas = canvas
        self.root = root
        self.font_scale = font_scale
        self.font_size = int(size / 2 / SCALEFACTOR * font_scale)
        self.font = font.Font(family=text_font, size=self.font_size, weight="bold")
        self.font2 = font.Font(family="Microsoft JhengHei UI", size=self.font_size - 2, weight="bold")
        self.font3 = font.Font(family="Segoe UI", size=self.font_size + 3, weight="bold")

        self.decimal_places = decimal_places
        self.x = x
        self.target_x = x
        self.target_height = target_height
        self.current_height = 0
        self.value = value
        self.is_negative = is_negative
        self.original_color = original_color or (random.randint(20, 225), random.randint(20, 225), random.randint(50, 225))

        if unit is None:
            self.unit = ("", "")
        elif isinstance(unit, str):
            self.unit = ("", unit)
        elif isinstance(unit, (tuple, list)) and len(unit) == 2:
            self.unit = tuple(unit)
        else:
            self.unit = ("", str(unit))

        self.width = width
        self.font_color = font_color
        self.base_y = base_y - 2
        self.image_above = None
        self.image_id = None

        self.color = cv._from_rgb((255, 0, 0) if self.is_negative else self.original_color)

        self._load_image_above_column()
        self.draw(value)

    def _load_image_above_column(self):
        try:
            img_path = os.path.join("assets", self.name.replace("*", "") + ".png")
            self.image_above = cv.load_image(
                img_path,
                int(self.width * 1.1),
                int(self.width * 1.0),
                self.root,
                self.name
            )
        except Exception as e:
            print(f"No image for {self.name}: {e}")
            self.image_above = None

    def draw(self, value=0):
        top_y = self.base_y - self.current_height if not self.is_negative else self.base_y + self.current_height

        self.rect = self.canvas.create_rectangle(
            self.x, self.base_y,
            self.x + self.width,
            top_y,
            fill=self.color,
            width=0
        )

        if self.image_above:
            y_pos = top_y - 10 if not self.is_negative else top_y + 10
            self.image_id = self.canvas.create_image(
                self.x + self.width / 2, y_pos,
                image=self.image_above,
                anchor="s" if not self.is_negative else "n"
            )

        value_y = top_y - 10 if not self.is_negative else top_y + 10
        self.value_text = self.canvas.create_text(
            self.x + self.width / 2,
            value_y,
            text=f"{self.unit[0]}{value:,.{self.decimal_places}f}{self.unit[1]}",
            anchor="s" if not self.is_negative else "n",
            font=self.font3,
            fill=cv._from_rgb(self.font_color)
        )

        display_name = self.name.replace(" ", "")
        self.name_text = self.canvas.create_text(
            self.x + self.width / 2,
            self.base_y + 60,
            text=display_name,
            anchor="n",
            justify="center",
            font=self.font2,
            fill=cv._from_rgb(self.font_color))

    def update(self, target_x, target_height, value, is_negative):
        self.current_height += (target_height - self.current_height) * 0.1
        self.x += (target_x - self.x) * 0.1

        if is_negative != self.is_negative:
            self.is_negative = is_negative
            color = (255, 0, 0) if self.is_negative else self.original_color
            self.color = cv._from_rgb(color)
            self.canvas.itemconfig(self.rect, fill=self.color)

        top_y = self.base_y - self.current_height if not self.is_negative else self.base_y + self.current_height

        self.canvas.coords(
            self.rect,
            self.x, self.base_y,
            self.x + self.width,
            top_y
        )

        if self.image_id:
            y_pos = top_y + 3 if not self.is_negative else top_y + 10
            self.canvas.coords(
                self.image_id,
                self.x + self.width / 2,
                y_pos
            )

        value_y = top_y - 95 if not self.is_negative else top_y + 95
        self.canvas.itemconfig(
            self.value_text,
            text=f"{self.unit[0]}{value:,.{self.decimal_places}f}{self.unit[1]}",
            anchor="s" if not self.is_negative else "n"
        )
        self.canvas.coords(
            self.value_text,
            self.x + self.width / 2,
            value_y
        )

        display_name = self.name.replace(" ", " ")
        self.canvas.itemconfig(self.name_text, text=display_name)
        self.canvas.coords(
            self.name_text,
            self.x + self.width / 2,
            self.base_y + 13
        )

    def delete(self):
        self.canvas.delete(self.rect)
        self.canvas.delete(self.value_text)
        if self.image_id:
            self.canvas.delete(self.image_id)

if __name__ == "__main__":
    from sjvisualizer import Canvas, DataHandler

    df = DataHandler.DataHandler(excel_file="data/DynamicMatrix.xlsx", number_of_frames=60*10).df

    canvas = Canvas.canvas()

    empty_chart = column_race(canvas=canvas, font_size=25, df=df, neutral_string="Neutral", level_count=3)
    canvas.add_sub_plot(empty_chart)

    canvas.add_time(df=df, time_indicator="day")
    canvas.add_title("Dynamic Matrix")

    canvas.play(fps=60)