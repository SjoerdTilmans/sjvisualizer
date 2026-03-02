import datetime as dt
import numpy as np
import pandas as pd
from sjvisualizer import Canvas, LineChart

# time index (date axis)
idx = [dt.datetime(2000, 1, 1) + dt.timedelta(days=i) for i in range(120)]

df = pd.DataFrame(
    {
        "A": np.linspace(0, 100, len(idx)),
        "B": 50 + 20 * np.sin(np.linspace(0, 6, len(idx))),
    },
    index=idx,
)

cv = Canvas.canvas()
chart = LineChart.line_chart(
    df=df,
    canvas=cv,
    x_pos=100,
    y_pos=150,
    width=1400,
    height=800,
    time_indicator="year",   # "year" | "month" | "day"
    draw_points=True,
)
cv.add_sub_plot(chart)
cv.play(df=df, fps=15, record=False)