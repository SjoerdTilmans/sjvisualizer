"""Bar race chart.

A bar race shows the top-N categories at each time step, animating bar lengths
and vertical order over time.

Typical usage
-------------

.. code-block:: python

    from sjvisualizer import Canvas, BarRace, DataHandler

    cv = Canvas.canvas()
    df = DataHandler.DataHandler("mydata.xlsx", number_of_frames=600).df

    chart = BarRace.bar_race(
        df=df,
        canvas=cv,
        x_pos=100,
        y_pos=150,
        width=1400,
        height=800,
        number_of_bars=10,
        allow_decrease=False,
        unit="",
    )
    cv.add_sub_plot(chart)
    cv.play(df=df)
"""

from __future__ import annotations

import os
import random
from tkinter import font

import pandas as pd

from ..core.subplot import sub_plot, load_image
from ..core.axis import axis
from ..utils.colors import from_rgb, min_color, max_color
from ..utils.format import format_value
from ..utils.scaling import HEIGHT, SCALEFACTOR


class bar_race(sub_plot):
    """Animated bar race chart.

    Parameters
    ----------
    df:
        Time-indexed dataframe. Each column is a category; each row is a frame.
    number_of_bars:
        How many bars to display at once (top-N). Defaults to ``min(10, n_cols)``.
    allow_decrease:
        If ``False`` (default), the axis maximum is sticky and will not shrink.
    sort:
        If ``True`` (default), categories are sorted by value each frame.
    unit:
        Optional unit suffix appended to the numeric value labels.

    All common positioning/styling options are inherited from
    :class:`sjvisualizer.core.subplot.sub_plot` (e.g. ``x_pos``, ``y_pos``,
    ``width``, ``height``, ``colors``).
    """

    def __init__(
        self,
        df: pd.DataFrame | None = None,
        canvas=None,
        *,
        x_pos=None,
        y_pos=None,
        width=None,
        height=None,
        colors=None,
        root=None,
        anchor="c",
        title: str | None = None,
        font_color=(0, 0, 0),
        back_ground_color=(255, 255, 255),
        text_font: str = "Microsoft JhengHei UI",
        font_size: int = 25,
        start_time=None,
        number_of_bars: int | None = None,
        allow_decrease: bool = False,
        sort: bool = True,
        unit: str = "",
        decimal_places: int | None = None,
        **kwargs,
    ):
        # Backwards-compatible: allow df to be passed through kwargs.
        if df is None and "df" in kwargs:
            df = kwargs.pop("df")

        if not isinstance(df, pd.DataFrame):
            raise ValueError("bar_race requires df=<pandas.DataFrame>")

        self.df = df
        self.start_time = start_time if start_time is not None else list(df.index)[0]

        if number_of_bars is None:
            number_of_bars = len(df.columns) if len(df.columns) < 10 else 10
        self.number_of_bars = int(number_of_bars)

        self.allow_decrease = bool(allow_decrease)
        self.sort = bool(sort)
        self.unit = unit

        if decimal_places is not None:
            kwargs["decimal_places"] = int(decimal_places)

        super().__init__(
            canvas=canvas,
            width=width,
            height=height,
            x_pos=x_pos,
            y_pos=y_pos,
            colors=colors,
            root=root,
            anchor=anchor,
            title=title,
            font_color=font_color,
            back_ground_color=back_ground_color,
            text_font=text_font,
            font_size=font_size,
            **kwargs,
        )

    def draw(self, time_obj):
        data = self._get_data_for_frame(time_obj)

        self.graph_elements = {}
        bar_height = int(self.height / self.number_of_bars * 0.75)

        for name, d in data.items():
            self.graph_elements[name] = bar(
                name=name,
                canvas=self.canvas,
                value=d,
                unit=self.unit,
                font_color=self.font_color,
                colors=self.colors,
                chart=self,
                text_font=self.text_font,
                font_size=self.font_size,
                bar_height=bar_height,
            )

        data = self._get_data_for_frame(time_obj)
        self.axis1 = axis(
            canvas=self.canvas,
            decimal_places=self.decimal_places,
            n=4,
            orientation="horizontal",
            x=self.x_pos + int(1 / 4 * self.width),
            y=self.y_pos - 10,
            length=self.width - int(1 / 4 * self.width),
            allow_decrease=self.allow_decrease,
            is_date=False,
            font_size=int(self.font_size / SCALEFACTOR / 1.5),
            color=self.font_color,
            anchor="n",
            width=self.height,
        )

        minimum = 0 if min(data) > 0 else min(data)
        self.axis1.draw(min=minimum, max=max(data))

    def update(self, time_obj):
        data = self._get_data_for_frame(time_obj)

        bar_y_pos = self.y_pos + (self.height / self.number_of_bars) / 2

        if self.sort:
            data = self._get_data_for_frame(time_obj).sort_values(ascending=False)

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

        minimum = 0 if min(data) > 0 else min(data)
        self.axis1.update(min=minimum, max=max(data))


