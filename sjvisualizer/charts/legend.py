"""Reusable ranked legend with stable ties and bounded item count."""
import numpy as np
from ._frame_chart import FrameChart
from ..utils.scaling import tk_font_size

__all__ = ["legend"]


class legend(FrameChart):
    def __init__(self, canvas=None, df=None, *, n=None, sort=True,
                 display_values=False, orientation="vertical", **kwargs):
        if orientation not in ("vertical", "horizontal"):
            raise ValueError("orientation must be vertical or horizontal")
        if n is not None and (int(n) != n or n < 1):
            raise ValueError("n must be an integer >= 1")
        self.n, self.sort, self.orientation = n, sort, orientation
        self.display_values = display_values
        self.elems = {}
        super().__init__(canvas, df, **kwargs)

    def draw(self, time):
        if self._drawn:
            return
        self.n = min(self.n or 10, len(self.df.columns))
        for name in self.df.columns:
            swatch = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color(name), outline="")
            label = self.text(0, 0, anchor="w")
            self.elems[name] = swatch, label
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            return
        row = self._values[k]
        order = np.argsort(-row, kind="stable") if self.sort else np.arange(len(row))
        for rank, j in enumerate(order):
            name = self.df.columns[j]
            swatch, label = self.elems[name]
            state = "normal" if rank < self.n else "hidden"
            self.canvas.itemconfig(swatch, state=state)
            suffix = f" {row[j]:,.{self.decimal_places}f}{self.unit}" if self.display_values else ""
            self.canvas.itemconfig(label, state=state, text=str(name)+suffix)
            x = self.x_pos + (rank*self.width/self.n if self.orientation == "horizontal" else 0)
            y = self.y_pos + ((rank+.5)*self.height/self.n if self.orientation == "vertical" else self.height/2)
            r = tk_font_size(self.font_size)*.3
            self.canvas.coords(swatch, x, y-r, x+2*r, y+r)
            self.canvas.coords(label, x+2*r+8, y)
        self._last_frame = k
