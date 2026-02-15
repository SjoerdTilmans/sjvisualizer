from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import sub_plot  # avoid star import
from tkinter import font
import ctypes
import platform

from screeninfo import get_monitors


# Keep these globals for compatibility with other modules/scripts that might import them
if platform.system() == "Windows":
    SCALEFACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
else:
    SCALEFACTOR = 1

UNDERLINE = 0
text_font = "Microsoft JhengHei UI"

try:
    monitor = get_monitors()[0]
    HEIGHT = monitor.height
    WIDTH = monitor.width
except Exception:
    WIDTH = 1920
    HEIGHT = 1080


def _normalize_anchor(anchor: str) -> str:
    if not anchor:
        return "center"
    a = str(anchor).lower()
    if a in ("c", "center"):
        return "center"
    return a


class static_text(cv.sub_plot):
    """
    Static text element.

    Improvements:
    - Uses font_size directly if provided.
    - Only falls back to legacy height->font sizing if font_size is missing.
    - position_mode:
        * "box"   (default): legacy feel; centers within (x_pos,y_pos,width,height)
        * "point": new behavior; uses x_pos/y_pos as the anchor point directly
    """

    def draw(self, *args, **kwargs):
        if not hasattr(self, "angle"):
            self.angle = 0

        # Choose font size:
        # - If user provided font_size, use it (new requested behavior).
        # - Else fall back to old height-derived logic for compatibility.
        if hasattr(self, "font_size") and self.font_size is not None:
            font_size = int(self.font_size / SCALEFACTOR)
        elif getattr(self, "height_is_set", False):
            font_size = int(0.65 * self.height / SCALEFACTOR)
        else:
            font_size = int(25 / SCALEFACTOR)

        chosen_font = getattr(self, "text_font", text_font)

        self.font = font.Font(
            family=chosen_font,
            size=font_size,
            underline=UNDERLINE,
            weight="bold",
        )

        anchor = _normalize_anchor(getattr(self, "anchor", "center"))
        position_mode = getattr(self, "position_mode", "box")

        # Positioning:
        # - "point": x_pos/y_pos are the anchor point (requested).
        # - "box": maintain old “box-centered” behavior by default.
        if position_mode == "point":
            x = self.x_pos
            y = self.y_pos
        else:
            # Legacy-ish behavior, including the special "align=left" handling you had :contentReference[oaicite:2]{index=2}
            if getattr(self, "align", None) == "left":
                x = self.x_pos
                y = self.y_pos + self.height / 2
            else:
                x = self.x_pos + self.width / 2
                y = self.y_pos + self.height / 2

        # Draw
        self.text_obj = self.canvas.create_text(
            x,
            y,
            text=self.text,
            font=self.font,
            fill=cv._from_rgb(self.font_color),
            anchor=anchor,
            angle=self.angle,
        )

    def update(self, *args, **kwargs):
        self.canvas.tag_raise(self.text_obj)
