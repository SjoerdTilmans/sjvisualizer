"""Animated sentiment matrix with bounded, continuous level positions."""
import numpy as np
from ._frame_chart import FrameChart
from ..utils.colors import from_rgb

__all__ = ["dynamic_matrix"]


class dynamic_matrix(FrameChart):
    def __init__(self, canvas=None, df=None, *, level_count=2, neutral_string="0",
                 color_range=None, **kwargs):
        if int(level_count) != level_count or level_count < 1:
            raise ValueError("level_count must be an integer >= 1")
        self.level_count, self.neutral_string = int(level_count), neutral_string
        self.color_range = color_range or [(255, 40, 60), (3, 175, 81)]
        self.bars = []
        super().__init__(canvas, df, **kwargs)

    def _generate_sentiment_levels(self, level_count):
        if int(level_count) != level_count or level_count < 1:
            raise ValueError("level_count must be an integer >= 1")
        return ["-"*-i if i < 0 else "+"*i if i else self.neutral_string
                for i in range(-int(level_count), int(level_count)+1)]

    def draw(self, time):
        if self._drawn:
            return
        self.spacing = self.height/len(self.df.columns)
        self.box_width = self.width*.7/(2*self.level_count+1)
        self._left = self.x_pos+self.width*.3
        for j, label in enumerate(self._generate_sentiment_levels(self.level_count)):
            x = self._left+j*self.box_width
            self.canvas.create_line(x, self.y_pos, x, self.y_pos+self.height, fill="#cccccc")
            self.text(x+self.box_width/2, self.y_pos-8, text=label, anchor="s")
        for i, name in enumerate(self.df.columns):
            y = self.y_pos+(i+.5)*self.spacing
            name = str(name)
            self.text(self.x_pos, y, text="   "*name.count("+")+name.replace("+", ""), anchor="w")
            self.bars.append(self.canvas.create_rectangle(0, 0, 0, 0, outline=""))
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            return
        for i, (bar, value) in enumerate(zip(self.bars, self._values[k])):
            value = np.clip(value, -self.level_count, self.level_count)
            x = self._left+(value+self.level_count)*self.box_width
            y = self.y_pos+(i+.5)*self.spacing
            self.canvas.coords(bar, x, y-self.spacing*.35, x+self.box_width, y+self.spacing*.35)
            fraction = abs(value)/self.level_count
            endpoint = self.color_range[0 if value < 0 else 1]
            color = tuple(int(210*(1-fraction)+c*fraction) for c in endpoint)
            self.canvas.itemconfig(bar, fill=from_rgb(color))
        self._last_frame = k
