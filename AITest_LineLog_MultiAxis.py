"""Logarithmic X and Y demo. Run: python AITest_LineLog_MultiAxis.py."""

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, LineChart


def main():
    idx = pd.date_range("2000-01-01", periods=600)
    x = pd.Series(np.geomspace(1, 100, len(idx)), index=idx)
    # Power laws appear as straight lines when both axes use log scales.
    df = pd.DataFrame({"x squared": x ** 2, "10 times x": 10 * x}, index=idx)
    cv = Canvas.canvas()
    chart = LineChart.line_chart(
        df=df, x_df=x, canvas=cv, x_pos=100, y_pos=150, width=1400, height=800,
        x_log=True, y_log=True, x_min=1, x_max=100, y_min=1, y_max=10000,
        draw_points=False,
    )
    cv.add_sub_plot(chart)
    cv.play(df=df, fps=60, record=False)


if __name__ == "__main__":
    main()
