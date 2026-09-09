"""Timestamp overlay using the shared date formatter."""
import pandas as pd
from ..core.subplot import sub_plot
from ..utils.colors import from_rgb
from ..utils.format import format_date
from ..utils.scaling import tk_font_size

__all__ = ["date"]


class date(sub_plot):
    def __init__(self, canvas=None, *, prefix="", time_indicator="year", format="Europe", **kwargs):
        if time_indicator not in ("year", "month", "day"):
            raise ValueError("time_indicator must be year, month or day")
        self.prefix, self.time_indicator, self.format = prefix, time_indicator, format
        self.obj_id, self._last_text = None, None
        super().__init__(canvas, **kwargs)

    def draw(self, time):
        if self.obj_id is not None:
            return
        direction = -1 if self.anchor == "se" else 1
        self.obj_id = self.canvas.create_text(self.x_pos+direction*self.width/2,
            self.y_pos+direction*self.height/2, anchor=self.anchor,
            font=(self.text_font, tk_font_size(self.font_size)), fill=from_rgb(self.font_color))
        self.update(time)

    def update(self, time):
        text = self.prefix + (format_date(pd.Timestamp(time), self.time_indicator, self.format)
                              if time is not None else "")
        if text != self._last_text:
            self.canvas.itemconfig(self.obj_id, text=text)
            self._last_text = text
