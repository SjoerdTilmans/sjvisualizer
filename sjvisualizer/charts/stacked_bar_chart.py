"""Time-sampled stacked bars with bounded canvas item count."""
import numpy as np
from ._frame_chart import FrameChart, numeric_data
from ..utils.format import format_date

__all__ = ["stacked_bar_chart"]


class stacked_bar_chart(FrameChart):
    """Reveal up to number_of_bars evenly sampled rows, including endpoints.

    Values must be nonnegative. Seeking hides future bars and restores the
    scale for that frame; no frame-count-dependent trailing pause is assumed.
    New bars rise with a damped spring over ``animation_frames`` updates
    (default 24). Existing bars smoothly share their width with new arrivals.
    Repeated final-frame updates let the last arrival finish animating.
    """
    def __init__(self, canvas=None, df=None, *, number_of_bars=10, y_ticks=5,
                 x_ticks=5, time_indicator="year", animation_frames=24,
                 bar_gap=0.08, **kwargs):
        values = numeric_data(df)
        if (values < 0).any():
            raise ValueError("stacked values must be nonnegative")
        if int(number_of_bars) != number_of_bars or number_of_bars < 1:
            raise ValueError("number_of_bars must be an integer >= 1")
        if not np.isfinite(animation_frames) or int(animation_frames) != animation_frames or animation_frames < 0:
            raise ValueError("animation_frames must be an integer >= 0")
        if not np.isfinite(bar_gap) or not 0 <= bar_gap < 1:
            raise ValueError("bar_gap must be between 0 and 1 (exclusive)")
        self.animation_frames, self.bar_gap = int(animation_frames), bar_gap
        self._held_frames = 0
        self.samples = np.unique(np.linspace(0, len(df)-1, min(int(number_of_bars), len(df)), dtype=int))
        self._tops = np.cumsum(values[:, ::-1], axis=1)[:, ::-1]
        if not np.isfinite(self._tops).all():
            raise ValueError("stacked totals exceed the numeric range")
        self._maxima = np.maximum.accumulate(self._tops[:, 0])
        self.y_ticks, self.x_ticks, self.time_indicator = y_ticks, x_ticks, time_indicator
        self.bars, self.labels = [], []
        super().__init__(canvas, df, **kwargs)

    def draw(self, time):
        if self._drawn:
            return
        self.axis = self.make_axis("vertical", self.y_ticks, unit=self.unit)
        self.axis.draw(min=0, max=1)
        spacing = self.width/len(self.samples)
        label_samples = set(np.linspace(0, len(self.samples)-1, max(1, min(int(self.x_ticks), len(self.samples))), dtype=int))
        for i, k in enumerate(self.samples):
            self.bars.append([self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color(name), outline="")
                              for name in self.df.columns])
            stamp = self.df.index[k]
            label = format_date(stamp, self.time_indicator) if hasattr(stamp, "year") else str(stamp)
            self.labels.append(self.text(self.x_pos+(i+.5)*spacing, self.y_pos+self.height+10,
                                         text=label if i in label_samples else "", anchor="n"))
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            if self._held_frames >= self.animation_frames:
                return
            self._held_frames += 1
        else:
            self._held_frames = 0
        maximum = max(1., self._maxima[k])
        self.axis.update(min=0, max=maximum)
        visible = int(np.searchsorted(self.samples, k, side="right"))
        ages = k-self.samples[:visible]+self._held_frames
        progress = np.clip(ages/max(1, self.animation_frames), 0, 1)
        if not self.animation_frames or len(self.df) == 1:
            progress[:] = 1
        # A smooth width transition cannot overshoot and overlap its neighbors.
        weights = progress*progress*(3-2*progress)
        weights[0] = 1  # The first bar owns the full width from the outset.
        edges = np.concatenate(([0.], np.cumsum(weights))) / weights.sum() * self.width
        # Analytic underdamped step response: a small bounce, then exact rest.
        phase = 12*progress
        spring = 1-np.exp(-.55*phase)*(np.cos(phase)+.55*np.sin(phase))
        spring[progress >= 1] = 1
        gap = self.bar_gap*self.width/weights.sum()*min(1., weights.sum()-1)
        for i, (sample, bars) in enumerate(zip(self.samples, self.bars)):
            state = "normal" if sample <= k else "hidden"
            self.canvas.itemconfig(self.labels[i], state=state)
            if i < visible:
                left, right = self.x_pos+edges[i], self.x_pos+edges[i+1]
                inset = min(gap/2, (right-left)/2)
                self.canvas.coords(self.labels[i], (left+right)/2, self.y_pos+self.height+10)
            for j, bar in enumerate(bars):
                self.canvas.itemconfig(bar, state=state)
                if i >= visible:
                    continue
                top = self._tops[sample, j]
                bottom = top-self._values[sample, j]
                self.canvas.coords(bar, left+inset,
                    self.y_pos+self.height-top/maximum*self.height*spring[i],
                    right-inset, self.y_pos+self.height-bottom/maximum*self.height*spring[i])
        self._last_frame = k
