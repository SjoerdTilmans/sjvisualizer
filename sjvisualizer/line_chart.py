"""Animated line chart.

This module implements an animated multi-series line chart.

Two x-axis modes are supported:

1) Date x-axis (default)
   - The animation "time" (dataframe index) is used as x.
   - The x-axis is rendered as a date axis via :class:`sjvisualizer.core.axis.axis`.

2) Numeric x-axis (optional)
   - Provide ``x_df`` (a second dataframe/series) holding the x-values.
   - The animation time still comes from the dataframe index, but the x-position
     of each point is taken from ``x_df`` at the same frame.

Typical usage (date x-axis)
---------------------------

.. code-block:: python

    import datetime as dt
    import numpy as np
    import pandas as pd
    from sjvisualizer import Canvas, LineChart

    idx = [dt.datetime(2000, 1, 1) + dt.timedelta(days=i) for i in range(120)]
    df = pd.DataFrame(
        {"A": np.linspace(0, 100, len(idx)), "B": np.linspace(50, 10, len(idx))},
        index=idx,
    )

    cv = Canvas.canvas()
    chart = LineChart.line_chart(df=df, canvas=cv, width=1400, height=800, x_pos=100, y_pos=150)
    cv.add_sub_plot(chart)
    cv.play(df=df, fps=60, record=False)

Typical usage (numeric x-axis)
------------------------------

.. code-block:: python

    import datetime as dt
    import numpy as np
    import pandas as pd
    from sjvisualizer import Canvas, LineChart

    idx = [dt.datetime(2000, 1, 1) + dt.timedelta(days=i) for i in range(120)]
    df_y = pd.DataFrame(
        {"A": np.linspace(0, 100, len(idx)), "B": np.linspace(50, 10, len(idx))},
        index=idx,
    )
    # x-values per series (same index, same columns)
    df_x = pd.DataFrame(
        {"A": np.linspace(0, 1, len(idx)) ** 2, "B": np.linspace(0, 1, len(idx))},
        index=idx,
    )

    cv = Canvas.canvas()
    chart = LineChart.line_chart(df=df_y, x_df=df_x, canvas=cv, width=1400, height=800, x_pos=100, y_pos=150)
    cv.add_sub_plot(chart)
    cv.play(df=df_y, fps=60, record=False)
"""

from __future__ import annotations

import datetime
import random
from dataclasses import dataclass
from tkinter import font
from typing import Any, Dict, Mapping

import pandas as pd

from ..core.axis import axis
from ..core.subplot import sub_plot
from ..utils.colors import from_rgb, min_color, max_color
from ..utils.scaling import HEIGHT, WIDTH, SCALEFACTOR

MAX_POINTS = 100


def _to_days_since_1800(dt: datetime.datetime) -> int:
    """Convert a datetime into integer days since 1800-01-01 (legacy date axis convention)."""
    return (dt - datetime.datetime(1800, 1, 1)).days


@dataclass
class _AxisConfig:
    x_ticks: int = 8
    y_ticks: int = 5
    axis_line_width: int = 3
    tick_prefix: str = ""
    unit: str = ""
    x_decimal_places: int = 0
    y_decimal_places: int = 0
    y_zero_based: bool = True


