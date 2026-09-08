"""Animated scatter bubbles, using the shared subplot and axis components."""

import numpy as np
import pandas as pd

from ..core.axis import axis
from ..core.subplot import sub_plot
from ..utils.colors import color_palette, from_rgb

__all__ = ["bubble_chart"]


class bubble_chart(sub_plot):
    """Animate aligned ``df_x`` and ``df_y`` frames (columns are categories).

    Optional ``df_size`` controls bubble *area*, with the largest observed size
    having diameter ``max_bubble_size`` (default 15% of plot height). Without
    sizes, ``marker_size`` is the diameter. Missing/nonfinite coordinates and
    nonpositive sizes are hidden; log axes also hide nonpositive coordinates.
    Frames must have identical indices and category sets; column order may differ.
    Axis limits expand during playback. ``x_min/x_max/y_min/y_max`` fix bounds.
    """

    def __init__(self, canvas=None, df_x=None, df_y=None, df_size=None, *,
                 marker_size=15, max_bubble_size=None, display_label=True,
                 x_log=False, y_log=False, x_ticks=5, y_ticks=5, unit="",
                 x_min=None, x_max=None, y_min=None, y_max=None, **kwargs):
        frames = [df_x, df_y] + ([] if df_size is None else [df_size])
        for frame in frames:
            if not isinstance(frame, pd.DataFrame) or frame.empty:
                raise ValueError("Bubble data must be nonempty DataFrames")
            if not frame.index.is_unique or not frame.columns.is_unique:
                raise ValueError("Bubble indices and columns must be unique")
            if not frame.index.equals(df_x.index) or set(frame.columns) != set(df_x.columns):
                raise ValueError("Bubble frames must have matching indices and categories")
        if marker_size <= 0 or (max_bubble_size is not None and max_bubble_size <= 0):
            raise ValueError("Bubble diameters must be positive")
        for low, high, log in ((x_min, x_max, x_log), (y_min, y_max, y_log)):
            if any(v is not None and (not np.isfinite(v) or (log and v <= 0)) for v in (low, high)):
                raise ValueError("Bounds must be finite and positive for log axes")
            if low is not None and high is not None and low >= high:
                raise ValueError("Axis minimum must be less than maximum")
        self.df_x, self.df_y, self.df_size = df_x, df_y, df_size
        self._arrays = [f.reindex(columns=df_x.columns).to_numpy(dtype=float) for f in frames]
        self.marker_size, self.max_bubble_size = marker_size, max_bubble_size
        self.display_label = display_label
        self.x_log, self.y_log = x_log, y_log
        self._axis_options = [(x_ticks, x_min, x_max, ""), (y_ticks, y_min, y_max, unit)]
        self._size_max = 0.0
        self.bubbles = {}
        self._last_frame = None
        super().__init__(canvas=canvas, df=df_x, **kwargs)

    def draw(self, time):
        if self.bubbles:
            return
        for i, (ticks, low, high, unit) in enumerate(self._axis_options):
            ax = axis(canvas=self.canvas, orientation="vertical" if i else "horizontal",
                      x=self.x_pos, y=self.y_pos + self.height,
                      length=self.height if i else self.width, width=self.width if i else self.height,
                      n=ticks, font_size=self.font_size, text_font=self.text_font,
                      color=self.font_color, ticks_only=False, unit=unit,
                      decimal_places=self.decimal_places, is_log_scale=self.y_log if i else self.x_log,
                      fixed_min=low, fixed_max=high)
            setattr(self, "y_axis" if i else "x_axis", ax)
        for i, name in enumerate(self.df.columns):
            if name not in self.colors:
                palette = getattr(self.sjcanvas, "color_palette", None)
                self.colors[name] = palette.pop(0) if palette else color_palette[i % len(color_palette)]
            color = from_rgb(self.colors[name])
            marker = self.canvas.create_oval(0, 0, 0, 0, fill=color, outline=color, state="hidden")
            label = self.canvas.create_text(0, 0, text=str(name), anchor="n",
                font=(self.text_font, max(1, int(self.font_size * 2 / 3))),
                fill=from_rgb(self.font_color), state="hidden") if self.display_label else None
            self.bubbles[name] = (marker, label)
        self._axes_drawn = False
        self.update(time)

    def update(self, time):
        pos = 0 if time is None else self.df.index.get_loc(time)
        if pos == self._last_frame:
            return
        x, y = (a[pos] for a in self._arrays[:2])
        valid = np.isfinite(x) & np.isfinite(y)
        if self.x_log:
            valid &= x > 0
        if self.y_log:
            valid &= y > 0
        sizes = self._arrays[2][pos] if self.df_size is not None else None
        if sizes is not None:
            valid &= np.isfinite(sizes) & (sizes > 0)
        for values, ax, log in ((x, self.x_axis, self.x_log), (y, self.y_axis, self.y_log)):
            visible = values[valid]
            low = float(visible.min()) if len(visible) else (ax.min_val if ax.min_val is not None else (1 if log else 0))
            high = float(visible.max()) if len(visible) else (ax.max_val if ax.max_val is not None else (10 if log else 1))
            low = 10 ** np.floor(np.log10(low)) if log else min(0, low)
            high = max(high, low * 10) if log and high <= low else high
            if high <= low:
                high = low + 1
            (ax.update if self._axes_drawn else ax.draw)(low, high)
        self._axes_drawn = True
        if sizes is not None:
            self._size_max = max(self._size_max, float(sizes[valid].max()) if valid.any() else 0)
        for i, (marker, label) in enumerate(self.bubbles.values()):
            state = "normal" if valid[i] else "hidden"
            self.canvas.itemconfig(marker, state=state)
            if label is not None:
                self.canvas.itemconfig(label, state=state)
            if not valid[i]:
                continue
            px = self.x_pos + self.x_axis.calc_positions(x[i])
            py = self.y_pos + self.height - self.y_axis.calc_positions(y[i])
            diameter = self.marker_size if sizes is None else (self.max_bubble_size or .15 * self.height) * np.sqrt(sizes[i] / self._size_max)
            r = diameter / 2
            self.canvas.coords(marker, px-r, py-r, px+r, py+r)
            if label is not None:
                self.canvas.coords(label, px, py+r+5)
        for _, label in self.bubbles.values():
            if label is not None:
                self.canvas.tag_raise(label)
        self._last_frame = pos
