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
import time
from tkinter import Canvas as TkCanvas
from tkinter import Tk
from tkinter import font

import cv2
import numpy as np
from PIL import ImageGrab

from ..utils.colors import color_palette as _default_palette
from ..utils.colors import from_rgb as _from_rgb
from ..utils.scaling import HEIGHT, WIDTH, SCALEFACTOR

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

        self.canvas.pack()
        self.tk.update()

    def add_sub_plot(self, sub_plot):
        """Add a subplot to this canvas."""

        sub_plot.set_root(self.tk)
        self.sub_canvas.append(sub_plot)

    def set_decimals(self, decimals: int):
        # Update shared default used by charts that don't set decimal_places explicitly
        _subplot.decimal_places = int(decimals)

    def play(self, df=None, fps=30, record=False, width=WIDTH, height=HEIGHT, file_name="output.mp4"):
        """Main loop of the animation."""

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

        capture_video = None
        if record:
            self.frames = []
            fourc = cv2.VideoWriter_fourcc(*"mp4v")
            capture_video = cv2.VideoWriter(file_name, fourc, fps, (int(width), int(height)))

        if self.include_logo:
            self._add_sj_logo()

        for i, date_time in enumerate(df.index):
            start = time.time()
            self.update(date_time)
            if i == 0:
                time.sleep(1)

            # grab a screenshot for each of the frames
            if record and i > 1:
                img = ImageGrab.grab(bbox=(0, 0, int(width), int(height)))
                self.frames.append(img)

                if len(self.frames) > FRAMES_PER_VIDEO_WRITE:
                    for f in self.frames:
                        img_np = np.array(f)
                        img_final = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                        capture_video.write(img_final)
                    self.frames = []

            # pace
            elapsed = time.time() - start
            remaining = (1 / fps) - elapsed
            if remaining > 0:
                time.sleep(remaining)

            time_used = time.time() - start
            fps_value = 1.0 / max(time_used, 1e-9)
            print(f"FPS: {fps_value:,.{_subplot.decimal_places}f}")

        if record:
            if getattr(self, "frames", None):
                for f in self.frames:
                    img_np = np.array(f)
                    img_final = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                    capture_video.write(img_final)
                self.frames = []

            try:
                capture_video.release()
            except Exception:
                pass

            time.sleep(1)
            self.tk.destroy()
            cv2.destroyAllWindows()

    def add_title(self, text, color=(0, 0, 0)):
        title_font = font.Font(family="Microsoft JhengHei UI", size=int(self.height / 30 / SCALEFACTOR), weight="bold")
        self.canvas.create_text(self.width / 2, self.height / 20, font=title_font, text=text, fill=_from_rgb(color))

    def add_sub_title(self, text, color=(0, 0, 0)):
        title_font = font.Font(family="Microsoft JhengHei UI", size=int(self.height / 45 / SCALEFACTOR))
        self.canvas.create_text(self.width / 2, self.height / 11, font=title_font, text=text, fill=_from_rgb(color))

    def add_time(self, df, time_indicator="year", color=(150, 150, 150)):
        # Optional dependency provided by other modules in the package
        from sjvisualizer import Date

        subp = Date.date(
            canvas=self.canvas,
            start_time=list(df.index)[0],
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