class line_chart(sub_plot):
    """Animated multi-series line chart.

    Parameters
    ----------
    df:
        Time-indexed dataframe containing the **y-values**.
        Each column is a series/category.
    x_df:
        Optional x-values. May be:

        - ``None``: use a date x-axis from ``df.index`` (default).
        - ``pd.Series``: one shared x-value per frame (applied to all series).
        - ``pd.DataFrame``: x-values per series and/or shared. If the dataframe
          contains the same columns as ``df``, those are used. Otherwise, a
          single column (``x_column`` or the first column) is used for all series.
    x_column:
        When ``x_df`` is a dataframe that does **not** contain the same columns as
        ``df``, this selects which column to use as the shared x-value.
        If omitted, the first column is used.
    draw_points:
        Draw circular markers at each point (may impact performance).
    time_indicator:
        Date tick formatting for date x-axes. Common values: ``"year"``, ``"month"``, ``"day"``.
        Only used when ``x_df is None``.
    events:
        Optional dict defining shaded time ranges for date x-axis mode only.
        Same structure as legacy SJVisualizer line chart.
    draw_all_events:
        If ``True``, keep labels for all events. If ``False``, only the most
        recent active event keeps a label.
    line_width:
        Explicit line width (pixels). If omitted, derived from subplot height.
    label_at_end:
        If ``True`` draw series labels at the most recent point.
    avoid_label_overlap:
        If ``True`` (default) the end labels are laid out using a smooth
        overlap-avoidance routine so labels do not cover each other. When
        two lines overtake each other, labels smoothly swap places.
    label_min_separation:
        Minimum vertical separation between end labels in pixels.
        If omitted, it is derived from the font line height.
    label_padding:
        Extra padding (pixels) added on top of ``label_min_separation``.
    label_relax_iterations:
        Number of relaxation iterations per frame used to resolve label
        collisions (higher is more strict but slightly slower).
    label_relax_strength:
        How strongly labels move toward their desired y-position per
        iteration (0..1). Lower values are smoother.
    y_lims:
        Optional fixed y-axis limits: ``(ymin, ymax)``.
    x_lims:
        Optional fixed numeric x-axis limits: ``(xmin, xmax)`` (only when ``x_df`` is given).
    x_ticks, y_ticks:
        Number of ticks to render on each axis.
    axis_line_width:
        Axis/tick line thickness.
    x_decimal_places, y_decimal_places:
        Decimal places for tick labels.
    y_zero_based:
        If ``True`` and y-values are non-negative, the y-axis is clamped to start at 0.
    tick_prefix, unit:
        Prefix/unit appended to y-axis tick labels.
    start_time:
        Optional initial frame time (must exist in ``df.index`` or be convertible).
        If omitted, the first index value is used.

    Notes
    -----
    - Date x-axes use a legacy "days since 1800-01-01" internal representation
      for positions, as used by other SJVisualizer charts and :class:`axis`.
    - For numeric x-axes, the animation still progresses over ``df.index``; only
      x-positions are taken from ``x_df``.
    """

    def __init__(
        self,
        df: pd.DataFrame | None = None,
        x_df: pd.DataFrame | pd.Series | None = None,
        x_column: str | None = None,
        canvas=None,
        *,
        # generic subplot params
        x_pos=None,
        y_pos=None,
        width=None,
        height=None,
        colors: dict | None = None,
        root=None,
        anchor="c",
        title: str | None = None,
        font_color=(0, 0, 0),
        back_ground_color=(255, 255, 255),
        font_size: int | None = None,
        text_font: str = "Microsoft JhengHei UI",
        # chart-specific params
        draw_points: bool = True,
        time_indicator: str = "year",
        events: dict | None = None,
        event_color=(225, 225, 225),
        draw_all_events: bool = False,
        line_width: int | None = None,
        label_at_end: bool = True,
        avoid_label_overlap: bool = True,
        label_min_separation: int | None = None,
        label_padding: int = 2,
        label_relax_iterations: int = 14,
        label_relax_strength: float = 0.18,
        y_lims: tuple[float, float] | None = None,
        x_lims: tuple[float, float] | None = None,
        x_ticks: int = 8,
        y_ticks: int = 5,
        axis_line_width: int = 3,
        x_decimal_places: int = 0,
        y_decimal_places: int = 0,
        y_zero_based: bool = True,
        tick_prefix: str = "",
        unit: str = "",
        start_time: datetime.datetime | None = None,
        **kwargs: Any,
    ):
        if df is None:
            raise ValueError("line_chart requires df (y-values).")

        # If not provided, pick a sensible font size relative to chart height.
        if font_size is None:
            # keep similar scale as legacy: height/33
            if height is None:
                height = int(HEIGHT / 2)
            font_size = int(height / 33)

        super().__init__(
            canvas=canvas,
            width=width if width is not None else int(WIDTH * 0.7),
            height=height if height is not None else int(HEIGHT * 0.6),
            x_pos=x_pos,
            y_pos=y_pos,
            colors=colors if colors is not None else {},
            root=root,
            anchor=anchor,
            title=title,
            font_color=font_color,
            back_ground_color=back_ground_color,
            font_size=int(font_size),
            text_font=text_font,
            **kwargs,
        )

        self.df: pd.DataFrame = df
        self.df_x = x_df  # used by canvas.play fallback
        self.x_column = x_column

        self.draw_points = bool(draw_points)
        self.time_indicator = time_indicator
        self.events: dict = events or {}
        self.event_color = event_color
        self.draw_all_events = bool(draw_all_events)
        self.line_width = line_width
        self.label_at_end = bool(label_at_end)
        self.avoid_label_overlap = bool(avoid_label_overlap)
        self.label_min_separation = label_min_separation
        self.label_padding = int(label_padding)
        self.label_relax_iterations = int(label_relax_iterations)
        self.label_relax_strength = float(label_relax_strength)
        self.y_lims = y_lims
        self.x_lims = x_lims

        self._axis_cfg = _AxisConfig(
            x_ticks=int(x_ticks),
            y_ticks=int(y_ticks),
            axis_line_width=int(axis_line_width),
            tick_prefix=str(tick_prefix or ""),
            unit=str(unit or ""),
            x_decimal_places=int(x_decimal_places),
            y_decimal_places=int(y_decimal_places),
            y_zero_based=bool(y_zero_based),
        )

        # Ensure a valid `start_time` for the initial draw (used by Canvas.add_sub_plot).
        if start_time is None or (hasattr(pd, "isna") and pd.isna(start_time)):
            try:
                start_time = df.index[0]
            except Exception:
                start_time = None
        self.start_time = start_time
        self._x_is_date = (self.df_x is None)
        self._min_time: datetime.datetime | None = None
        self._max_time: datetime.datetime | None = None

        self.axis_x: axis | None = None
        self.axis_y: axis | None = None
        self.lines: dict[str, _Line] = {}
        self._events: list[_Event] = []

    def _layout_end_labels(self):
        """Lay out end labels to avoid overlap while remaining smooth.

        This uses a small relaxation loop:
        - each label moves partway toward its desired y
        - overlapping neighbors are pushed apart
        - labels are clamped into the plot bounds

        The result is stable (no abrupt jumps) and ensures labels do not
        overlap while allowing smooth swapping when lines overtake.
        """

        if not self.label_at_end or not self.avoid_label_overlap:
            return
        if not self.lines:
            return

        # Collect label-enabled series that have a desired position.
        active: list[_Line] = [
            l
            for l in self.lines.values()
            if l.label_at_end and l.label_id is not None and l.desired_label_y is not None
        ]
        if len(active) <= 1:
            # Nothing to collide with.
            for l in active:
                l.apply_label_direct()
            return

        # Font line height -> minimum separation.
        try:
            line_h = int(self._font.metrics("linespace"))
        except Exception:
            line_h = max(10, int(self.font_size / SCALEFACTOR))

        min_sep = int(self.label_min_separation) if self.label_min_separation is not None else int(line_h * 1.05)
        min_sep = max(6, min_sep + self.label_padding)

        # Labels use anchor="w" (left-center), so y is the center.
        min_y = self.y_pos + line_h / 2
        max_y = self.y_pos + self.height - line_h / 2

        # If there are too many labels to fit at the requested separation,
        # shrink separation to the maximum feasible value.
        available = max(1.0, float(max_y - min_y))
        if len(active) > 1:
            feasible = available / float(len(active) - 1)
            if float(min_sep) > feasible:
                min_sep = max(1, int(feasible))

        # Initialize current y to last drawn y (or desired if first frame).
        for l in active:
            if not l.label_drawn:
                l._label_y = float(l.desired_label_y)
                l.label_drawn = True

        # Relaxation loop on the *current* y positions to keep things smooth.
        alpha = max(0.02, min(0.8, self.label_relax_strength))
        iters = max(1, self.label_relax_iterations)

        for _ in range(iters):
            # 1) pull each label gently toward its desired y
            for l in active:
                l._label_y += alpha * (float(l.desired_label_y) - float(l._label_y))

            # 2) push overlapping neighbors apart
            active.sort(key=lambda li: float(li._label_y))
            for i in range(1, len(active)):
                prev = active[i - 1]
                cur = active[i]
                dy = float(cur._label_y) - float(prev._label_y)
                if dy < min_sep:
                    push = (min_sep - dy) / 2.0
                    prev._label_y -= push
                    cur._label_y += push

            # 3) clamp into bounds (shift group to preserve spacing)
            active.sort(key=lambda li: float(li._label_y))
            if float(active[0]._label_y) < min_y:
                shift = min_y - float(active[0]._label_y)
                for l in active:
                    l._label_y += shift
            if float(active[-1]._label_y) > max_y:
                shift = float(active[-1]._label_y) - max_y
                for l in active:
                    l._label_y -= shift

        # Final strict pass to guarantee non-overlap and bounds.
        active.sort(key=lambda li: float(li._label_y))
        active[0]._label_y = max(min_y, min(max_y, float(active[0]._label_y)))
        for i in range(1, len(active)):
            active[i]._label_y = max(float(active[i]._label_y), float(active[i - 1]._label_y) + min_sep)
        if float(active[-1]._label_y) > max_y:
            shift = float(active[-1]._label_y) - max_y
            for l in active:
                l._label_y -= shift
            active[0]._label_y = max(min_y, float(active[0]._label_y))
            for i in range(1, len(active)):
                active[i]._label_y = max(float(active[i]._label_y), float(active[i - 1]._label_y) + min_sep)

        # Apply label coords.
        for l in active:
            l.apply_label_from_layout()

    # ---- helpers

    def _get_y_series(self, time_obj: datetime.datetime) -> pd.Series:
        row = self._get_data_for_frame(time_obj, df=self.df)
        if isinstance(row, pd.Series):
            return row
        # If the dataframe has a single column, loc can return scalar; normalize.
        return pd.Series(row, index=self.df.columns)

    def _get_x_for_frame(self, time_obj: datetime.datetime, y_columns: list[str]) -> Dict[str, float]:
        """Return x-values per series for the current frame."""
        if self.df_x is None:
            v = float(_to_days_since_1800(time_obj))
            return {c: v for c in y_columns}

        if isinstance(self.df_x, pd.Series):
            v = float(self.df_x.loc[time_obj])
            return {c: v for c in y_columns}

        # DataFrame case
        x_row = self._get_data_for_frame(time_obj, df=self.df_x)
        if not isinstance(x_row, pd.Series):
            # scalar
            v = float(x_row)
            return {c: v for c in y_columns}

        # 1) per-series columns exist
        if all(c in x_row.index for c in y_columns):
            return {c: float(x_row[c]) for c in y_columns}

        # 2) shared single column requested / fallback
        col = self.x_column
        if col and col in x_row.index:
            v = float(x_row[col])
            return {c: v for c in y_columns}

        # 3) fallback to first value
        if len(x_row.index) > 0:
            v = float(x_row.iloc[0])
            return {c: v for c in y_columns}

        # degenerate
        return {c: 0.0 for c in y_columns}

    def _pick_color(self, name: str) -> str:
        if isinstance(self.colors, dict) and name in self.colors:
            return from_rgb(self.colors[name])
        # Use canvas palette first (legacy behavior)
        if getattr(self, "sjcanvas", None) is not None and getattr(self.sjcanvas, "color_palette", None):
            rgb = self.sjcanvas.color_palette.pop(0)
        else:
            rgb = (
                random.randint(min_color, max_color),
                random.randint(min_color, max_color),
                random.randint(min_color, max_color),
            )
        if isinstance(self.colors, dict):
            self.colors[name] = rgb
        return from_rgb(rgb)

    # ---- drawing

    def draw(self, time=None):
        self._x_is_date = (self.df_x is None)

        # Effective font size (respect DPI scaling)
        self._font_px = max(8, int(self.font_size / SCALEFACTOR))
        self._font = font.Font(family=self.text_font, size=int(self._font_px))

        y_series = self._get_y_series(time)
        cols = list(self.df.columns)
        x_values = self._get_x_for_frame(time, cols)

        # --- X axis
        if self._x_is_date:
            self._min_time = time
            self._max_time = time
            self.axis_x = axis(
                canvas=self.canvas,
                x=self.x_pos,
                y=self.y_pos + self.height,
                length=self.width,
                orientation="horizontal",
                n=self._axis_cfg.x_ticks,
                allow_decrease=False,
                is_date=True,
                time_indicator=self.time_indicator,
                font_size=self._font_px,
                text_font=self.text_font,
                color=self.font_color,
                line_tickness=self._axis_cfg.axis_line_width,
                ticks_only=False,
                decimal_places=self._axis_cfg.x_decimal_places,
            )
            self.axis_x.draw(min_val=self._min_time, max_val=self._max_time)
        else:
            xs = [x_values[c] for c in cols]
            x_min = min(xs) if xs else 0.0
            x_max = max(xs) if xs else 1.0
            if self.x_lims:
                x_min, x_max = self.x_lims
            self.axis_x = axis(
                canvas=self.canvas,
                x=self.x_pos,
                y=self.y_pos + self.height,
                length=self.width,
                orientation="horizontal",
                n=self._axis_cfg.x_ticks,
                allow_decrease=False,
                is_date=False,
                font_size=self._font_px,
                text_font=self.text_font,
                color=self.font_color,
                line_tickness=self._axis_cfg.axis_line_width,
                ticks_only=False,
                decimal_places=self._axis_cfg.x_decimal_places,
            )
            self.axis_x.draw(min_val=x_min, max_val=x_max)

        # --- Y axis
        vals = [float(v) for v in y_series.values] if len(y_series.values) else [0.0]
        y_min = min(vals)
        y_max = max(vals)
        if self.y_lims:
            y_min, y_max = self.y_lims

        self.axis_y = axis(
            canvas=self.canvas,
            x=self.x_pos,
            y=self.y_pos + self.height,
            length=self.height,
            width=self.width,
            orientation="vertical",
            n=self._axis_cfg.y_ticks,
            allow_decrease=False,
            is_date=False,
            font_size=self._font_px,
            text_font=self.text_font,
            color=self.font_color,
            line_tickness=self._axis_cfg.axis_line_width,
            ticks_only=False,
            decimal_places=self._axis_cfg.y_decimal_places,
            unit=self._axis_cfg.unit,
            tick_prefix=self._axis_cfg.tick_prefix,
            zero_based=self._axis_cfg.y_zero_based,
        )
        self.axis_y.draw(min_val=y_min, max_val=y_max)

        # --- series lines
        for name in cols:
            color = self._pick_color(name)
            self.lines[name] = _Line(
                name=name,
                canvas=self.canvas,
                chart=self,
                color=color,
                xaxis=self.axis_x,
                yaxis=self.axis_y,
                draw_points=self.draw_points,
                line_width=self.line_width,
                label_at_end=self.label_at_end,
                font=self._font,
            )
            yv = float(y_series.get(name, 0.0))
            xv = float(x_values.get(name, 0.0))
            self.lines[name].seed(x=xv, y=yv, time_obj=time, x_is_date=self._x_is_date)

        # --- events (date mode only)
        self._events = []
        if self._x_is_date and self.events:
            for key, cfg in self.events.items():
                try:
                    start_date = cfg.get("start_date")
                    end_date = cfg.get("end_date")
                    if not start_date or not end_date:
                        continue
                    color = cfg.get("color", self.event_color)
                    label = cfg.get("label", key)
                    self._events.append(
                        _Event(
                            name=label,
                            canvas=self.canvas,
                            parent=self,
                            start_date=start_date,
                            end_date=end_date,
                            event_color=color,
                            font=self._font,
                            font_color=self.font_color,
                        )
                    )
                except Exception:
                    # keep chart running if an event config is malformed
                    continue

    def update(self, time: datetime.datetime):
        y_series = self._get_y_series(time)
        cols = list(self.df.columns)
        x_values = self._get_x_for_frame(time, cols)

        # Update axes
        if self.axis_x is None or self.axis_y is None:
            return

        if self._x_is_date:
            if self._min_time is None:
                self._min_time = time
            self._max_time = time
            self.axis_x.update(min_val=self._min_time, max_val=self._max_time)
        else:
            xs = [x_values[c] for c in cols] if cols else [0.0]
            x_min = min(xs) if xs else 0.0
            x_max = max(xs) if xs else 1.0
            if self.x_lims:
                x_min, x_max = self.x_lims
            self.axis_x.update(min_val=x_min, max_val=x_max)

        vals = [float(v) for v in y_series.values] if len(y_series.values) else [0.0]
        y_min = min(vals)
        y_max = max(vals)
        if self.y_lims:
            y_min, y_max = self.y_lims
        self.axis_y.update(min_val=y_min, max_val=y_max)

        # update line points (performance guard for markers)
        if self.draw_points:
            total_points = sum(len(l.points) for l in self.lines.values())

        for name in cols:
            yv = float(y_series.get(name, 0.0))
            xv = float(x_values.get(name, 0.0))
            line_obj = self.lines.get(name)
            if not line_obj:
                continue

            if self.draw_points:
                # degrade markers when too many points exist
                if total_points > MAX_POINTS and line_obj.point_radius > 0:
                    line_obj.point_radius -= 0.25
                if line_obj.point_radius <= 0:
                    line_obj.remove_points()

            line_obj.update(x=xv, y=yv, time_obj=time, x_is_date=self._x_is_date)

        # Lay out end labels (collision-free) after all series have computed their desired positions.
        self._layout_end_labels()

        # events (date only)
        if self._x_is_date and self._events:
            for e in self._events:
                if self.draw_all_events:
                    e.draw_label = True
                e.update(time)


