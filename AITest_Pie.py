"""Run with python AITest_Pie.py using the bundled portrait images.

The default values are synthetic demo data, not real audience statistics.
For Excel data, put matching <column name>.png images in the assets folder.

Examples: python AITest_Pie.py --seconds 5 --fps 30
          python AITest_Pie.py --excel tests/Data/browsers.xlsx
          python AITest_Pie.py --solid --no-sort
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from sjvisualizer import Canvas, DataHandler, PieRace, sub_plot


class _DemoDate(sub_plot):
    """Small date caption while the legacy Date chart awaits migration."""

    def draw(self, time_obj):
        self.item = self.canvas.create_text(
            self.x_pos, self.y_pos, font=("Arial", 20), fill="grey")
        self.update(time_obj)

    def update(self, time_obj):
        self.canvas.itemconfig(self.item, text=pd.Timestamp(time_obj).strftime("%Y-%m"))


def demo_data(frames):
    """Synthetic shares with rank changes and a disappearing category."""
    t = np.linspace(0, 2*np.pi, frames)
    return pd.DataFrame({
        "Dwayne Johnson": 30 + 23*np.sin(t),
        "Justin Bieber": 28 + 20*np.cos(t),
        "Kendall Jenner": 18 + 10*np.sin(t + 1),
        "Nicki Minaj": np.maximum(0, 20*np.sin(t - 1)),
        "Other": np.full(frames, 2.0),
    }, index=pd.date_range("2000-01-01", "2025-01-01", periods=frames))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel", help="Optional time-indexed Excel dataset")
    parser.add_argument("--seconds", type=int, default=20)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--solid", action="store_true")
    parser.add_argument("--no-sort", action="store_true")
    args = parser.parse_args()
    if args.seconds <= 0 or args.fps <= 0:
        parser.error("seconds and fps must be positive")
    frames = max(2, args.seconds * args.fps)
    df = DataHandler.DataHandler(excel_file=args.excel, number_of_frames=frames).df if args.excel else demo_data(frames)
    cv = Canvas.canvas()
    cv.tk.attributes("-fullscreen", True)
    cv.tk.title("SJVisualizer — PieRace demo")
    cv.add_title("Pie Race — " + ("Your data" if args.excel else "Portrait demo (synthetic data)"))
    chart = PieRace.pie_plot(
        canvas=cv, df=df, font_size=20, sort=not args.no_sort,
        inner_radius=0 if args.solid else 0.5,
        display_images=True, assets_dir=Path(__file__).resolve().parent / "assets",
    )
    cv.add_sub_plot(chart)
    cv.add_sub_plot(_DemoDate(canvas=cv, df=df, x_pos=550, y_pos=745))
    cv.play(df=df, fps=args.fps)
    cv.tk.mainloop()


if __name__ == "__main__":
    main()
