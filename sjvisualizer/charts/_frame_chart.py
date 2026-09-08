"""Shared cached frame data and styling for discrete-frame charts."""
import numpy as np
import pandas as pd

from ..core.subplot import sub_plot
from ..core.axis import axis
from ..utils.colors import color_palette, from_rgb


def numeric_data(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("data must be a nonempty DataFrame")
    if not df.index.is_unique or not df.index.is_monotonic_increasing or df.index.hasnans:
        raise ValueError("frame index must be sorted, unique and without missing values")
    if not df.columns.is_unique:
        raise ValueError("column names must be unique")
    values = df.to_numpy(dtype=float, copy=True)
    return np.where(np.isfinite(values), values, 0.0)


class FrameChart(sub_plot):
    """Cache numeric data; nonfinite values become zero. Input is a snapshot."""
    def __init__(self, canvas=None, df=None, *, unit="", **kwargs):
        self._values = numeric_data(df)
        self._last_frame = None
        self._drawn = False
        self.unit = unit
        super().__init__(canvas=canvas, df=df.copy(), **kwargs)

    def frame(self, time):
        if time is None:
            return 0
        if isinstance(self.df.index, pd.DatetimeIndex):
            return int(self.df.index.get_indexer([pd.Timestamp(time)], method="nearest")[0])
        return int(self.df.index.get_loc(time))

    def color(self, name):
        if name not in self.colors:
            palette = getattr(self.sjcanvas, "color_palette", None)
            self.colors[name] = palette.pop(0) if palette else color_palette[len(self.colors) % len(color_palette)]
        return from_rgb(self.colors[name])

    def text(self, x, y, **kwargs):
        options = dict(font=(self.text_font, int(self.font_size)), fill=from_rgb(self.font_color))
        options.update(kwargs)
        return self.canvas.create_text(x, y, **options)

    def make_axis(self, orientation, n=5, **kwargs):
        vertical = orientation == "vertical"
        return axis(canvas=self.canvas, x=self.x_pos, y=self.y_pos+self.height,
                    length=self.height if vertical else self.width,
                    width=self.width if vertical else self.height, orientation=orientation,
                    n=n, allow_decrease=True, font_size=self.font_size,
                    text_font=self.text_font, color=self.font_color, **kwargs)
