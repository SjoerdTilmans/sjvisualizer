import datetime as dt
import numpy as np
import pandas as pd
from sjvisualizer import Canvas, LineChart

idx = [dt.datetime(2000, 1, 1) + dt.timedelta(days=i) for i in range(600)]

# y-values
df_y = pd.DataFrame(
    {
        "A": np.linspace(0, 100, len(idx)),
        "B": np.linspace(80, 20, len(idx)),
    },
    index=idx,
)

# x-values per series (same index, same columns)
df_x = pd.DataFrame(
    {
        "A": np.linspace(0, 1, len(idx)) ** 2,   # curved progression
        "B": np.linspace(0, 1, len(idx)),        # linear progression
    },
    index=idx,
)

cv = Canvas.canvas()
chart = LineChart.line_chart(
    df=df_y,
    x_df=df_x,               # <-- numeric x-axis mode
    canvas=cv,
    x_pos=100,
    y_pos=150,
    width=1400,
    height=800,
    x_decimal_places=2,
    y_decimal_places=0,
    draw_points=True,
)
cv.add_sub_plot(chart)
cv.play(df=df_y, fps=60, record=False)