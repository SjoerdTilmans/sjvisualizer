import math
import datetime
from sjvisualizer import Canvas as cv
from tkinter import font

months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# Helper for converting RGB + opacity to tkinter-compatible hex color string
def blend_with_white(rgb, opacity):
    r, g, b = rgb
    r = int((1 - opacity) * 255 + opacity * r)
    g = int((1 - opacity) * 255 + opacity * g)
    b = int((1 - opacity) * 255 + opacity * b)
    return f'#{r:02x}{g:02x}{b:02x}'

class axis():
    def __init__(self, canvas, x=0, y=0, length=1000, width=1000, orientation="horizontal", n=5, allow_decrease=False,
                 tick_length=0, is_log_scale=False, is_date=False, color=(0, 0, 0), font_size=20,
                 text_font="Microsoft JhengHei UI", time_indicator="year", line_tickness=2, ticks_only=True, unit="",
                 tick_prefix="", decimal_places=2, negative_values=False,
                 show_gridlines=False, gridline_color=(100, 100, 100), gridline_opacity=0.6):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.length = length
        self.orientation = orientation
        self.n = n
        self.allow_decrease = allow_decrease
        self.is_log_scale = is_log_scale
        self.is_date = is_date
        self.color = color
        self.font_size = font_size
        self.text_font = text_font
        self.time_indicator = time_indicator
        self.line_tickness = line_tickness
        self.ticks_only = ticks_only
        self.width = width
        self.unit = unit
        self.tick_prefix = tick_prefix
        self.decimal_places = decimal_places
        self.negative_values = negative_values

        self.show_gridlines = show_gridlines
        self.gridline_color = gridline_color
        self.gridline_opacity = gridline_opacity

        self.min = None
        self.max = None

        self.ticks = [tick(self.canvas, axis=self, length=tick_length, tick_prefix=self.tick_prefix) for _ in range(5)]

    def draw(self, min=0, max=0):
        self.min = min
        self.max = max

        if not self.ticks_only:
            if self.orientation == "horizontal":
                self.canvas.create_line(self.x, self.y, self.x + self.length - 230, self.y,
                                        fill=cv._from_rgb((0,0,0)), width=self.line_tickness)
            elif self.orientation == "vertical":
                if self.negative_values:
                    self.canvas.create_line(self.x, self.y - self.length / 2, self.x, self.y + self.length / 2,
                                            fill=cv._from_rgb(self.color), width=self.line_tickness)
                else:
                    self.canvas.create_line(self.x, self.y, self.x, self.y - self.length,
                                            fill=cv._from_rgb((0,0,0)), width=self.line_tickness)

        for t in self.ticks:
            t.draw(value=0)

    def update(self, min=0, max=0):
        self.min = min
        self.max = max

        if self.negative_values:
            abs_max = max(abs(self.min), abs(self.max))
            rounded_max = math.ceil(abs_max / 10) * 10
            interval = rounded_max / 4
            tick_values = [interval * i for i in range(-4, 5)]
            tick_values = [v for v in tick_values if v >= self.min and v <= self.max]

            if self.min <= 0 <= self.max and 0 not in tick_values:
                tick_values.append(0)
                tick_values.sort()
        else:
            interval = (self.max - self.min) / 4
            tick_values = [self.min + interval * i for i in range(5)]
            tick_values = [v for v in tick_values if v <= self.max]

        for i, v in enumerate(tick_values):
            if i < len(self.ticks):
                self.ticks[i].update(value=v, draw=True)
                if self.negative_values and v < 0:
                    self.canvas.itemconfig(self.ticks[i].text, text=f"-{abs(v):.{self.decimal_places}f}{self.unit}")
                if self.negative_values and v == 0:
                    zero_color = cv._from_rgb((150, 150, 150))
                    self.canvas.itemconfig(self.ticks[i].text, fill=zero_color)
                    self.canvas.itemconfig(self.ticks[i].line, fill=zero_color)
                else:
                    normal_color = cv._from_rgb(self.color)
                    self.canvas.itemconfig(self.ticks[i].text, fill=normal_color)
                    self.canvas.itemconfig(self.ticks[i].line, fill=normal_color)

        for j in range(len(tick_values), len(self.ticks)):
            self.ticks[j].update(value=1, draw=False)

    def calc_positions(self, value):
        if self.min == 0 and self.max == 0:
            self.max = 0.1

        if not self.is_date:
            if not self.is_log_scale:
                if self.negative_values:
                    total_range = abs(self.max - self.min)
                    if total_range == 0:
                        return 0
                    if self.orientation == "vertical":
                        return (self.length / 2) * (value / self.max) if value >= 0 else -(self.length / 2) * (
                                    value / self.min)
                    else:
                        return self.length * (value - self.min) / (self.max - self.min)
                else:
                    return self.length * (value - self.min) / (self.max - self.min)
            else:
                return self.length * math.log10(value) / (math.log10(self.max) - math.log10(self.min))
        else:
            try:
                return self.length * (value - self.min_date) / (self.max_date - self.min_date)
            except ZeroDivisionError:
                return 0

