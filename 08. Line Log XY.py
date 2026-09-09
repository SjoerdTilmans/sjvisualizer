"""Line Log XY with generated data.

Run: python "08. Line Log XY.py" --seconds 12 --fps 30
Use --smoke to render a few frames in a hidden Tk window and exit.
"""
import argparse
import tkinter

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, LineChart


def demo_data(frames):
    """Positive values spanning several orders of magnitude."""
    return pd.DataFrame(
        {"Fast growth": np.geomspace(1, 10000, frames),
         "Slow growth": np.geomspace(10, 1000, frames)},
        index=pd.date_range("2000-01-01", "2025-01-01", periods=frames),
    )


def build_chart(cv, df):
    """Configure this example using the public chart API."""
    # These power laws become straight lines on log-log axes.
    x = pd.Series(np.geomspace(1, 100, len(df)), index=df.index)
    return LineChart.line_chart(
        canvas=cv, df=df, x_pos=100, y_pos=150,
        width=900, height=450, font_size=18,
        x_df=x, x_log=True, y_log=True,
        x_min=1, x_max=100, y_min=1, y_max=10000, draw_points=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=12)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--smoke", action="store_true",
                        help="Render initial, middle, final, and initial frames, then exit")
    args = parser.parse_args()
    if not np.isfinite(args.seconds) or args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")
    frames = max(2, int(args.seconds * args.fps))
    df = demo_data(frames)
    cv = Canvas.canvas(width=1200, height=800, include_logo=False)
    cv.tk.attributes("-fullscreen", False)
    cv.tk.title("SJVisualizer - Line Log XY")
    if args.smoke:
        cv.tk.withdraw()
    try:
        cv.add_title("Line Log XY")
        chart = build_chart(cv, df)
        cv.add_sub_plot(chart)
        cv.add_time(df, time_indicator="year")
        if args.smoke:
            for frame in (0, len(df) // 2, len(df) - 1, 0):
                cv.update(df.index[frame])
            print("Line Log XY: render smoke passed")
        else:
            cv.play(df=df, fps=args.fps)
            cv.tk.mainloop()
    finally:
        try:
            cv.tk.destroy()
        except tkinter.TclError:
            pass  # The window may already have been closed during playback.


if __name__ == "__main__":
    main()
