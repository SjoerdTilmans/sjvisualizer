"""Run: python AITest_Bubble.py [--seconds 15 --fps 60 --log --no-labels]."""
import argparse

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, Bubble


def demo_data(frames):
    t = np.linspace(0, 2*np.pi, frames)
    index = pd.date_range("2000-01-01", "2025-01-01", periods=frames)
    x = pd.DataFrame({f"Series {i+1}": 55+40*np.sin(t+i) for i in range(5)}, index=index)
    y = pd.DataFrame({f"Series {i+1}": 55+40*np.cos(t+i*.7) for i in range(5)}, index=index)
    size = pd.DataFrame({f"Series {i+1}": np.maximum(0, 30+40*np.sin(t+i*.5)) for i in range(5)}, index=index)
    return x, y, size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--no-labels", action="store_true")
    args = parser.parse_args()
    if args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")
    x, y, size = demo_data(max(2, args.seconds*args.fps))
    cv = Canvas.canvas(width=1200, height=800)
    cv.tk.attributes("-fullscreen", False)
    cv.tk.title("SJVisualizer - Bubble demo")
    cv.add_title("Bubble chart - synthetic data")
    cv.add_sub_plot(Bubble.bubble_chart(canvas=cv, df_x=x, df_y=y, df_size=size,
        x_pos=110, y_pos=130, width=950, height=540, font_size=18,
        x_log=args.log, y_log=args.log, display_label=not args.no_labels))
    cv.play(df=x, fps=args.fps)
    cv.tk.mainloop()


if __name__ == "__main__":
    main()