class _Event:
    """Shaded time-range overlay for date x-axes."""

    def __init__(
        self,
        name: str,
        canvas,
        parent: line_chart,
        start_date: str,
        end_date: str,
        event_color=(200, 200, 200),
        font: font.Font | None = None,
        font_color=(0, 0, 0),
    ):
        self.name = name
        self.canvas = canvas
        self.parent = parent

        # Legacy format: "dd/mm/YYYY"
        self.start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
        self.end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")

        self.fill = from_rgb(event_color)
        self.font_color = font_color
        self.font = font or font.Font(family="Microsoft JhengHei UI", size=12)

        self.drawn = False
        self.draw_label = False

        self.rect = self.canvas.create_rectangle(-1000, -1000, -1000, -1000, fill=self.fill, outline="")
        self.label = self.canvas.create_text(-1000, -1000, text=self.name, font=self.font, fill=from_rgb(self.font_color), anchor="s")

    def update(self, date: datetime.datetime):
        if self.parent.axis_x is None:
            return

        if date <= self.start_date:
            return

        if not self.drawn:
            self.drawn = True
            # Only the most recent event shows a label unless draw_all_events
            for e in getattr(self.parent, "_events", []):
                e.draw_label = False
            if self.end_date > (self.parent._min_time or self.start_date):
                self.draw_label = True

        # convert to "days since 1800"
        start_days = _to_days_since_1800(self.start_date)
        end_days = _to_days_since_1800(self.end_date)
        cur_days = _to_days_since_1800(date)

        pos1 = self.parent.x_pos + self.parent.axis_x.calc_positions(start_days)
        pos2_days = cur_days if self.end_date > date else end_days
        pos2 = self.parent.x_pos + self.parent.axis_x.calc_positions(pos2_days)

        # clamp to chart area
        pos1 = max(pos1, self.parent.x_pos)
        pos2 = max(pos2, self.parent.x_pos)

        # rect spans full plot height
        self.canvas.coords(self.rect, pos1, self.parent.y_pos, pos2, self.parent.y_pos + self.parent.height)

        if self.draw_label:
            x = self._calc_label_x_pos(pos1, pos2)
            self.canvas.itemconfig(self.label, text=self.name)
            self.canvas.coords(self.label, x, self.parent.y_pos - 3)
        else:
            self.canvas.itemconfig(self.label, text="")

    def _calc_label_x_pos(self, pos1: float, pos2: float) -> float:
        try:
            bbox = self.canvas.bbox(self.label)
            text_width = (bbox[2] - bbox[0]) if bbox else 0
        except Exception:
            text_width = 0

        center = (pos1 + pos2) / 2
        if center + text_width / 2 > self.parent.x_pos + self.parent.width:
            self.canvas.itemconfig(self.label, anchor="se")
            return self.parent.x_pos + self.parent.width
        if center - text_width / 2 < self.parent.x_pos:
            self.canvas.itemconfig(self.label, anchor="sw")
            return self.parent.x_pos
        self.canvas.itemconfig(self.label, anchor="s")
        return center


