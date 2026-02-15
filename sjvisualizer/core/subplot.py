"""Subplot base class and legacy helpers.

The SJVisualizer API is built around a *canvas* (see :mod:`sjvisualizer.core.canvas`)
that owns a ``tkinter.Canvas`` plus an animation/playback loop.

Each visual element (a "chart") is implemented as a *subplot*:

- Subclass :class:`sub_plot`
- Implement :meth:`draw` (initial draw)
- Implement :meth:`update` (per-frame update)

This module intentionally keeps a few legacy helper functions (e.g.
:func:`load_image`, :func:`truncate`) because many charts historically imported
those from ``Canvas.py``.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any

import pandas as pd
import tkinter
from tkinter import font

from PIL import Image, ImageTk

from ..utils.colors import from_rgb
from ..utils.format import format_date, format_value
from ..utils.scaling import SCALEFACTOR, WIDTH, HEIGHT


# Legacy global default (Canvas.canvas.set_decimals updates this)
decimal_places: int = 0


class sub_plot:
    """Base class for all chart/subplot types.

    The goal of this base class is to provide *shared wiring* for all charts:

    - Resolve the drawing surface (either a raw ``tkinter.Canvas`` or an
      :class:`sjvisualizer.core.canvas.canvas` instance).
    - Store a bounding box (``x_pos``, ``y_pos``, ``width``, ``height``).
    - Store shared styling defaults (``colors``, ``font_color``, ``text_font``).
    - Provide a consistent place to hang arbitrary chart-specific attributes.

    Parameters
    ----------
    canvas:
        Either a ``tkinter.Canvas`` instance **or** an instance of
        :class:`sjvisualizer.core.canvas.canvas`.

        If you pass the SJVisualizer canvas, the subplot will internally use its
        ``.canvas`` attribute.
    width, height:
        Size of the subplot bounding box in pixels. Defaults are based on the
        primary monitor size as detected in :mod:`sjvisualizer.utils.scaling`.
    x_pos, y_pos:
        Top-left position of the subplot bounding box in pixels.
    colors:
        Shared color mapping ``{label: (r, g, b)}`` used by charts to keep colors
        stable across frames.
    root:
        The Tk root window. Usually set automatically via
        :meth:`sjvisualizer.core.canvas.canvas.add_sub_plot`.
    anchor:
        Default Tk anchor for elements; usage is chart-specific.
    title:
        Optional title text drawn above the subplot's bounding box.
    font_color, back_ground_color:
        Common foreground/background colors used by many charts.
    text_font, font_size:
        Default font settings (charts may override or ignore these).
    **kwargs:
        Any additional keyword arguments are accepted and stored as attributes.
        This keeps older chart code working while allowing chart-specific
        configuration to live in chart subclasses.
    """

    def __init__(
        self,
        canvas,
        width=None,
        height=None,
        x_pos=None,
        y_pos=None,
        colors=None,
        root=None,
        anchor="c",
        title: str | None = None,
        font_color=(0, 0, 0),
        back_ground_color=(255, 255, 255),
        font_size: int = 25,
        text_font: str = "Microsoft JhengHei UI",
        **kwargs: Any,
    ):
        # Store chart-specific configuration (and preserve legacy patterns).
        self.__dict__.update(kwargs)

        # If someone passed common params through kwargs, prefer the explicit
        # arguments but fall back to the kwarg attribute when explicit is None.
        if width is None and hasattr(self, "width"):
            width = getattr(self, "width")
        if height is None and hasattr(self, "height"):
            height = getattr(self, "height")
        if x_pos is None and hasattr(self, "x_pos"):
            x_pos = getattr(self, "x_pos")
        if y_pos is None and hasattr(self, "y_pos"):
            y_pos = getattr(self, "y_pos")
        if colors is None and hasattr(self, "colors"):
            colors = getattr(self, "colors")
        if root is None and hasattr(self, "root"):
            root = getattr(self, "root")
        if anchor is None and hasattr(self, "anchor"):
            anchor = getattr(self, "anchor")

        # Canvas wiring
        if isinstance(canvas, tkinter.Canvas):
            self.canvas = canvas
            self.sjcanvas = None
        elif hasattr(canvas, "canvas") and isinstance(getattr(canvas, "canvas"), tkinter.Canvas):
            # sjvisualizer.core.canvas.canvas instance (duck-typed)
            self.canvas = canvas.canvas
            self.sjcanvas = canvas
        else:
            raise TypeError("Please set canvas to a tkinter.Canvas or sjvisualizer canvas()")

        if colors is None:
            colors = {}

        self.colors = colors
        self.root = root
        self.anchor = anchor

        # Common styling defaults
        self.font_color = font_color
        self.back_ground_color = back_ground_color
        self.font_size = font_size
        self.text_font = text_font

        # Bounding box defaults
        self.width = 0.65 * WIDTH if width is None else width

        if height is None:
            self.height = 0.65 * HEIGHT
            self.height_is_set = False
        else:
            self.height = height
            self.height_is_set = True

        self.x_pos = 0.175 * WIDTH if x_pos is None else x_pos
        self.y_pos = 0.175 * HEIGHT if y_pos is None else y_pos

        # Shared default for formatting numbers.
        if not hasattr(self, "decimal_places"):
            self.decimal_places = decimal_places

        # Backwards-compatible convenience: infer a start_time if a df was
        # provided (either as `df` or older `df_x` / `df_y`).
        df = getattr(self, "df", None)
        if not isinstance(df, pd.DataFrame):
            if hasattr(self, "df_x") and isinstance(getattr(self, "df_x"), pd.DataFrame):
                df = getattr(self, "df_x")
                setattr(self, "df", df)
            elif hasattr(self, "df_y") and isinstance(getattr(self, "df_y"), pd.DataFrame):
                df = getattr(self, "df_y")
                setattr(self, "df", df)

        if isinstance(df, pd.DataFrame) and not hasattr(self, "start_time"):
            try:
                self.start_time = list(df.index)[0]
            except Exception:
                self.start_time = None

        # Title (optional). Many charts rely on this being handled here.
        if title:
            self.canvas.create_text(
                self.x_pos + self.width / 2,
                self.y_pos - self.height / 18,
                anchor="s",
                text=title,
                font=font.Font(
                    family=self.text_font,
                    size=int(15 + self.height / 60 / SCALEFACTOR),
                    weight="bold",
                ),
                fill=from_rgb(self.font_color),
            )

        # If a root is already known, draw immediately.
        if self.root:
            self.draw(getattr(self, "start_time", None))

    def set_root(self, root):
        """Attach the Tk root and trigger the initial draw.

        The main canvas calls this automatically when you add the subplot.
        """

        if not self.root:
            self.root = root
            self.draw(getattr(self, "start_time", None))

    def save_colors(self, path: str = "colors/colors.json"):
        """Persist the current ``colors`` mapping to JSON."""

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.colors, file, indent=4)

    def draw(self, time_obj=None):  # noqa: D401
        """Draw the initial state of the chart.

        Subclasses should override this.
        """

        raise NotImplementedError

    def update(self, time_obj):
        """Advance the chart by one frame."""

        raise NotImplementedError

    def load_image(self):
        """Optional hook used by some legacy chart types."""

        raise NotImplementedError

    def _get_data_for_frame(self, time_obj, df=None):
        """Return the row for a given frame/time from a dataframe."""

        if not isinstance(df, pd.DataFrame):
            df = getattr(self, "df", None)
        if not isinstance(df, pd.DataFrame):
            raise ValueError("No dataframe available on this subplot.")
        return df.loc[time_obj]


# --- Legacy helpers (kept to minimize chart changes) ---


def load_image(path: str, x: int, y: int, root, name: str):
    """Legacy helper used by several charts to load+resize images.

    Keeps a reference on the Tk root to prevent garbage collection.
    """

    load = Image.open(path)
    load = load.resize((int(x * load.size[0] / load.size[1]), int(y)), resample=2)
    load = ImageTk.PhotoImage(load)

    i = 0
    while hasattr(root, name + str(i)):
        i += 1
    setattr(root, name + str(i), load)
    return load


def _from_rgb(rgb):
    """Backwards-compatible alias."""

    return from_rgb(rgb)


def truncate(n, decimals: int = 1):
    """Truncate/round a number while being robust to NaNs."""

    multiplier = 10 ** decimals
    if not math.isnan(n):
        return round(n * multiplier) / multiplier
    return 0


def calc_spacing(value, current_spacing, n):
    """Legacy spacing heuristic used by some charts."""

    if current_spacing * 4 < value:
        current_spacing = round(current_spacing * 2, -len(str(round(value))) + 1)
    if not current_spacing:
        current_spacing = 1
    return current_spacing


# Re-export format helpers for legacy imports
format_date = format_date
format_value = format_value
