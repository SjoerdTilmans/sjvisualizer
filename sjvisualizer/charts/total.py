"""Animated sum overlay."""
from ._frame_chart import FrameChart

__all__ = ["total"]


class total(FrameChart):
    def __init__(self, canvas=None, df=None, *, prefix="", **kwargs):
        self.prefix = prefix
        self._last_text = None
        super().__init__(canvas, df, **kwargs)

    def draw(self, time):
        if self._drawn:
            return
        self._totals = self._values.sum(axis=1)
        self.text_id = self.text(self.x_pos, self.y_pos, anchor=self.anchor)
        self._drawn = True
        self.update(time)

    def update(self, time):
        value = self._totals[self.frame(time)]
        money = "$" if "$" in self.unit else ""
        text = f"{self.prefix}{money}{value:,.{self.decimal_places}f}{self.unit.replace('$', '')}"
        if text != self._last_text:
            self.canvas.itemconfig(self.text_id, text=text)
            self._last_text = text
