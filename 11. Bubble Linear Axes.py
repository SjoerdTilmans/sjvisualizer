"""Bubble Linear Axes with generated data.

Run: python "11. Bubble Linear Axes.py" --seconds 12 --fps 30
Use --smoke to render a few frames in a hidden Tk window and exit.
"""
import argparse
import tkinter

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, Bubble


def demo_data(frames):
    """Generate smooth, positive time series without external files."""
    t = np.linspace(0, 4 * np.pi, frames)
    return pd.DataFrame(
        {"Solar": 30 + 20 * np.sin(t) + t * 3,
         "Wind": 35 + 25 * np.cos(t * .7),
         "Hydro": 40 + 15 * np.sin(t + 1)},
        index=pd.date_range("2000-01-01", "2025-01-01", periods=frames),
    )


def build_chart(cv, df, args=None):
    """Configure this example using the public chart API."""
    # All three frames share the same dates and categories.
    t = np.linspace(0, 2 * np.pi, len(df))
    x = pd.DataFrame({name: 55 + 40 * np.sin(t + i)
                      for i, name in enumerate(df.columns)}, index=df.index)
    y = pd.DataFrame({name: 55 + 40 * np.cos(t + i * .7)
                      for i, name in enumerate(df.columns)}, index=df.index)
    # Bubble area, rather than diameter, represents this linear size variable.
    size = pd.DataFrame({name: 50 + 30 * np.sin(t + i * .5)
                         for i, name in enumerate(df.columns)}, index=df.index)
    return Bubble.bubble_chart(
        canvas=cv, x_pos=100, y_pos=150,
        width=900, height=450, font_size=18,
        df_x=x, df_y=y, df_size=size, x_log=False, y_log=False,
        max_bubble_size=65, display_label=not (args and args.no_labels),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=12)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--smoke", action="store_true",
                        help="Render initial, middle, final, and initial frames, then exit")
    parser.add_argument("--no-labels", action="store_true")
    args = parser.parse_args()
    if not np.isfinite(args.seconds) or args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")
    frames = max(2, int(args.seconds * args.fps))
    df = demo_data(frames)
    cv = Canvas.canvas(width=1200, height=800, include_logo=False)
    cv.tk.attributes("-fullscreen", False)
    cv.tk.title("SJVisualizer - Bubble Linear Axes")
    if args.smoke:
        cv.tk.withdraw()
    try:
        cv.add_title("Bubble Linear Axes")
        chart = build_chart(cv, df, args=args)
        cv.add_sub_plot(chart)
        cv.add_time(df, time_indicator="year")
        if args.smoke:
            for frame in (0, len(df) // 2, len(df) - 1, 0):
                cv.update(df.index[frame])
            print("Bubble Linear Axes: render smoke passed")
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
