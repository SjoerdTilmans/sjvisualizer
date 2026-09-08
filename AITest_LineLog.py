"""Date X / logarithmic Y demo. Run: python AITest_LineLog.py."""

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, LineChart


def main():
    idx = pd.date_range("2000-01-01", periods=600)
    df = pd.DataFrame({"Fast growth": np.geomspace(1, 10000, len(idx)),
                       "Slow growth": np.geomspace(10, 1000, len(idx))}, index=idx)
    cv = Canvas.canvas()
    chart = LineChart.line_chart(
        df=df, canvas=cv, x_pos=100, y_pos=150, width=1400, height=800,
        y_log=True, y_min=1, y_max=10000, time_indicator="month",
        draw_points=False,
    )
    cv.add_sub_plot(chart)
    cv.play(df=df, fps=60, record=False)


if __name__ == "__main__":
    main()
