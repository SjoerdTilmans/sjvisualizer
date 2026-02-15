"""Axis component used by multiple charts."""

from __future__ import annotations

import datetime
import math
from tkinter import font

from ..utils.colors import from_rgb
from ..utils.format import format_date, format_value


months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


class axis:
    """Numeric or date axis with ticks and labels.

    The :class:`axis` class is a reusable component used by multiple charts to
    map values to pixel positions and to render tick marks + tick labels.

    It supports:
    - horizontal/vertical orientation
    - optional sticky min/max behaviour (useful for animations)
    - linear and log scales
    - numeric and date (datetime) axes

    Parameters are passed via ``__init__`` and most charts call :meth:`draw`
    once and :meth:`update` every frame.
    """

    def __init__(
        self,
        canvas,
        x=0,
        y=0,
        length=1000,
        width=1000,
        orientation="horizontal",
        n=3,
        allow_decrease=False,
        tick_length=0,
        is_log_scale=False,
        is_date=False,
        color=(50, 50, 50),
        font_size=20,
        text_font="Microsoft JhengHei UI",
        time_indicator="year",
        line_tickness=3,
        ticks_only=True,
        unit="",
        tick_prefix="",
        anchor="s",
        decimal_places=0,
        zero_based=False,
        sticky_min=None,
        sticky_max=None,
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.orientation = orientation
        self.n = n
        self.allow_decrease = allow_decrease
        self.is_log_scale = is_log_scale
        self.is_date = is_date
        self.color = color
        self.font_size = font_size
        self.text_font = text_font
        self.time_indicator = time_indicator
        self.line_tickness = line_tickness
        self.ticks_only = ticks_only
        self.unit = unit
        self.tick_prefix = tick_prefix
        self.anchor = anchor
        self.decimal_places = decimal_places

        self.zero_based = bool(zero_based)

        if sticky_min is None:
            sticky_min = (not allow_decrease)
        if sticky_max is None:
            sticky_max = (not allow_decrease)

        self.sticky_min = bool(sticky_min)
        self.sticky_max = bool(sticky_max)

        self.min_val = None
        self.max_val = None

        self.ticks = []
        self._ensure_tick_capacity(self.n * 3, tick_length)

        self._axis_line_id = None

    def _ensure_tick_capacity(self, needed: int, tick_length: int):
        while len(self.ticks) < needed:
            self.ticks.append(
                tick(
                    self.canvas,
                    axis=self,
                    length=tick_length,
                    tick_prefix=self.tick_prefix,
                    label_pos=self.anchor,
                )
            )

    def _coerce_legacy_minmax_kwargs(self, min_val, max_val, kwargs):
        if "min" in kwargs:
            min_val = kwargs["min"]
        if "max" in kwargs:
            max_val = kwargs["max"]
        return min_val, max_val

    def _update_limits(self, incoming_min, incoming_max):
        if self.min_val is None or self.max_val is None:
            self.min_val = incoming_min
            self.max_val = incoming_max
        else:
            self.min_val = builtins_min(self.min_val, incoming_min) if self.sticky_min else incoming_min
            self.max_val = builtins_max(self.max_val, incoming_max) if self.sticky_max else incoming_max

        if self.zero_based and incoming_min >= 0:
            self.min_val = 0

    def draw(self, min_val=0, max_val=0, **kwargs):
        min_val, max_val = self._coerce_legacy_minmax_kwargs(min_val, max_val, kwargs)
        self._update_limits(min_val, max_val)

        if not self.ticks_only:
            if self.orientation == "horizontal":
                self._axis_line_id = self.canvas.create_line(
                    self.x,
                    self.y,
                    self.x + self.length,
                    self.y,
                    fill=from_rgb(self.color),
                    width=self.line_tickness,
                )
            elif self.orientation == "vertical":
                self._axis_line_id = self.canvas.create_line(
                    self.x,
                    self.y,
                    self.x,
                    self.y - self.length,
                    fill=from_rgb(self.color),
                    width=self.line_tickness,
                )

        for t in self.ticks:
            t.draw(value=0)

        self.update(min_val=min_val, max_val=max_val)

    def update(self, min_val=0, max_val=0, **kwargs):
        min_val, max_val = self._coerce_legacy_minmax_kwargs(min_val, max_val, kwargs)
        self._update_limits(min_val, max_val)

        if not self.is_date:
            tick_values = calculate_nice_ticks(self.min_val, self.max_val, self.n, is_log_scale=self.is_log_scale)
            self._ensure_tick_capacity(builtins_max(self.n * 3, len(tick_values)), tick_length=0)

            last_used = -1
            for i, v in enumerate(tick_values):
                if i >= len(self.ticks):
                    break

                if v < self.min_val or v > self.max_val:
                    self.ticks[i].update(value=1, draw=False)
                    continue

                if abs(v) < 0.00001:
                    v = 0

                if v == 0:
                    self.ticks[i].update(value=v, draw=True, l=self.width)
                else:
                    self.ticks[i].update(value=v, draw=True)

                last_used = i

            for j in range(last_used + 1, len(self.ticks)):
                self.ticks[j].update(value=1, draw=False)

        else:
            min_days = (min_val - datetime.datetime(1800, 1, 1)).days
            max_days = (max_val - datetime.datetime(1800, 1, 1)).days

            if min_days == max_days:
                for t in self.ticks:
                    t.update(value=1, draw=False)
                return

            if self.time_indicator in ("year", "month"):
                tick_values = calculate_nice_ticks(
                    min_days,
                    max_days,
                    self.n,
                    is_log_scale=self.is_log_scale,
                    time_indicator=self.time_indicator,
                )
            else:
                tick_values = calculate_nice_ticks(min_days, max_days, self.n, is_log_scale=self.is_log_scale)

            spacing = tick_values[1] - tick_values[0] if len(tick_values) > 1 else 0
            number_of_ticks = len(tick_values)

            tick_values = [min_days]
            for _ in range(number_of_ticks):
                tick_values.append(tick_values[-1] + spacing)

            self._ensure_tick_capacity(builtins_max(self.n * 3, len(tick_values)), tick_length=0)

            last_used = -1
            for i, v in enumerate(tick_values):
                if i >= len(self.ticks):
                    break
                if min_days < v < max_days:
                    self.ticks[i].update(value=v, draw=True)
                    last_used = i
                else:
                    self.ticks[i].update(value=1, draw=False)

            for j in range(last_used + 1, len(self.ticks)):
                self.ticks[j].update(value=1, draw=False)

    def calc_positions(self, value):
        if self.min_val == 0 and self.max_val == 0:
            self.max_val = 0.1

        if not self.is_date:
            if not self.is_log_scale:
                denom = (self.max_val - self.min_val) or 1e-12
                return self.length * (value - self.min_val) / denom

            v = builtins_max(float(value), 1e-12)
            mn = builtins_max(float(self.min_val), 1e-12)
            mx = builtins_max(float(self.max_val), mn * 10)

            return self.length * math.log10(v / mn) / (math.log10(mx / mn) or 1e-12)

        min_days = (self._as_date(self.min_val) - datetime.datetime(1800, 1, 1)).days
        max_days = (self._as_date(self.max_val) - datetime.datetime(1800, 1, 1)).days
        val_days = value
        return self.length * (val_days - min_days) / ((max_days - min_days) or 1e-12)

    @staticmethod
    def _as_date(v):
        return v if isinstance(v, datetime.datetime) else datetime.datetime.fromtimestamp(v)


class tick:
    """A single tick mark + label on an :class:`axis`.

    Instances are created and reused by :class:`axis` to avoid recreating Tk
    canvas primitives each frame.
    """

    def __init__(self, canvas, axis=None, length=0, label_pos="s", tick_prefix=""):
        self.canvas = canvas
        self.axis = axis
        self.length = length
        self.label_pos = label_pos
        self.tick_prefix = tick_prefix
        self.font = font.Font(family=self.axis.text_font, size=int(self.axis.font_size))

    def draw(self, value=0):
        self.line = self.canvas.create_line(-1, -1, -1, -1, fill=from_rgb(self.axis.color), width=self.axis.line_tickness)
        self.text = self.canvas.create_text(-1, -1, text="", anchor="n", fill=from_rgb(self.axis.color), font=self.font)

    def update(self, value=0, draw=True, l=0):
        pos = self.axis.calc_positions(value)

        if draw:
            if self.axis.is_date:
                t = datetime.datetime(1800, 1, 1) + datetime.timedelta(days=value)
                label = format_date(t, self.axis.time_indicator)
            else:
                label = format_value(value, decimal=self.axis.decimal_places)

            if self.axis.orientation == "horizontal":
                if self.label_pos == "s":
                    self.canvas.coords(self.line, self.axis.x + pos, self.axis.y - self.length - l, self.axis.x + pos, self.axis.y + 10)
                elif self.label_pos == "n":
                    self.canvas.coords(self.line, self.axis.x + pos, self.axis.y, self.axis.x + pos, self.axis.y + 10 + l)
                else:
                    self.canvas.coords(self.line, self.axis.x + pos, self.axis.y - self.length - l, self.axis.x + pos, self.axis.y + 10)

                self.canvas.itemconfig(self.text, text=self.tick_prefix + label + self.axis.unit)

                if self.label_pos == "s":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y + 11)
                elif self.label_pos == "n":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y - self.length - 1)
                    self.canvas.itemconfig(self.text, anchor="s")

            elif self.axis.orientation == "vertical":
                if l:
                    self.canvas.coords(self.line, self.axis.x - 10, self.axis.y - pos, self.axis.x + self.length + l, self.axis.y - pos)
                else:
                    self.canvas.coords(self.line, self.axis.x - 10, self.axis.y - pos, self.axis.x + self.length, self.axis.y - pos)

                self.canvas.itemconfig(self.text, text=self.tick_prefix + label + self.axis.unit)

                if self.label_pos in ("s", "w"):
                    self.canvas.coords(self.text, self.axis.x - 15, self.axis.y - pos)
                    self.canvas.itemconfig(self.text, anchor="e")
                elif self.label_pos == "e":
                    self.canvas.coords(self.text, self.axis.x + self.length + 1, self.axis.y - pos)
                    self.canvas.itemconfig(self.text, anchor="w")

            self.canvas.tag_raise(self.line)

        else:
            self.canvas.coords(self.line, -1, -1, -1, -1)
            self.canvas.itemconfig(self.text, text="")


