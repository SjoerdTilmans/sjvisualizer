"""Canvas / playback loop.

This is the top-level orchestrator that:
- owns the Tk root and a tkinter.Canvas
- holds subplots
- runs the animation loop (optionally recording)

For backwards compatibility, this module also re-exports a few commonly-used
helpers from other modules.
"""

from __future__ import annotations

import os
import math
import time
from tkinter import Canvas as TkCanvas
from tkinter import Tk
from tkinter import font

from ..utils.colors import color_palette as _default_palette
from ..utils.colors import from_rgb as _from_rgb
from ..utils.scaling import HEIGHT, WIDTH, tk_font_size

from . import subplot as _subplot


FRAMES_PER_VIDEO_WRITE = 10


class canvas:
    """Canvas to which all the graphs will be drawn."""

    def __init__(self, width=None, height=None, bg=(255, 255, 255), colors=None, include_logo=True):
        self.tk = Tk()

        if not width:
            width = WIDTH
        if not height:
            height = HEIGHT

        # Copy palette per-canvas (so multiple canvases don't share/pop the same list)
        self.color_palette = list(_default_palette)

        self.canvas = TkCanvas(self.tk, width=width, height=height, bg=_from_rgb(bg))
        self.canvas.config(highlightthickness=0)
        self.tk.attributes("-fullscreen", True)

        self.include_logo = include_logo

        if colors is None:
            colors = {}
        self.colors = colors

        self.canvas.pack()

        self.width = width
        self.height = height

        self.sub_canvas = []

        if not os.path.isdir("assets"):
            os.mkdir("assets")

    def update(self, time_obj):
        """Update function that gets called every frame of the animation."""

        for sub in self.sub_canvas:
            sub.update(time_obj)

        self.tk.update()

    def add_sub_plot(self, sub_plot):
        """Add a subplot to this canvas."""

        if sub_plot in self.sub_canvas:
            return
        sub_plot.set_root(self.tk)
        self.sub_canvas.append(sub_plot)

    def set_decimals(self, decimals: int):
        # Update shared default used by charts that don't set decimal_places explicitly
        _subplot.decimal_places = int(decimals)

    def play(self, df=None, fps=30, record=False, width=None, height=None, file_name="output.mp4", *, show_fps=False):
        """Play every frame; optionally record the canvas at its screen position.

        Recording dimensions default to the canvas size. ``show_fps`` enables
        per-frame diagnostics, which are disabled to avoid console overhead.
        """

        fps = float(fps)
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("fps must be a finite positive number")
        width = int(self.width if width is None else width)
        height = int(self.height if height is None else height)
        if record and (width <= 0 or height <= 0):
            raise ValueError("Recording dimensions must be positive")

        if df is None:
            for sub in self.sub_canvas:
                if getattr(sub, "df", None) is not None:
                    df = sub.df
                    break
                if hasattr(sub, "df_x") and getattr(sub, "df_x") is not None:
                    df = sub.df_x
                    break
                if hasattr(sub, "df_y") and getattr(sub, "df_y") is not None:
                    df = sub.df_y
                    break

        if df is None:
            raise ValueError("No dataframe provided and no subplot contains a dataframe to play.")
        if len(df.index) == 0:
            raise ValueError("Cannot play an empty dataframe")

        if self.include_logo and not getattr(self, "_logo_added", False):
            self._add_sj_logo()
            self._logo_added = True

        capture_video = None
        if record:
            # Playback and data loading do not need the video encoder.
            import cv2
            import numpy as np
            from PIL import ImageGrab

            fourc = cv2.VideoWriter_fourcc(*"mp4v")
            capture_video = cv2.VideoWriter(file_name, fourc, fps, (int(width), int(height)))
            if not capture_video.isOpened():
                capture_video.release()
                raise RuntimeError(f"Could not open video writer for {file_name!r}")

        try:
            for date_time in df.index:
                start = time.perf_counter()
                self.update(date_time)
                if record:
                    x = self.canvas.winfo_rootx()
                    y = self.canvas.winfo_rooty()
                    with ImageGrab.grab(bbox=(x, y, x + width, y + height)) as img:
                        capture_video.write(cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR))

                remaining = (1 / fps) - (time.perf_counter() - start)
                if remaining > 0:
                    time.sleep(remaining)
                if show_fps:
                    fps_value = 1.0 / max(time.perf_counter() - start, 1e-9)
                    print(f"FPS: {fps_value:,.{_subplot.decimal_places}f}")
        finally:
            if capture_video is not None:
                capture_video.release()

        if record:
            self.tk.destroy()

    def add_title(self, text, color=(0, 0, 0)):
        title_font = font.Font(family="Microsoft JhengHei UI", size=tk_font_size(self.height / 30), weight="bold")
        self.canvas.create_text(self.width / 2, self.height / 20, font=title_font, text=text, fill=_from_rgb(color))

    def add_sub_title(self, text, color=(0, 0, 0)):
        title_font = font.Font(family="Microsoft JhengHei UI", size=tk_font_size(self.height / 45))
        self.canvas.create_text(self.width / 2, self.height / 11, font=title_font, text=text, fill=_from_rgb(color))

    def add_time(self, df, time_indicator="year", color=(150, 150, 150)):
        # Optional dependency provided by other modules in the package
        from sjvisualizer import Date

        subp = Date.date(
            canvas=self.canvas,
            start_time=df.index[0],
            width=0,
            height=self.height / 12,
            x_pos=self.width / 20,
            y_pos=self.height * 0.9,
            time_indicator=time_indicator,
            font_color=color,
            anchor="w",
        )
        self.add_sub_plot(subp)

    def add_logo(self, logo):
        from sjvisualizer import StaticImage

        img = StaticImage.static_image(
            canvas=self.canvas,
            width=int(self.width / 15),
            height=int(self.width / 15),
            x_pos=self.width * 0.95,
            y_pos=self.height * 0.00,
            file=logo,
            root=self.tk,
            anchor="ne",
        )
        self.add_sub_plot(img)

    def _add_sj_logo(self):
        from sjvisualizer import StaticImage

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "Made with SJvisualzer.png")
        path = os.path.abspath(path)
        img = StaticImage.static_image(
            canvas=self.canvas,
            width=int(self.width / 5),
            height=int(self.width / 5),
            x_pos=self.width * 0.85,
            y_pos=self.height * 0.90,
            file=path,
            root=self.tk,
            anchor="e",
        )
        self.add_sub_plot(img)


# --- Backwards-compatible re-exports (used as "from sjvisualizer import Canvas as cv") ---

# Base class and helpers
sub_plot = _subplot.sub_plot
load_image = _subplot.load_image

# Formatting / colors
format_date = _subplot.format_date
format_value = _subplot.format_value

# Color conversion
# (many charts call cv._from_rgb)

# Also re-export color constants some charts rely on
from ..utils.colors import min_color, max_color, hex_to_rgb  # noqa: E402

# Legacy helper names
_from_rgb = _from_rgb