class _Line:
    """One series in the line chart (keeps a history of points)."""

    def __init__(
        self,
        name: str,
        canvas,
        chart: line_chart,
        color: str,
        xaxis: axis,
        yaxis: axis,
        draw_points: bool,
        line_width: int | None,
        label_at_end: bool,
        font: font.Font,
    ):
        self.name = name
        self.canvas = canvas
        self.chart = chart
        self.color = color
        self.xaxis = xaxis
        self.yaxis = yaxis

        self.draw_points = bool(draw_points)
        self.point_radius = float(int(2 + self.chart.height / 150))
        self.label_at_end = bool(label_at_end)

        self.line_width = int(1 + self.chart.height / 200) if not line_width else int(line_width)

        self.x_values: list[float] = []
        self.y_values: list[float] = []

        self.line_id = None
        self.points: list[int] = []

        self.label_drawn = False
        self._label_y = 0.0
        self._v = 0.0
        self._a = 0.0
        self._m = 2.0
        self._k = 0.5
        self._d = 2.4

        # Desired label position at the end of the line (computed each frame)
        self.desired_label_x: float | None = None
        self.desired_label_y: float | None = None

        self.label_id = None
        self.font = font
        if self.label_at_end:
            self.label_id = self.canvas.create_text(-10000, -10000, text=self.name, font=self.font, fill=self.color, anchor="w")

    def seed(self, x: float, y: float, time_obj: datetime.datetime, x_is_date: bool):
        # Store an initial point so first update can draw a segment.
        if x_is_date:
            self.x_values.append(float(_to_days_since_1800(time_obj)))
        else:
            self.x_values.append(float(x))
        self.y_values.append(float(y))

    def update(self, x: float, y: float, time_obj: datetime.datetime, x_is_date: bool):
        # Append "anchor" points occasionally to build a tail.
        if time_obj.hour == 0 and time_obj.minute == 0 and time_obj.second == 0:
            self.x_values.append(float(_to_days_since_1800(time_obj)) if x_is_date else float(x))
            self.y_values.append(float(y))

        # Draw with history + current point
        xs = self.x_values.copy()
        ys = self.y_values.copy()

        xs.append(float(_to_days_since_1800(time_obj)) if x_is_date else float(x))
        ys.append(float(y))

        coords: list[float] = []
        for i, (xv, yv) in enumerate(zip(xs, ys)):
            px = self.chart.x_pos + self.xaxis.calc_positions(xv)
            py = self.chart.y_pos + self.chart.height - self.yaxis.calc_positions(yv)
            coords.extend([px, py])

            if self.draw_points:
                try:
                    self.canvas.coords(
                        self.points[i],
                        px - self.point_radius,
                        py - self.point_radius,
                        px + self.point_radius,
                        py + self.point_radius,
                    )
                except IndexError:
                    self.points.append(
                        self.canvas.create_oval(
                            px - self.point_radius,
                            py - self.point_radius,
                            px + self.point_radius,
                            py + self.point_radius,
                            fill=self.color,
                            outline="",
                        )
                    )

        if len(coords) == 2:
            coords = coords + coords

        if self.line_id is None:
            if coords:
                self.line_id = self.canvas.create_line(*coords, width=self.line_width, fill=self.color)
        else:
            self.canvas.coords(self.line_id, *coords)

        # label follow the last point (with a little spring motion)
        if not self.label_at_end or self.label_id is None:
            return

        if coords:
            target_x, target_y = coords[-2], coords[-1]
            # Store desired position; the chart may apply overlap-avoidance.
            self.desired_label_x = float(target_x + 10)
            self.desired_label_y = float(target_y)

            if self.chart.avoid_label_overlap:
                # Defer positioning to chart-level layout.
                return

            # Legacy per-label spring (no overlap avoidance)
            if not self.label_drawn:
                self._label_y = target_y
                self.canvas.coords(self.label_id, target_x + 10, target_y)
                self.label_drawn = True
            else:
                F = self._k * (target_y - self._label_y) - self._d * self._v
                self._a = F / self._m
                self._v = self._v + self._a
                self._label_y = self._label_y + self._v
                self.canvas.coords(self.label_id, target_x + 10, self._label_y)
        else:
            self.canvas.coords(self.label_id, -1000, -1000)
            self.label_drawn = False
            self.desired_label_x = None
            self.desired_label_y = None

    def apply_label_direct(self):
        """Apply label directly at its desired position (no overlap handling needed)."""
        if self.label_id is None or self.desired_label_x is None or self.desired_label_y is None:
            return
        self._label_y = float(self.desired_label_y)
        self.canvas.coords(self.label_id, float(self.desired_label_x), float(self._label_y))
        self.label_drawn = True

    def apply_label_from_layout(self):
        """Apply label at the current layout y-position."""
        if self.label_id is None or self.desired_label_x is None:
            return
        self.canvas.coords(self.label_id, float(self.desired_label_x), float(self._label_y))
        self.label_drawn = True

    def remove_points(self):
        for p in self.points:
            try:
                self.canvas.delete(p)
            except Exception:
                pass
        self.points = []
        self.draw_points = False
