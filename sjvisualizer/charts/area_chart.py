"""Stacked area animation with cached data and bounded polygon complexity."""

import numpy as np
import pandas as pd

from ..core.axis import axis
from ..core.subplot import sub_plot
from ..utils.colors import color_palette, from_rgb
from ..utils.scaling import tk_font_size

__all__ = ["area_chart", "area_plot"]


class area_chart(sub_plot):
    """Animate nonnegative time series stacked in column order (first on top).

    ``df`` needs a sorted, unique, timezone-naive DatetimeIndex. Missing and
    infinite values become zero; negative values are rejected. Polygons use at
    most ``max_points`` samples, including both endpoints (default 1000; None
    retains every sample). Sampling can omit narrow spikes. Original data and
    cumulative axis maxima remain exact. Seeking and repeated frames are safe.
    ``external_legend``, ``display_values``, ``unit`` and legacy date-range
    ``events`` are supported. ``draw_points`` shows current stack boundaries.
    Labels whose current value is zero, or would round to zero at the configured
    ``decimal_places``, are hidden. ``label_min_value`` can set an explicit
    cutoff instead. ``label_position="area"`` replaces the legend with contrasting labels at
    the horizontal midpoint of each rendered band. Labels hide when the band
    is too small to contain them. ``display_values`` still shows current values.
    ``label_position="right"`` places series-colored labels just outside the
    right edge, centered between each band's latest boundaries. Zero-height
    bands hide their labels; labels for narrow bands may overlap.
    """

    def __init__(self, canvas=None, df=None, *, x_ticks=5, y_ticks=5,
                 time_indicator="year", external_legend=True, display_values=False,
                 display_legend=True, unit="", max_points=1000, draw_points=False,
                 label_position="legend", label_min_value=None,
                 events=None, event_color=(225, 225, 225), draw_all_events=False, **kwargs):
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Area data must be a nonempty DataFrame")
        if not isinstance(df.index, pd.DatetimeIndex) or df.index.tz is not None or df.index.hasnans:
            raise ValueError("Area data needs a timezone-naive DatetimeIndex without NaT")
        if not df.index.is_unique or not df.index.is_monotonic_increasing or not df.columns.is_unique:
            raise ValueError("Area dates must be sorted and unique; columns must be unique")
        values = df.to_numpy(dtype=float)
        if np.any(values < 0):
            raise ValueError("Stacked area values must be nonnegative")
        values = np.where(np.isfinite(values), values, 0)
        if max_points is not None and (int(max_points) != max_points or max_points < 2):
            raise ValueError("max_points must be an integer >= 2 or None")
        self._values = values
        if label_position not in ("legend", "area", "right"):
            raise ValueError("label_position must be 'legend', 'area', or 'right'")
        if label_min_value is not None and (not np.isfinite(label_min_value) or label_min_value < 0):
            raise ValueError("label_min_value must be finite and nonnegative")
        self.label_position = label_position
        self.label_min_value = None if label_min_value is None else float(label_min_value)
        self._tops = np.cumsum(values[:, ::-1], axis=1)[:, ::-1]
        if not np.isfinite(self._tops).all():
            raise ValueError("Stacked totals exceed the supported numeric range")
        self._maxima = np.maximum.accumulate(self._tops[:, 0])
        self.max_points = None if max_points is None else int(max_points)
        self._times = (df.index - df.index[0]).total_seconds().to_numpy()
        self.x_ticks, self.y_ticks, self.time_indicator = x_ticks, y_ticks, time_indicator
        self.external_legend, self.display_values = external_legend, display_values
        self.display_legend, self.unit, self.draw_points = display_legend, unit, draw_points
        self.draw_all_events, self.event_color = draw_all_events, event_color
        self._events = []
        for name, dates in (events or {}).items():
            start, end = [pd.to_datetime(d, dayfirst=True) for d in dates]
            if pd.isna(start) or pd.isna(end) or end < start:
                raise ValueError("Event dates must define an increasing range")
            self._events.append((name, start, end))
        self.areas, self._labels, self._markers, self._event_items = {}, {}, {}, []
        self._last_frame = None
        super().__init__(canvas=canvas, df=df, **kwargs)

    def draw(self, time):
        if self.areas:
            return
        for i, name in enumerate(self.df.columns):
            if name not in self.colors:
                palette = getattr(self.sjcanvas, "color_palette", None)
                self.colors[name] = palette.pop(0) if palette else color_palette[i % len(color_palette)]
            color = from_rgb(self.colors[name])
            self.areas[name] = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill=color, outline="")
            if self.display_legend:
                lx = self.x_pos + self.width + 20 if self.external_legend else self.x_pos + 15
                rendered_font_size = tk_font_size(self.font_size)
                self._labels[name] = self.canvas.create_text(lx, self.y_pos+i*(rendered_font_size+8),
                    anchor="nw", fill=color, font=(self.text_font, rendered_font_size))
                if self.label_position == "right":
                    self.canvas.itemconfig(self._labels[name], anchor="w")
                if self.label_position == "area":
                    rgb = np.asarray(self.colors[name], dtype=float) / 255
                    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
                    luminance = float(linear @ [.2126, .7152, .0722])
                    self.canvas.itemconfig(self._labels[name], anchor="center",
                                           fill="black" if luminance > .179 else "white")
            if self.draw_points:
                self._markers[name] = self.canvas.create_oval(0, 0, 0, 0, fill=color, outline=from_rgb(self.font_color))
        for name, _, _ in self._events:
            self._event_items.append((
                self.canvas.create_rectangle(0, 0, 0, 0, fill=from_rgb(self.event_color), stipple="gray25", outline="", state="hidden"),
                self.canvas.create_text(0, 0, text=name, anchor="s", fill=from_rgb(self.font_color),
                                        font=(self.text_font, tk_font_size(self.font_size)), state="hidden")))
        common = dict(canvas=self.canvas, x=self.x_pos, y=self.y_pos+self.height,
                      font_size=self.font_size, text_font=self.text_font,
                      color=self.font_color, ticks_only=False, allow_decrease=True)
        self.axis1 = axis(**common, length=self.width, orientation="horizontal", n=self.x_ticks,
                          is_date=True, time_indicator=self.time_indicator)
        self.axis2 = axis(**common, length=self.height, width=self.width, orientation="vertical",
                          n=self.y_ticks, unit=self.unit, decimal_places=self.decimal_places)
        self.axis1.draw(self.df.index[0], self.df.index[0])
        self.axis2.draw(0, 1)
        self.update(time)

    def update(self, time):
        pos = 0 if time is None else self.df.index.get_loc(time)
        if pos == self._last_frame:
            return
        self.axis1.update(self.df.index[0], self.df.index[pos])
        self.axis2.update(0, max(1, self._maxima[pos]))
        count = pos + 1
        indices = np.arange(count) if self.max_points is None or count <= self.max_points else np.linspace(0, pos, self.max_points, dtype=int)
        if len(indices) == 1:
            indices = np.repeat(indices, 2)
        # Seconds preserve intraday geometry despite legacy date tick formatting.
        elapsed = self._times[pos]
        xs = self.x_pos + self.width * self._times[indices] / (elapsed or 1)
        tops = self._tops[indices]
        for i, name in enumerate(self.df.columns):
            bottom = tops[:, i+1] if i+1 < tops.shape[1] else np.zeros(len(indices))
            top_y = self.y_pos+self.height-self.axis2.calc_positions_many(tops[:, i])
            bottom_y = self.y_pos+self.height-self.axis2.calc_positions_many(bottom)
            coords = np.concatenate((np.column_stack((xs, top_y)), np.column_stack((xs[::-1], bottom_y[::-1])))).ravel()
            self.canvas.coords(self.areas[name], *coords.tolist())
            if name in self._labels:
                text = str(name)
                if self.display_values:
                    text += f"  {self._values[pos, i]:,.{self.decimal_places}f}{self.unit}"
                self.canvas.itemconfig(self._labels[name], text=text)
                label_visible = self._label_value_is_visible(self._values[pos, i])
                if not label_visible:
                    self.canvas.itemconfig(self._labels[name], state="hidden")
                elif self.label_position == "area":
                    self._position_area_label(self._labels[name], xs, top_y, bottom_y, elapsed)
                elif self.label_position == "right":
                    self.canvas.coords(self._labels[name], self.x_pos+self.width+10,
                                       (top_y[-1]+bottom_y[-1])/2)
                    self.canvas.itemconfig(self._labels[name], state="normal")
                else:
                    self.canvas.itemconfig(self._labels[name], state="normal")
                self.canvas.tag_raise(self._labels[name])
            if name in self._markers:
                self.canvas.coords(self._markers[name], xs[-1]-3, top_y[-1]-3, xs[-1]+3, top_y[-1]+3)
                self.canvas.tag_raise(self._markers[name])
        now, first = self.df.index[pos], self.df.index[0]
        for (_, start, end), (rect, label) in zip(self._events, self._event_items):
            visible = elapsed > 0 and start <= now and end >= first
            self.canvas.itemconfig(rect, state="normal" if visible else "hidden")
            self.canvas.itemconfig(label, state="normal" if visible and (self.draw_all_events or now <= end) else "hidden")
            if visible:
                left = self.x_pos + self.width * (max(first, start)-first).total_seconds()/elapsed
                right = self.x_pos + self.width * (min(now, end)-first).total_seconds()/elapsed
                self.canvas.coords(rect, left, self.y_pos, right, self.y_pos+self.height)
                self.canvas.coords(label, (left+right)/2, self.y_pos-5)
        self._last_frame = pos

    def _label_value_is_visible(self, value):
        """Return whether a current value is meaningful at display precision."""
        threshold = self.label_min_value
        if threshold is None:
            threshold = 0.5 * 10 ** (-self.decimal_places)
        return bool(np.isfinite(value) and value > threshold)

    def _position_area_label(self, label, xs, top_y, bottom_y, elapsed):
        """Fit the label inside the actual sampled polygon, including its width."""
        cx = self.x_pos + self.width / 2
        cy = (np.interp(cx, xs, top_y) + np.interp(cx, xs, bottom_y)) / 2
        self.canvas.coords(label, cx, cy)
        # Show before measuring: Tk reports no bbox for hidden canvas items.
        self.canvas.itemconfig(label, state="normal")
        box = self.canvas.bbox(label)
        if box is None:
            self.canvas.itemconfig(label, state="hidden")
            return
        left, upper, right, lower = box
        samples = np.concatenate(([left, right], xs[(xs > left) & (xs < right)]))
        fits = (elapsed > 0 and left >= xs[0] and right <= xs[-1]
                and upper >= np.max(np.interp(samples, xs, top_y)) + 2
                and lower <= np.min(np.interp(samples, xs, bottom_y)) - 2)
        self.canvas.itemconfig(label, state="normal" if fits else "hidden")


# The unfinished legacy AreaPlot now uses the complete stacked implementation.
area_plot = area_chart
