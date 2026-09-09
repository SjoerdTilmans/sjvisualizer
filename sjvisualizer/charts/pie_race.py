"""Animated pie/donut chart using persistent canvas items.

Use ``from sjvisualizer import PieRace`` then ``PieRace.pie_plot(df=df,
canvas=cv)`` and register it with ``cv.add_sub_plot(chart)``.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from ..core.subplot import sub_plot
from ..utils.colors import color_palette, from_rgb
from ..utils.scaling import tk_font_size

__all__ = ["pie_plot"]


class pie_plot(sub_plot):
    """Animate category shares in a time-indexed dataframe.

    Common positioning and styling options are inherited from ``sub_plot``.
    ``sort=True`` orders categories by their current value (stable for ties).
    Shares at or below ``min_slice`` (default 0.02), plus explicit ``Other``
    and ``Others`` columns, are combined into an ``Other`` slice.
    Negative, missing and non-finite values count as zero. Empty frames hide
    all slices. Column names and frame indices must be unique.

    ``inner_radius`` is the hole/outer-radius ratio; use 0 for a solid pie.
    ``smoothing`` is the per-frame interpolation factor in (0, 1]; 1 tracks
    the data exactly. Sizes and sorted slice positions interpolate without
    overshoot, including when ranks change mid-transition. Slices may overlap
    temporarily as they pass each other, as in the legacy chart. Exposed edges
    extend to the next moving slice so transitions never uncover the background.
    Percentages retain the interpolated data shares; once settled, wedges return
    to those exact proportions. Use ``sort=False`` for fixed category order and
    contiguous slices throughout size changes.
    Subpixel wedges are hidden, with their space covered by neighboring slices.
    ``display_label`` and ``display_percentages`` work independently.
    Optional PNG icons in ``assets_dir`` are loaded once per category at a
    fixed size, lazily when first visible. Set ``display_images=False`` to
    disable them. ``min_percentage`` controls percentage/icon visibility.
    """

    def __init__(self, df=None, canvas=None, *, sort=True,
                 display_label=True, display_percentages=True,
                 display_images=True, assets_dir="assets", min_slice=0.02,
                 min_percentage=0.055, inner_radius=0.5, smoothing=0.2,
                 decimal_places=2, start_time=None, **kwargs):
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("pie_plot requires a non-empty pandas.DataFrame")
        if not df.columns.is_unique or not df.index.is_unique:
            raise ValueError("pie_plot requires unique columns and index")
        for name, value in (("min_slice", min_slice),
                            ("min_percentage", min_percentage),
                            ("inner_radius", inner_radius)):
            if not math.isfinite(value) or not 0 <= value < 1:
                raise ValueError(f"{name} must be in [0, 1)")
        if not math.isfinite(smoothing) or not 0 < smoothing <= 1:
            raise ValueError("smoothing must be in (0, 1]")
        if not isinstance(decimal_places, int) or decimal_places < 0:
            raise ValueError("decimal_places must be a non-negative integer")
        self.df = df
        self.start_time = df.index[0] if start_time is None else start_time
        self.sort = sort
        self.display_label = display_label
        self.display_percentages = display_percentages
        self.display_images = display_images
        self.assets_dir = Path(assets_dir)
        self.min_slice = min_slice
        self.min_percentage = min_percentage
        self.inner_radius = inner_radius
        self.smoothing = smoothing
        self.decimal_places = decimal_places
        self.pies = {}
        self._shares = {}
        self._starts = {}
        self._order = []
        self.white = None
        super().__init__(canvas=canvas, **kwargs)

    def _targets(self, time_obj):
        data = pd.to_numeric(self._get_data_for_frame(time_obj), errors="coerce")
        values = data.to_numpy(dtype=float, na_value=0).copy()
        values[~np.isfinite(values) | (values < 0)] = 0
        # Scale before summing to avoid overflow with very large finite values.
        maximum = values.max(initial=0)
        if maximum == 0:
            return {}
        values /= maximum
        values /= values.sum()
        indices = np.argsort(-values, kind="stable") if self.sort else range(len(values))
        shares = {}
        other = 0.0
        for i in indices:
            name, share = data.index[i], float(values[i])
            if name in ("Other", "Others") or share <= self.min_slice:
                other += share
            else:
                shares[name] = share
        shares["Other"] = other
        return shares

    def _color(self, name):
        if name not in self.colors:
            if name == "Other":
                color = (200, 200, 200)
            elif self.sjcanvas is not None and self.sjcanvas.color_palette:
                color = self.sjcanvas.color_palette.pop(0)
            else:
                color = color_palette[len(self.colors) % len(color_palette)]
            self.colors[name] = color
        return self.colors[name]

    def draw(self, time_obj):
        """Create the scene once; subsequent draws reset to the requested frame."""
        if not self.pies:
            self._cx = self.x_pos + self.width / 2
            self._cy = self.y_pos + self.height / 2
            self._radius = 0.34 * min(self.width, self.height)
            self._label_font = (self.text_font, tk_font_size(self.font_size), "bold")
            self._percent_font = (self.text_font, tk_font_size(self.font_size * 0.7))
        self._render(time_obj, immediate=True)

    def update(self, time_obj):
        if not self.pies:
            self.draw(time_obj)
        else:
            self._render(time_obj)

    def _render(self, time_obj, immediate=False):
        targets = self._targets(time_obj)
        names = list(targets)
        names.extend(name for name in self._order if name not in targets)
        # Keep the aggregate last even when fading categories out.
        names = [name for name in names if name != "Other"] + ["Other"]
        reset = immediate or not targets or not any(self._shares.values())
        if reset:
            self._shares = {name: targets.get(name, 0) for name in names}
        else:
            self._shares = {
                name: self._shares.get(name, 0) + self.smoothing *
                (targets.get(name, 0) - self._shares.get(name, 0))
                for name in names
            }
            self._shares = {name: (share if share > 1e-7 else 0)
                            for name, share in self._shares.items()}
            if all(abs(share - targets.get(name, 0)) < 1e-7
                   for name, share in self._shares.items()):
                self._shares = {name: targets.get(name, 0) for name in names}
        total = sum(self._shares.values())
        if total:
            self._shares = {name: share / total for name, share in self._shares.items()}
        self._order = names
        start = 0.0
        new_slice = False
        for name in names:
            if name not in self.pies:
                self.pies[name] = _Slice(self, name, self._color(name))
                new_slice = True
            share = self._shares[name]
            previous = self.pies[name]._last
            # Animate from the last displayed position, not the previous rank's
            # target. Retargeting an unfinished swap therefore remains smooth.
            # Hidden/new slices start at their destination instead of flying in
            # from a stale angle when they reappear.
            if reset or not self.sort or previous is None or previous[1] <= 1e-7:
                displayed_start = start
            else:
                old_start = self._starts[name]
                displayed_start = old_start + self.smoothing * (start - old_start)
                if abs(displayed_start - start) < 1e-7:
                    displayed_start = start
            self._starts[name] = displayed_start
            start += 360 * share
        extents = self._covering_extents()
        for name in names:
            self.pies[name].render(self._starts[name], self._shares[name], extents[name])
        if self.white is None:
            r = self._radius * self.inner_radius
            self.white = self.canvas.create_oval(
                self._cx-r, self._cy-r, self._cx+r, self._cy+r,
                fill=from_rgb(self.back_ground_color), outline="",
                state="normal" if r else "hidden")
        if new_slice:
            self.canvas.tag_raise(self.white)
            # New slices must not obscure icons belonging to existing slices.
            for item in self.pies.values():
                if item.image_id is not None:
                    self.canvas.tag_raise(item.image_id)

    def _covering_extents(self):
        """Cover every angle while independently moving wedges cross.

        In angular order, each visible wedge must reach at least the start of
        its next neighbor, including the last-to-first interval across zero.
        Keep larger data extents intact to preserve the passing animation.
        Hidden slices cannot serve as boundaries because they provide no fill.
        Use a pixel-based cutoff at the smaller shaded radius: tiny Windows Tk
        pieslices can round both endpoints to the same pixel and flash a disk.
        """
        minimum_share = self._minimum_arc_extent() / 360
        drawable = {name for name, share in self._shares.items() if share > minimum_share}
        if not drawable and any(self._shares.values()):
            # Even very small charts or many tiny categories retain a filled pie.
            drawable.add(max(self._shares, key=self._shares.get))
        extents = {name: share * 360 if name in drawable else 0
                   for name, share in self._shares.items()}
        visible = sorted((self._starts[name] % 360, i, name)
                         for i, name in enumerate(self._order)
                         if name in drawable)
        for i, (start, _, name) in enumerate(visible):
            end = visible[i + 1][0] if i + 1 < len(visible) else visible[0][0] + 360
            extents[name] = max(extents[name], end - start)
        return extents

    def _minimum_arc_extent(self):
        """Angle spanning two pixels on the inner shaded arc."""
        return math.degrees(2 / max(1, self._radius * 0.6))


class _Slice:
    """Persistent wedge, label and optional single cached icon."""

    def __init__(self, chart, name, color):
        self.chart, self.name = chart, name
        cv = chart.canvas
        cx, cy, r = chart._cx, chart._cy, chart._radius
        self.arc = cv.create_arc(cx-r, cy-r, cx+r, cy+r,
                                 fill=from_rgb(color), outline="", state="hidden")
        r *= 0.6
        self.shade = cv.create_arc(cx-r, cy-r, cx+r, cy+r,
                                   fill=from_rgb([c-25 for c in color]), outline="", state="hidden")
        self.line = cv.create_line(0, 0, 0, 0, fill="grey", state="hidden") if chart.display_label else None
        self.label = cv.create_text(0, 0, text=str(name), font=chart._label_font,
                                    fill=from_rgb(chart.font_color), state="hidden") if chart.display_label else None
        self.percent = cv.create_text(0, 0, text="", font=chart._percent_font,
                                      fill=from_rgb(chart.font_color), state="hidden") if chart.display_percentages else None
        self.image_id = self.image = None
        self._image_checked = False
        self._last = None
        self._last_extent = None

    def _load_icon(self):
        self._image_checked = True
        chart = self.chart
        filename = str(self.name).replace("*", "") + ".png"
        if Path(filename).name != filename:
            return
        try:
            with Image.open(chart.assets_dir / filename) as source:
                icon = source.convert("RGBA")
                size = max(1, int(chart._radius * 0.24))
                icon.thumbnail((size, size), Image.Resampling.LANCZOS)
                self.image = ImageTk.PhotoImage(icon, master=chart.canvas)
        except (OSError, ValueError):
            return
        self.image_id = chart.canvas.create_image(0, 0, image=self.image, state="hidden")

    def render(self, start, share, extent=None):
        extent = share * 360 if extent is None else extent
        if self._last == (start, share) and self._last_extent == extent:
            return
        self._last = (start, share)
        self._last_extent = extent
        chart, cv = self.chart, self.chart.canvas
        visible = share > 1e-7 and extent >= chart._minimum_arc_extent()
        if not visible:
            extent = 0
        # Tk reduces 360 degrees modulo 360, so use a near-full circle.
        extent = min(359.999999, extent)
        for item in (self.arc, self.shade):
            cv.itemconfig(item, start=start, extent=extent,
                          state="normal" if visible else "hidden")
        angle = math.radians(start + share * 180)
        dx, dy = math.cos(angle), -math.sin(angle)
        cx, cy, r = chart._cx, chart._cy, chart._radius
        label_visible = visible and share > chart.min_slice
        x, y = cx + 1.12*r*dx, cy + 1.12*r*dy
        anchor = "w" if dx >= 0 else "e"
        if self.label is not None:
            cv.coords(self.label, x, y)
            cv.itemconfig(self.label, anchor=anchor, state="normal" if label_visible else "hidden")
            cv.coords(self.line, cx+1.01*r*dx, cy+1.01*r*dy, cx+1.09*r*dx, cy+1.09*r*dy)
            cv.itemconfig(self.line, state="normal" if label_visible else "hidden")
        if self.percent is not None:
            offset = chart._label_font[1] * 1.5 if self.label is not None else 0
            cv.coords(self.percent, x, y+offset)
            cv.itemconfig(self.percent, anchor=anchor,
                          text=f"{share * 100:,.{chart.decimal_places}f}%",
                          state="normal" if visible and share > chart.min_percentage else "hidden")
        icon_visible = visible and share > chart.min_percentage
        if chart.display_images and icon_visible and not self._image_checked:
            self._load_icon()
        if self.image_id is not None:
            icon_radius = r * (1 + chart.inner_radius) / 2
            cv.coords(self.image_id, cx+icon_radius*dx, cy+icon_radius*dy)
            cv.itemconfig(self.image_id, state="normal" if icon_visible else "hidden")
