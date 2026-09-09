"""Animated categorical bars (legacy Histogram input is already aggregated)."""
import numpy as np
from ._frame_chart import FrameChart

__all__ = ["histogram"]


class histogram(FrameChart):
    """One bar per column, with signed values and deterministic frame seeking."""
    def __init__(self, canvas=None, df=None, *, y_ticks=5, allow_decrease=False, **kwargs):
        self.y_ticks, self.allow_decrease = y_ticks, allow_decrease
        self.bars = {}
        super().__init__(canvas, df, **kwargs)

    def draw(self, time):
        if self._drawn:
            return
        self.axis = self.make_axis("vertical", self.y_ticks, unit=self.unit)
        self.axis.draw(min=0, max=1)
        self._lows = np.minimum.accumulate(np.minimum(self._values.min(axis=1), 0))
        self._highs = np.maximum.accumulate(np.maximum(self._values.max(axis=1), 0))
        self.spacing = self.width / len(self.df.columns)
        for i, name in enumerate(self.df.columns):
            self.bars[name] = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color(name), outline="")
            self.text(self.x_pos+(i+.5)*self.spacing, self.y_pos+self.height+8,
                      text=str(name), anchor="n")
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            return
        row = self._values[k]
        lo, hi = (min(0, row.min()), max(0, row.max())) if self.allow_decrease else (self._lows[k], self._highs[k])
        self.axis.update(min=lo, max=hi if hi > lo else lo+1)
        baseline = self.y_pos+self.height-self.axis.calc_positions(0)
        for i, (name, value) in enumerate(zip(self.df.columns, row)):
            x = self.x_pos+(i+.5)*self.spacing
            y = self.y_pos+self.height-self.axis.calc_positions(value)
            self.canvas.coords(self.bars[name], x-.375*self.spacing, baseline, x+.375*self.spacing, y)
        self._last_frame = k