def calculate_nice_ticks(min_val, max_val, num_ticks, is_log_scale=False, time_indicator=False):
    if is_log_scale:
        min_val = builtins_max(float(min_val), 1e-12)
        max_val = builtins_max(float(max_val), min_val * 10)

    if not time_indicator:
        if is_log_scale:
            min_val = math.log10(min_val)
            max_val = math.log10(max_val)

        if min_val == max_val:
            max_val = min_val + 0.1

        rough_range = max_val - min_val
        rough_tick_incr = rough_range / num_ticks if num_ticks else rough_range
        if rough_tick_incr == 0:
            rough_tick_incr = 0.1

        exponent = math.floor(math.log10(abs(rough_tick_incr)))
        nice_tick_incr = 10 ** exponent

        ratio = abs(rough_tick_incr) / nice_tick_incr
        if ratio < 1.5:
            nice_tick_incr *= 1
        elif ratio < 3:
            nice_tick_incr *= 2
        else:
            nice_tick_incr *= 5

        nice_min_val = nice_tick_incr * math.floor(min_val / nice_tick_incr)
        needed = math.ceil((max_val - nice_min_val) / nice_tick_incr)
        nice_max_val = nice_min_val + needed * nice_tick_incr

        tick_values = []
        current_val = nice_min_val
        while current_val <= nice_max_val + 1e-12:
            tick_values.append(current_val)
            current_val += nice_tick_incr

        if is_log_scale:
            tick_values = [10 ** val for val in tick_values]

        return tick_values

    # Date tick logic
    if min_val == max_val:
        max_val = min_val + 0.1

    if time_indicator == "year":
        dt = (max_val - min_val) / 365.242199
    else:
        dt = (max_val - min_val) / 31

    rough_tick_incr = (dt / num_ticks) if num_ticks else dt
    if rough_tick_incr == 0:
        rough_tick_incr = 1

    exponent = math.floor(math.log10(abs(rough_tick_incr)))
    nice_tick_incr = 10 ** exponent

    ratio = abs(rough_tick_incr) / nice_tick_incr
    if ratio < 1.5:
        nice_tick_incr *= 1
    elif ratio < 3:
        nice_tick_incr *= 2
    else:
        nice_tick_incr *= 5

    if nice_tick_incr < 1:
        nice_tick_incr = 1

    nice_min_val = 0
    needed = math.ceil((dt - nice_min_val) / nice_tick_incr)
    nice_max_val = nice_min_val + needed * nice_tick_incr

    tick_values = []
    current_val = nice_min_val
    while current_val <= nice_max_val + 1e-12:
        if time_indicator == "year":
            tick_values.append(current_val * 365.242199 + min_val)
        else:
            tick_values.append(current_val * 31 + min_val)
        current_val += nice_tick_incr

    return tick_values


def builtins_min(a, b):
    return a if a <= b else b


def builtins_max(a, b):
    return a if a >= b else b
