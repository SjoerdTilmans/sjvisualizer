"""Log-log bubble demo. Run: python AITest_BubbleLog.py [--seconds 15 --fps 60]."""

import argparse

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, Bubble


def demo_data(frames):
    t = np.linspace(0, 2 * np.pi, frames)
    index = pd.date_range("2000-01-01", "2025-01-01", periods=frames)
    # Move through several orders of magnitude, keeping log coordinates positive.
    x = pd.DataFrame({f"Series {i + 1}": 10 ** (2 + 1.5 * np.sin(t + i))
                      for i in range(5)}, index=index)
    y = pd.DataFrame({f"Series {i + 1}": 10 ** (2 + 1.5 * np.cos(t + i * .7))
                      for i in range(5)}, index=index)
    # Bubble area uses a separate, linear size variable.
    size = pd.DataFrame({f"Series {i + 1}": 50 + 30 * np.sin(t + i * .5)
                         for i in range(5)}, index=index)
    return x, y, size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--fps", type=int, default=60)
    args = parser.parse_args()
    if args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")

    x, y, size = demo_data(max(2, args.seconds * args.fps))
    cv = Canvas.canvas(width=1200, height=800)
    cv.tk.attributes("-fullscreen", False)
    cv.tk.title("SJVisualizer - Log-log bubble demo")
    cv.add_title("Bubble chart - logarithmic X and Y")
    cv.add_sub_plot(Bubble.bubble_chart(
        canvas=cv, df_x=x, df_y=y, df_size=size,
        x_pos=110, y_pos=130, width=950, height=540, font_size=18,
        x_log=True, y_log=True, x_min=1, x_max=10000, y_min=1, y_max=10000,
        x_ticks=4, y_ticks=4, max_bubble_size=65, display_label=True,
    ))
    cv.play(df=x, fps=args.fps, record=False)
    cv.tk.mainloop()


if __name__ == "__main__":
    main()