class tick():
    def __init__(self, canvas, axis=None, length=0, label_pos="s", tick_prefix=""):
        self.canvas = canvas
        self.axis = axis
        self.length = length
        self.label_pos = label_pos
        self.tick_prefix = tick_prefix
        self.font = font.Font(family=self.axis.text_font, size=int(self.axis.font_size) + 3, weight="bold")

    def draw(self, value=0):
        self.line = self.canvas.create_line(-1, -1, -1, -1, fill=cv._from_rgb(self.axis.color),
                                            width=self.axis.line_tickness)
        self.text = self.canvas.create_text(-1, -1, text="", anchor="n", fill=cv._from_rgb(self.axis.color),
                                            font=self.font)

        # Create gridline if needed
        if self.axis.show_gridlines and self.axis.orientation == "vertical":
            grid_color = blend_with_white(self.axis.gridline_color, self.axis.gridline_opacity)
            self.gridline = self.canvas.create_line(-1, -1, -1, -1, fill=grid_color, dash=(2, 2))

    def update(self, value=0, draw=True, l=0):
        pos = self.axis.calc_positions(value)
        if draw:
            if self.axis.is_date:
                t = datetime.datetime(1800, 1, 1) + datetime.timedelta(days=value)
                label = cv.format_date(t, self.axis.time_indicator)
            else:
                label = f"{abs(value):,.{self.axis.decimal_places}f}"

            # Extract unit prefix and suffix
            unit_prefix, unit_suffix = self.axis.unit

            # Update tick line position and label
            if self.axis.orientation == "horizontal":
                self.canvas.coords(self.line, self.axis.x + pos, self.axis.y - self.length - l,
                                   self.axis.x + pos, self.axis.y + 10)
                self.canvas.itemconfig(self.text, text=self.tick_prefix + unit_prefix + label + unit_suffix)
                if self.label_pos == "s":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y + 11)
                elif self.label_pos == "n":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y - self.length - 1)
                    self.canvas.itemconfig(self.text, anchor="s")

            elif self.axis.orientation == "vertical":
                y_pos = self.axis.y - pos
                self.canvas.coords(self.line, self.axis.x - 10, y_pos, self.axis.x + self.length, y_pos)
                self.canvas.itemconfig(self.text, text=self.tick_prefix + unit_prefix + label + unit_suffix)
                if self.label_pos in ["s", "w"]:
                    self.canvas.coords(self.text, self.axis.x - 15, y_pos)
                    self.canvas.itemconfig(self.text, anchor="e")
                elif self.label_pos == "e":
                    self.canvas.coords(self.text, self.axis.x + self.length + 1, y_pos)
                    self.canvas.itemconfig(self.text, anchor="w")

                if self.axis.show_gridlines and y_pos != self.axis.y:
                    grid_color = blend_with_white(self.axis.gridline_color, self.axis.gridline_opacity)
                    gridline_end = self.axis.x + self.axis.length + 180
                    self.canvas.coords(self.gridline, self.axis.x, y_pos, gridline_end, y_pos)
                    self.canvas.itemconfig(self.gridline, fill=grid_color)
                    self.canvas.tag_lower(self.gridline)
                else:
                    self.canvas.coords(self.gridline, -1, -1, -1, -1)

            self.canvas.tag_raise(self.line)
        else:
            self.canvas.coords(self.line, -1, -1, -1, -1)
            self.canvas.itemconfig(self.text, text="")
            if hasattr(self, "gridline"):
                self.canvas.coords(self.gridline, -1, -1, -1, -1)