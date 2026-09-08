"""Dynamic Line with generated data.

Run: python "09. Dynamic Line.py" --seconds 12 --fps 30
Use --smoke to render a few frames in a hidden Tk window and exit.
"""
import argparse
import tkinter

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, DynamicLine


def demo_data(frames):
    """Generate smooth, positive time series without external files."""
    t = np.linspace(0, 4 * np.pi, frames)
    return pd.DataFrame(
        {"Solar": 30 + 20 * np.sin(t) + t * 3,
         "Wind": 35 + 25 * np.cos(t * .7),
         "Hydro": 40 + 15 * np.sin(t + 1)},
        index=pd.date_range("2000-01-01", "2025-01-01", periods=frames),
    )


def build_chart(cv, df):
    """Configure this example using the public chart API."""
    return DynamicLine.dynamic_curve(
        canvas=cv, df=df, x_pos=100, y_pos=150,
        width=900, height=450, font_size=18,
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
    cv.tk.title("SJVisualizer - Dynamic Line")
    if args.smoke:
        cv.tk.withdraw()
    try:
        cv.add_title("Dynamic Line")
        chart = build_chart(cv, df)
        cv.add_sub_plot(chart)
        cv.add_time(df, time_indicator="year")
        if args.smoke:
            for frame in (0, len(df) // 2, len(df) - 1, 0):
                cv.update(df.index[frame])
            print("Dynamic Line: render smoke passed")
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
