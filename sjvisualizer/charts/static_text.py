"""Static text element.

This is a lightweight subplot that draws a single text string. It can be used
for titles, labels, annotations, etc.

Unlike time-series charts, :class:`static_text` does not require a dataframe.
"""

from __future__ import annotations

from tkinter import font

from ..core.subplot import sub_plot
from ..utils.colors import from_rgb
from ..utils.scaling import SCALEFACTOR


UNDERLINE = 0
DEFAULT_TEXT_FONT = "Microsoft JhengHei UI"


def _normalize_anchor(anchor: str) -> str:
    if not anchor:
        return "center"
    a = str(anchor).lower()
    if a in ("c", "center"):
        return "center"
    return a


class static_text(sub_plot):
    """Draw a static text string on the canvas.

    Parameters
    ----------
    text:
        The text to display.
    angle:
        Rotation angle in degrees (Tk supports this on some platforms).
    position_mode:
        - ``"box"`` (default): interpret ``x_pos``/``y_pos`` as a bounding box.
        - ``"point"``: interpret ``x_pos``/``y_pos`` as the actual text point.
    align:
        Optional legacy alignment hint (e.g. ``"left"``).

    Common positioning and styling parameters are inherited from
    :class:`sjvisualizer.core.subplot.sub_plot`.
    """

    def __init__(
        self,
        canvas,
        text: str | None = None,
        *,
        x_pos=None,
        y_pos=None,
        width=None,
        height=None,
        colors=None,
        root=None,
        anchor="center",
        title: str | None = None,
        font_color=(0, 0, 0),
        back_ground_color=(255, 255, 255),
        text_font: str = DEFAULT_TEXT_FONT,
        font_size: int = 25,
        angle: float = 0,
        position_mode: str = "box",
        align: str | None = None,
        **kwargs,
    ):
        # Backwards-compatible: allow text to be passed via kwargs.
        if text is None and "text" in kwargs:
            text = kwargs.pop("text")

        self.text = text
        self.angle = angle
        self.position_mode = position_mode
        self.align = align

        super().__init__(
            canvas=canvas,
            width=width,
            height=height,
            x_pos=x_pos,
            y_pos=y_pos,
            colors=colors,
            root=root,
            anchor=anchor,
            title=title,
            font_color=font_color,
            back_ground_color=back_ground_color,
            text_font=text_font,
            font_size=font_size,
            **kwargs,
        )

    def draw(self, *args, **kwargs):
        if not hasattr(self, "angle"):
            self.angle = 0

        if hasattr(self, "font_size") and self.font_size is not None:
            font_size = int(self.font_size / SCALEFACTOR)
        elif getattr(self, "height_is_set", False):
            font_size = int(0.65 * self.height / SCALEFACTOR)
        else:
            font_size = int(25 / SCALEFACTOR)

        chosen_font = getattr(self, "text_font", DEFAULT_TEXT_FONT)

        self.font = font.Font(
            family=chosen_font,
            size=font_size,
            underline=UNDERLINE,
            weight="bold",
        )

        anchor = _normalize_anchor(getattr(self, "anchor", "center"))
        position_mode = getattr(self, "position_mode", "box")

        if position_mode == "point":
            x = self.x_pos
            y = self.y_pos
        else:
            if getattr(self, "align", None) == "left":
                x = self.x_pos
                y = self.y_pos + self.height / 2
            else:
                x = self.x_pos + self.width / 2
                y = self.y_pos + self.height / 2

        self.text_obj = self.canvas.create_text(
            x,
            y,
            text=self.text,
            font=self.font,
            fill=from_rgb(self.font_color),
            anchor=anchor,
            angle=self.angle,
        )

    def update(self, *args, **kwargs):
        # Static elements typically want to stay visible.
        self.canvas.tag_raise(self.text_obj)
