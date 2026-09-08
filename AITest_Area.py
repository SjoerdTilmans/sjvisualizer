"""Run: python AITest_Area.py [--seconds 15 --fps 60 --excel path.xlsx]."""
import argparse

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, DataHandler, AreaChart


def demo_data(frames):
    t = np.linspace(0, 3*np.pi, frames)
    return pd.DataFrame({"Solar": 15+10*np.sin(t)+t*5,
                         "Wind": 25+15*np.cos(t*.8),
                         "Hydro": 30+8*np.sin(t+1)},
                        index=pd.date_range("2000-01-01", "2025-01-01", periods=frames))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--excel", help="Optional time-indexed Excel dataset")
    args = parser.parse_args()
    if args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")
    frames = max(2, args.seconds*args.fps)
    df = DataHandler.DataHandler(excel_file=args.excel, number_of_frames=frames).df if args.excel else demo_data(frames)
    cv = Canvas.canvas(width=1200, height=800)
    cv.tk.attributes("-fullscreen", False)
    cv.tk.title("SJVisualizer - Area demo")
    cv.add_title("Stacked area - " + ("Your data" if args.excel else "synthetic data"))
    cv.add_sub_plot(AreaChart.area_chart(canvas=cv, df=df, x_pos=100, y_pos=150,
        width=800, height=520, font_size=18, display_values=True, label_position="right",
        events={} if args.excel else {"Example event": ["01/01/2010", "01/01/2013"]}, log=True))
    cv.play(df=df, fps=args.fps)
    cv.tk.mainloop()


if __name__ == "__main__":
    main()