class bar:
    """A single animated bar in a :class:`bar_race`.

    This class manages the Tk canvas primitives (rectangle, label, value text,
    optional icon) and applies a simple spring-damper model to smooth vertical
    motion between frames.
    """

    def __init__(
        self,
        name=None,
        canvas=None,
        value=0,
        font_color=(0, 0, 0),
        colors=None,
        font_size=12,
        chart=None,
        text_font="Microsoft JhengHei UI",
        bar_height=50,
        unit="",
    ):
        self.name = name
        self.canvas = canvas
        self.unite = unit  # legacy typo attribute
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart

        if colors is None:
            colors = {}
        self.colors = colors

        self.text_font = text_font
        self.exists = False
        self.bar_height = bar_height
        self.unit = unit

        # Simple spring-damper dynamics for vertical transitions.
        self.mass = 2
        self.stiffness = 0.1
        self.damping = 0.6

        self.v = 0
        self.a = 0

        self._font_obj = font.Font(family=self.text_font, size=int(self.font_size / SCALEFACTOR))
        self._font_obj_num = font.Font(family=self.text_font, size=int(self.font_size / SCALEFACTOR * 0.9))

        try:
            self.img = load_image(
                os.path.join("assets", self.name.replace("*", "") + ".png"),
                int(bar_height),
                int(bar_height),
                self.chart.root,
                name,
            )
        except Exception:
            print(f"No image for {self.name}")
            self.img = None

        if isinstance(colors, dict):
            if name in colors:
                self.color = from_rgb(colors[name])
            else:
                self._set_color()
        else:
            self._set_color()

        self.draw(value)

    def _set_color(self):
        if self.chart.sjcanvas and getattr(self.chart.sjcanvas, "color_palette", None):
            color = self.chart.sjcanvas.color_palette[0]
            self.chart.sjcanvas.color_palette.pop(0)
        else:
            color = (
                random.randint(min_color, max_color),
                random.randint(min_color, max_color),
                random.randint(min_color + 30, max_color),
            )

        self.color = from_rgb(color)
        self.colors[self.name] = color

    def draw(self, value):
        self.rect = self.canvas.create_rectangle(50, 50, 500, 500, fill=self.color, outline="")
        self.label = self.canvas.create_text(
            0,
            0,
            text=self.name,
            anchor="e",
            font=self._font_obj,
            fill=from_rgb(self.font_color),
        )
        self.value = self.canvas.create_text(
            0,
            0,
            text=format_value(value, decimal=self.chart.decimal_places),
            anchor="w",
            font=self._font_obj_num,
            fill=from_rgb(self.font_color),
        )
        if self.img:
            self.img_obj = self.canvas.create_image(-1000, -1000, image=self.img, anchor="w")
        self.exists = True

    def update(self, value, bar_y_pos):
        if value:
            if self.exists:
                if not hasattr(self, "y"):
                    self.y = bar_y_pos

                F = self.stiffness * (bar_y_pos - self.y) - self.damping * self.v
                self.a = F / self.mass
                self.v = self.v + self.a
                self.y = self.y + self.v

                self.canvas.coords(
                    self.rect,
                    self.chart.axis1.calc_positions(0) + self.chart.x_pos + int(1 / 4 * self.chart.width),
                    self.y - self.bar_height / 2,
                    self.chart.axis1.calc_positions(value) + self.chart.x_pos + int(1 / 4 * self.chart.width),
                    self.y + self.bar_height / 2,
                )

                rect_bbox = self.canvas.coords(self.rect)
                self.canvas.itemconfig(self.value, text=format_value(value, decimal=self.chart.decimal_places) + self.unit)

                value_bbox = self.canvas.bbox(self.value)
                if (rect_bbox[2] - rect_bbox[0]) * 0.75 > (value_bbox[2] - value_bbox[0]):
                    self.canvas.coords(self.value, rect_bbox[2] - 10, self.y)
                    self.canvas.itemconfig(self.value, anchor="e")
                else:
                    self.canvas.coords(self.value, rect_bbox[2] + 10, self.y)
                    self.canvas.itemconfig(self.value, anchor="w")

                self.canvas.coords(self.label, self.chart.x_pos + int(1 / 4 * self.chart.width) - 10, self.y)

                value_bbox = self.canvas.bbox(self.value)
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
        """Remove all Tk primitives for this bar."""

        if hasattr(self, "rect"):
            self.canvas.delete(self.rect)
        if hasattr(self, "label"):
            self.canvas.delete(self.label)
        if hasattr(self, "value"):
            self.canvas.delete(self.value)
        if hasattr(self, "img_obj"):
            self.canvas.delete(self.img_obj)
        self.exists = False
