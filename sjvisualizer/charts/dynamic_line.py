"""A curve connecting categories at each animation frame."""
import numpy as np
from ._frame_chart import FrameChart

__all__ = ["dynamic_curve"]


class dynamic_curve(FrameChart):
    def __init__(self, canvas=None, df=None, *, color=(31, 119, 180),
                 marker_size=10, y_ticks=5, allow_decrease=False, label="", **kwargs):
        if marker_size < 0:
            raise ValueError("marker_size must be nonnegative")
        self._line_color, self.marker_size = color, marker_size
        self.y_ticks, self.allow_decrease, self.label = y_ticks, allow_decrease, label
        super().__init__(canvas, df, **kwargs)

    def draw(self, time):
        if self._drawn:
            return
        self.x_axis = self.make_axis("horizontal", fixed_min=0, fixed_max=len(self.df.columns))
        self.x_axis.draw(min=0, max=len(self.df.columns))
        for tick in self.x_axis.ticks:
            tick.update(value=0, draw=False)
        self.y_axis = self.make_axis("vertical", self.y_ticks, unit=self.unit)
        self.y_axis.draw(min=0, max=1)
        self._lows = np.minimum.accumulate(np.minimum(self._values.min(axis=1), 0))
        self._highs = np.maximum.accumulate(np.maximum(self._values.max(axis=1), 0))
        self._positions = [self.x_pos+self.x_axis.calc_positions(i+.5) for i in range(len(self.df.columns))]
        self.colors.setdefault(self.label, self._line_color)
        color = self.color(self.label)
        self.line = self.canvas.create_line(0, 0, 0, 0, fill=color, width=max(1, self.marker_size/3))
        self.markers = []
        for name, x in zip(self.df.columns, self._positions):
            self.markers.append(self.canvas.create_oval(0, 0, 0, 0, fill="white", outline=color, width=2))
            self.text(x, self.y_pos+self.height+10, text=str(name), anchor="n")
        self._label_id = self.text(0, 0, text=self.label, fill=color, anchor="w")
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            return
        row = self._values[k]
        lo, hi = (min(0, row.min()), max(0, row.max())) if self.allow_decrease else (self._lows[k], self._highs[k])
        self.y_axis.update(min=lo, max=hi if hi > lo else lo+1)
        coords = []
        r = self.marker_size/2
        for marker, x, value in zip(self.markers, self._positions, row):
            y = self.y_pos+self.height-self.y_axis.calc_positions(value)
            coords.extend((x, y))
            self.canvas.coords(marker, x-r, y-r, x+r, y+r)
        self.canvas.coords(self.line, *(coords if len(coords)>2 else coords*2))
        self.canvas.coords(self._label_id, coords[-2]+10, coords[-1])
        self._last_frame = k
