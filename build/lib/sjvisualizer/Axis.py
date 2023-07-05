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

class axis():
    def __init__(self, canvas, x=0, y=0, length=1000, width=1000, orientation="horizontal", n=3, allow_decrease=False, tick_length=0, is_log_scale=False, is_date=False, color=(50,50,50), font_size=20, text_font="Microsoft JhengHei UI", time_indicator="year", line_tickness=3, ticks_only=True, unit=""):
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

        self.min = None
        self.max = None

        self.ticks = []
        for i in range(self.n * 3):
            self.ticks.append(tick(self.canvas, axis=self, length=tick_length))

    def draw(self, min=0, max=0):
        self.min = min
        self.max = max
        if not self.ticks_only:
            if self.orientation == "horizontal":
                self.canvas.create_line(self.x, self.y, self.x+self.length, self.y, fill=cv._from_rgb(self.color), width=self.line_tickness)
            elif self.orientation == "vertical":
                self.canvas.create_line(self.x, self.y, self.x, self.y-self.length, fill=cv._from_rgb(self.color), width=self.line_tickness)

        if not self.allow_decrease:
            if self.min > min:
                self.min = min
        else:
            self.min = min

        if not self.allow_decrease:
            if self.max < max:
                self.max = max
        else:
            self.max = max

        for t in self.ticks:
            t.draw(value=0)

    def update(self, min=0, max=0):

        if not self.allow_decrease:
            if self.min > min:
                self.min = min
        else:
            self.min = min

        if not self.allow_decrease:
            if self.max < max:
                self.max = max
        else:
            self.max = max

        if not self.is_date:
            tick_values = calculate_nice_ticks(self.min, self.max, self.n, is_log_scale=self.is_log_scale)
            for i, v in enumerate(tick_values):
                if v < self.min or v > self.max:
                    self.ticks[i].update(value=1, draw=False)
                else:
                    if v == 0:
                        self.ticks[i].update(value=v, draw=True, l=self.width)
                    else:
                        self.ticks[i].update(value=v, draw=True)
            if not "i" in locals():
                i = 0

            for j in range(i, self.n * 3):
                self.ticks[j].update(value=1, draw=False)
        else:
            self.min_date = (min - datetime.datetime(1800,1,1)).days
            self.max_date = (max - datetime.datetime(1800,1,1)).days
            if self.min_date == self.max_date:
                tick_values = []
            else:
                tick_values = calculate_nice_ticks(self.min_date, self.max_date, self.n, is_log_scale=self.is_log_scale)

                spacing = tick_values[1] - tick_values[0]
                number_of_ticks = len(tick_values)

                tick_values = [self.min_date]

                for k in range(number_of_ticks):
                    tick_values.append(tick_values[-1] + spacing)

                for i, v in enumerate(tick_values):
                    if v < self.max_date:
                        self.ticks[i].update(value=v, draw=True)
                    else:
                        self.ticks[i].update(value=1, draw=True)
                if not "i" in locals():
                    i = 0

                for j in range(i, self.n * 3):
                    self.ticks[j].update(value=1, draw=False)

    def calc_positions(self, value):
        if not self.is_date:
            if not self.is_log_scale:
                return self.length * (value - self.min) / (self.max - self.min)
            else:
                return self.length * math.log10(value) / (math.log10(self.max) - math.log10(self.min))
        else:
            try:
                return self.length * (value - self.min_date) / (self.max_date - self.min_date)
            except ZeroDivisionError:
                return 0

class tick():

    def __init__(self, canvas, axis=None, length=0, label_pos="s"):
        self.canvas = canvas
        self.axis = axis
        self.length = length
        self.label_pos = label_pos
        self.font = font.Font(family=self.axis.text_font, size=int(self.axis.font_size))

    def draw(self, value=0):
        self.line = self.canvas.create_line(-1, -1, -1, -1, fill=cv._from_rgb(self.axis.color), width=self.axis.line_tickness)
        self.text = self.canvas.create_text(-1, -1, text="", anchor="n", fill=cv._from_rgb(self.axis.color), font=self.font)

    def update(self, value=0, draw=True, l=0):
        pos = self.axis.calc_positions(value)
        if draw:
            if self.axis.is_date:
                t = datetime.datetime(1800,1,1) + datetime.timedelta(days=value)
                label = cv.format_date(t, self.axis.time_indicator)
            else:
                label = str(value)
            if self.axis.orientation == "horizontal":
                self.canvas.coords(self.line, self.axis.x + pos, self.axis.y - self.length - l, self.axis.x + pos, self.axis.y + 10)
                self.canvas.itemconfig(self.text, text=label + self.axis.unit)
                if self.label_pos == "s":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y + 11)
                elif self.label_pos == "n":
                    self.canvas.coords(self.text, self.axis.x + pos, self.axis.y - self.length - 1)
                    self.canvas.itemconfig(anchor="s")

            elif self.axis.orientation == "vertical":
                if l:
                    self.canvas.coords(self.line, self.axis.x - 10, self.axis.y - pos, self.axis.x + self.length + l, self.axis.y - pos)
                else:
                    self.canvas.coords(self.line, self.axis.x - 10, self.axis.y - pos, self.axis.x + self.length, self.axis.y - pos)
                self.canvas.itemconfig(self.text, text=label + self.axis.unit)
                if self.label_pos == "s" or self.label_pos == "w":
                    self.canvas.coords(self.text, self.axis.x - 11, self.axis.y - pos)
                    self.canvas.itemconfig(self.text, anchor="e")
                elif self.label_pos == "e":
                    self.canvas.coords(self.text, self.axis.x + self.length + 1, self.axis.y - pos)
                    self.canvas.itemconfig(self.text, anchor="w")
            self.canvas.tag_raise(self.line)

        else:
            self.canvas.coords(self.line, -1, -1, -1, -1)
            self.canvas.itemconfig(self.text, text="")


def calculate_nice_ticks(min_val, max_val, num_ticks, is_log_scale=False):
    if is_log_scale:
        min_val = math.log10(min_val)
        max_val = math.log10(max_val)

    # Calculate the rough range
    rough_range = max_val - min_val

    # Calculate the rough tick increment
    rough_tick_incr = rough_range / num_ticks

    # Calculate the exponent of the rough tick increment in base 10
    exponent = math.floor(math.log10(rough_tick_incr))

    # Calculate the nice tick increment
    nice_tick_incr = 10 ** exponent
    if rough_tick_incr / nice_tick_incr < 1.5:
        nice_tick_incr *= 1
    elif rough_tick_incr / nice_tick_incr < 3:
        nice_tick_incr *= 2
    else:
        nice_tick_incr *= 5

    # Calculate the nice minimum value
    nice_min_val = nice_tick_incr * math.floor(min_val / nice_tick_incr)

    # Calculate the number of ticks needed to cover the range
    num_ticks = math.ceil((max_val - nice_min_val) / nice_tick_incr)

    # Calculate the adjusted maximum value
    nice_max_val = nice_min_val + num_ticks * nice_tick_incr

    # Generate the nice tick values
    tick_values = []
    current_val = nice_min_val
    while current_val <= nice_max_val:
        tick_values.append(current_val)
        current_val += nice_tick_incr

    if is_log_scale:
        tick_values = [10 ** val for val in tick_values]

    return tick_values