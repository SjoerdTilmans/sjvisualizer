"""Choropleth animation with immutable source geometry and cached fills."""
from pathlib import Path
import numpy as np
from ._frame_chart import FrameChart
from ..utils.colors import from_rgb
from ..data.maps import geometry as _geometry, map_name as _map_name, MAP_NAMES

__all__ = ["map", "MAP_NAMES"]
MAP_SIZE = (2000, 1142.5758125835168)


class map(FrameChart):
    """Color countries and legend with round automatic range boundaries.

    ``legend_values=[0, 10, 25, 50, 100, 200]`` fixes the boundaries for the
    entire animation, overriding ``legend_bins`` and ``min_value``. Automatic
    ranges use 1, 2 or 5 times a power of ten, rounding outward to cover data.

    Missing/nonfinite values use a separate grey swatch. Finite values outside
    the scale are clamped to its endpoint bins. Internal boundaries belong to
    the higher bin; the upper endpoint belongs to the final bin.

    ``map_name`` selects world (default), europe, usa_states, africa,
    north_america or asia. ``map_file`` optionally supplies a custom JSON
    keyed by region name, with a Polygons array of projected [x, y] rings.
    US state data may use full names or postal abbreviations.
    """
    def __init__(self, canvas=None, df=None, *, min_value=0, color_bar_color=None,
                 allow_decrease=False, missing_color=(190, 190, 190),
                 legend_bins=5, legend_values=None, map_name="world", map_file=None, **kwargs):
        self.map_name = _map_name(map_name)
        self.map_file = str(Path(map_file).resolve()) if map_file is not None else None
        self._geometry = _geometry(self.map_name, self.map_file)
        if not np.isfinite(min_value):
            raise ValueError("min_value must be finite")
        if not np.isfinite(legend_bins) or int(legend_bins) != legend_bins or legend_bins < 1:
            raise ValueError("legend_bins must be an integer >= 1")
        self.legend_bins = int(legend_bins)
        self.legend_values = None
        if legend_values is not None:
            edges = np.array(legend_values, dtype=float, copy=True)
            if edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges).all() or not np.all(edges[1:] > edges[:-1]):
                raise ValueError("legend_values must contain at least two finite, strictly increasing boundaries")
            self.legend_values = edges
            self.legend_bins = len(edges)-1
        self.min_value, self.allow_decrease = min_value, allow_decrease
        self.color_bar_color = color_bar_color or [(220, 235, 250), (35, 90, 180)]
        self._bin_colors = [from_rgb(tuple(int(a+(b-a)*fraction)
                            for a, b in zip(*self.color_bar_color)))
                            for fraction in np.linspace(0, 1, self.legend_bins)]
        self.missing_color = from_rgb(missing_color)
        self.countries, self._fills = {}, {}
        # Missing values remain visually distinct from actual zero values.
        self._valid = np.isfinite(df.to_numpy(dtype=float)) if hasattr(df, "to_numpy") else None
        super().__init__(canvas, df, **kwargs)

    def _legend_edges(self, maximum):
        if self.legend_values is not None:
            return self.legend_values.copy()
        span = max(0., maximum-self.min_value)
        raw_step = span/self.legend_bins if span else 1.
        magnitude = 10.**np.floor(np.log10(raw_step))
        # Include room for rounding the lower boundary down as well.
        while True:
            for multiple in (1, 2, 5):
                step = multiple*magnitude
                start = np.floor(self.min_value/step)*step
                if step >= raw_step*(1-1e-12) and start+self.legend_bins*step >= maximum-step*1e-12:
                    return start+np.arange(self.legend_bins+1)*step
            magnitude *= 10

    def _color(self, value, maximum=None):
        if not np.isfinite(value):
            return self.missing_color
        edges = self.bin_edges if maximum is None else self._legend_edges(maximum)
        index = int(np.searchsorted(edges, value, side="right"))-1
        return self._bin_colors[max(0, min(index, self.legend_bins-1))]

    def draw(self, time):
        if self._drawn:
            return
        points = np.concatenate([ring for data in self._geometry.values() for ring in data["Polygons"]])
        low, high = points.min(axis=0), points.max(axis=0)
        if self.map_name == "world" and self.map_file is None:
            low, high = np.zeros(2), np.asarray(MAP_SIZE)
        extent = np.maximum(high-low, 1e-12)
        ratio = min(self.width/extent[0], self.height/extent[1])
        shift = np.array([self.x_pos+(self.width-extent[0]*ratio)/2,
                          self.y_pos+(self.height-extent[1]*ratio)/2])-low*ratio
        for name, data in self._geometry.items():
            self.countries[name] = [self.canvas.create_polygon(
                *((np.asarray(poly)*ratio+shift).ravel().tolist()),
                fill=self.missing_color, outline="#c8c8c8", width=.5) for poly in data["Polygons"]]
        self._columns = {str(name).casefold(): i for i, name in enumerate(self.df.columns)}
        self._region_values = {}
        for name, data in self._geometry.items():
            aliases = [name, *data.get("Aliases", [])]
            if name == "Russia":
                aliases.extend(("USSR", "USSR/Russia"))
            columns = [self._columns[n.casefold()] for n in aliases if n.casefold() in self._columns]
            if columns:
                values = np.where(self._valid[:, columns], self._values[:, columns], -np.inf).max(axis=1)
                self._region_values[name] = values
        # Ignore columns for countries outside the selected region's scale.
        frame_maxima = np.zeros(len(self.df))
        for values in self._region_values.values():
            frame_maxima = np.maximum(frame_maxima, values)
        self._frame_maxima = frame_maxima
        self._maxima = np.maximum.accumulate(frame_maxima)
        self._legend_labels, self._legend_swatches = [], []
        legend_width = self.width*.75
        y = self.y_pos+self.height+20
        for i, color in enumerate(self._bin_colors):
            x = self.x_pos+i*legend_width/self.legend_bins
            self._legend_swatches.append(self.canvas.create_rectangle(
                x, y, x+legend_width/self.legend_bins, y+18,
                fill=color, outline=from_rgb(self.back_ground_color)))
        for i in range(self.legend_bins+1):
            self._legend_labels.append(self.text(self.x_pos+i*legend_width/self.legend_bins,
                y+24, anchor="n"))
        x = self.x_pos+self.width*.82
        self._missing_swatch = self.canvas.create_rectangle(x, y, x+24, y+18,
            fill=self.missing_color, outline="")
        self.text(x+32, y+9, text="No data", anchor="w")
        self._drawn = True
        self.update(time)

    def update(self, time):
        k = self.frame(time)
        if k == self._last_frame:
            return
        maximum = max(self.min_value, self._frame_maxima[k] if self.allow_decrease else self._maxima[k])
        self.current_max_value = maximum
        self.bin_edges = self._legend_edges(maximum)
        for label, edge in zip(self._legend_labels, self.bin_edges):
            if edge and abs(edge) < 1e-8:
                text = f"{edge:.10g}"
            else:
                text = f"{edge:,.10f}".rstrip("0").rstrip(".")
            self.canvas.itemconfig(label, text=text+self.unit)
        for name, polygons in self.countries.items():
            values = self._region_values.get(name)
            color = self._color(values[k]) if values is not None else self.missing_color
            if self._fills.get(name) != color:
                for polygon in polygons:
                    self.canvas.itemconfig(polygon, fill=color)
                self._fills[name] = color
        self._last_frame = k
