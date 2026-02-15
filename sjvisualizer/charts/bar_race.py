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
from ..utils.scaling import HEIGHT, WIDTH, SCALEFACTOR


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
    orientation:
        Bar direction: ``"horizontal"`` (default) or ``"vertical"``.
    category_label_angle:
        Rotation angle (degrees) for category labels. Defaults to ``30`` for
        vertical bars (to reduce overlap) and ``0`` for horizontal bars.

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
        orientation: str = "horizontal",
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
        category_label_angle: float | int | None = None,
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

        # Orientation of bars: "horizontal" (default) or "vertical"
        orientation = (orientation or "horizontal").lower().strip()
        if orientation in ("h", "hor", "horizontal"):
            orientation = "horizontal"
        elif orientation in ("v", "ver", "vertical"):
            orientation = "vertical"
        else:
            raise ValueError("orientation must be 'horizontal' or 'vertical'")
        self.orientation = orientation

        # Rotation angle (degrees) for category labels.
        # Primarily useful in vertical mode to reduce overlap.
        if category_label_angle is None:
            category_label_angle = 30 if self.orientation == "vertical" else 0
        self.category_label_angle = float(category_label_angle)

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
        """Initial draw for the bar race."""

        data = self._get_data_for_frame(time_obj)

        self.graph_elements = {}

        # Layout tuning.
        # For horizontal bars we reserve a left margin for category labels.
        # For vertical bars we use the full width and place category labels
        # in a dedicated bottom margin.
        left_margin = int(1 / 4 * self.width) if self.orientation == "horizontal" else 0

        if self.orientation == "horizontal":
            bar_thickness = int(self.height / self.number_of_bars * 0.75)
            self._layout = {
                "orientation": "horizontal",
                "left_margin": left_margin,
                "bottom_margin": 0,
                "bar_thickness": bar_thickness,
                "step": self.height / self.number_of_bars,
                "axis_x": self.x_pos + left_margin,
                "axis_y": self.y_pos - 10,
                "bar_area_width": self.width - left_margin,
                "bar_area_height": self.height,
            }
        else:
            # Bottom margin reserved for category labels in vertical mode.
            # Keep it tight so labels sit close to the bars while still
            # avoiding clipping at the bottom of the subplot.
            base_bottom = max(self.height * 0.06, (self.font_size / SCALEFACTOR) * 1.6)
            # Rotated labels need slightly more room, but avoid overly large gaps.
            if abs(getattr(self, "category_label_angle", 0) or 0) > 0.1:
                base_bottom *= 1.10
            bottom_margin = int(base_bottom)
            bar_area_width = self.width - left_margin
            bar_area_height = self.height - bottom_margin
            # Use most of the available width.
            bar_thickness = int(bar_area_width / self.number_of_bars * 0.90)
            self._layout = {
                "orientation": "vertical",
                "left_margin": left_margin,
                "bottom_margin": bottom_margin,
                "bar_thickness": bar_thickness,
                "step": bar_area_width / self.number_of_bars,
                "axis_x": self.x_pos + left_margin,
                "axis_y": self.y_pos + bar_area_height,
                "bar_area_width": bar_area_width,
                "bar_area_height": bar_area_height,
            }

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
                bar_height=self._layout["bar_thickness"],
                orientation=self.orientation,
            )

        # Axis for the bar lengths/heights.
        if self.orientation == "horizontal":
            self.axis1 = axis(
                canvas=self.canvas,
                decimal_places=self.decimal_places,
                n=4,
                orientation="horizontal",
                x=self._layout["axis_x"],
                y=self._layout["axis_y"],
                length=self._layout["bar_area_width"],
                allow_decrease=self.allow_decrease,
                is_date=False,
                font_size=int(self.font_size / SCALEFACTOR / 1.5),
                color=self.font_color,
                anchor="n",
                width=self.height,
            )
        else:
            self.axis1 = axis(
                canvas=self.canvas,
                decimal_places=self.decimal_places,
                n=4,
                orientation="vertical",
                x=self._layout["axis_x"],
                y=self._layout["axis_y"],
                length=self._layout["bar_area_height"],
                allow_decrease=self.allow_decrease,
                is_date=False,
                font_size=int(self.font_size / SCALEFACTOR / 1.5),
                color=self.font_color,
                anchor="w",
                width=self._layout["bar_area_width"],
            )

        minimum = 0 if data.min() > 0 else data.min()
        self.axis1.draw(min_val=minimum, max_val=data.max())

        # Position bars for the first frame (avoids a one-frame "jump")
        self.update(time_obj)

    def update(self, time_obj):
        """Update all bars and the axis for a given frame."""

        data = self._get_data_for_frame(time_obj)

        if self.sort:
            data = data.sort_values(ascending=False)

        if self.orientation == "horizontal":
            bar_y_pos = self.y_pos + (self.height / self.number_of_bars) / 2

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

        else:
            step = float(self._layout.get("step") or (self._layout["bar_area_width"] / self.number_of_bars))
            bar_x_pos = self._layout["axis_x"] + step / 2

            for i, (name, d) in enumerate(data.items()):
                if d:
                    if i == self.number_of_bars:
                        bar_x_pos = WIDTH + step

                    if i < self.number_of_bars + 1:
                        self.graph_elements[name].update(d, bar_x_pos)
                    else:
                        self.graph_elements[name].delete()

                    bar_x_pos = bar_x_pos + step
                else:
                    self.graph_elements[name].delete()

        minimum = 0 if data.min() > 0 else data.min()
        self.axis1.update(min_val=minimum, max_val=data.max())

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
        orientation=None,
    ):
        self.name = name
        self.canvas = canvas
        self.unite = unit  # legacy typo attribute
        self.font_color = font_color
        self.font_size = font_size
        self.chart = chart

        self.orientation = (orientation or getattr(self.chart, "orientation", "horizontal")).lower().strip()
        if self.orientation in ("h", "hor", "horizontal"):
            self.orientation = "horizontal"
        elif self.orientation in ("v", "ver", "vertical"):
            self.orientation = "vertical"
        else:
            self.orientation = "horizontal"

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
            anchor="ne",
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

    def update(self, value, bar_pos):
        """Update the bar geometry for the current frame.

        Parameters
        ----------
        value:
            The current numeric value for this category.
        bar_pos:
            Primary position used for ranking animation:
            - horizontal charts: y position (row)
            - vertical charts:   x position (column)
        """

        if value:
            if self.exists:
                if self.orientation == "horizontal":
                    if not hasattr(self, "y"):
                        self.y = bar_pos

                    F = self.stiffness * (bar_pos - self.y) - self.damping * self.v
                    self.a = F / self.mass
                    self.v = self.v + self.a
                    self.y = self.y + self.v

                    left_margin = 0
                    if hasattr(self.chart, "_layout"):
                        left_margin = int(self.chart._layout.get("left_margin", 0) or 0)
                    x0 = self.chart.axis1.calc_positions(0) + self.chart.x_pos + left_margin
                    x1 = self.chart.axis1.calc_positions(value) + self.chart.x_pos + left_margin
                    left = min(x0, x1)
                    right = max(x0, x1)

                    self.canvas.coords(
                        self.rect,
                        left,
                        self.y - self.bar_height / 2,
                        right,
                        self.y + self.bar_height / 2,
                    )

                    rect_bbox = self.canvas.coords(self.rect)
                    self.canvas.itemconfig(self.value, text=format_value(value, decimal=self.chart.decimal_places) + self.unit)

                    # Place value text inside near the bar end if it fits, otherwise outside.
                    value_bbox = self.canvas.bbox(self.value) or (0, 0, 0, 0)
                    text_w = (value_bbox[2] - value_bbox[0]) or 0
                    bar_w = rect_bbox[2] - rect_bbox[0]

                    direction = 1 if x1 >= x0 else -1
                    if direction == 1:
                        if bar_w * 0.75 > text_w:
                            self.canvas.coords(self.value, rect_bbox[2] - 10, self.y)
                            self.canvas.itemconfig(self.value, anchor="e")
                        else:
                            self.canvas.coords(self.value, rect_bbox[2] + 10, self.y)
                            self.canvas.itemconfig(self.value, anchor="w")
                    else:
                        if bar_w * 0.75 > text_w:
                            self.canvas.coords(self.value, rect_bbox[0] + 10, self.y)
                            self.canvas.itemconfig(self.value, anchor="w")
                        else:
                            self.canvas.coords(self.value, rect_bbox[0] - 10, self.y)
                            self.canvas.itemconfig(self.value, anchor="e")

                    # Category label on the left
                    self.canvas.coords(self.label, self.chart.x_pos + left_margin - 10, self.y)
                    self.canvas.itemconfig(self.label, anchor="e")

                    # Optional icon after the value text
                    if self.img:
                        vb = self.canvas.bbox(self.value)
                        if vb:
                            if direction == 1:
                                self.canvas.coords(self.img_obj, vb[2] + 20, self.y)
                                self.canvas.itemconfig(self.img_obj, anchor="w")
                            else:
                                self.canvas.coords(self.img_obj, vb[0] - 20, self.y)
                                self.canvas.itemconfig(self.img_obj, anchor="e")

                else:
                    if not hasattr(self, "x"):
                        self.x = bar_pos

                    F = self.stiffness * (bar_pos - self.x) - self.damping * self.v
                    self.a = F / self.mass
                    self.v = self.v + self.a
                    self.x = self.x + self.v

                    half = self.bar_height / 2  # thickness for vertical bars
                    axis_y = self.chart.axis1.y
                    y0 = axis_y - self.chart.axis1.calc_positions(0)
                    y1 = axis_y - self.chart.axis1.calc_positions(value)
                    top = min(y0, y1)
                    bottom = max(y0, y1)

                    self.canvas.coords(
                        self.rect,
                        self.x - half,
                        top,
                        self.x + half,
                        bottom,
                    )

                    self.canvas.itemconfig(self.value, text=format_value(value, decimal=self.chart.decimal_places) + self.unit)

                    # Value label above (positive) or below (negative) the bar end.
                    self.canvas.coords(self.value, self.x, top - 8)
                    self.canvas.itemconfig(self.value, anchor="s")

                    # Category label just below the bars, centered under each bar.
                    bottom_margin = 0
                    if hasattr(self.chart, "_layout"):
                        bottom_margin = int(self.chart._layout.get("bottom_margin", 0) or 0)

                    # Keep labels close to the bars (avoid large empty gaps).
                    pad = max(20, int((self.chart.font_size / SCALEFACTOR) * 0.35))
                    label_y = axis_y + pad

                    # Rotate category labels to reduce overlap.
                    angle = float(getattr(self.chart, "category_label_angle", 30) or 0)

                    x_anchor = self.x
                    # Clamp within subplot bounds to reduce clipping at the edges.
                    if hasattr(self.chart, "x_pos") and hasattr(self.chart, "width"):
                        x_min = self.chart.x_pos + 2
                        x_max = self.chart.x_pos + self.chart.width - 2
                        x_anchor = max(x_min, min(x_anchor, x_max))

                    self.canvas.coords(self.label, x_anchor, label_y)
                    if abs(angle) > 0.1:
                        try:
                            self.canvas.itemconfig(self.label, anchor="e", angle=angle)
                        except Exception:
                            # Older Tk builds may not support angled text.
                            self.canvas.itemconfig(self.label, anchor="e")
                    else:
                        self.canvas.itemconfig(self.label, anchor="e")
                    if self.img:
                        vb = self.canvas.bbox(self.value)
                        if vb:
                            self.canvas.coords(self.img_obj, vb[2] + 10, (vb[1] + vb[3]) / 2)
                            self.canvas.itemconfig(self.img_obj, anchor="w")

            else:
                # Recreate bar if it was previously deleted.
                if self.orientation == "horizontal":
                    self.y = bar_pos
                else:
                    self.x = bar_pos
                self.v = 0
                self.a = 0
                self.draw(value)
                self.update(value, bar_pos)
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
