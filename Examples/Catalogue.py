from pathlib import Path
import sys

# Run against the sjvisualizer package in this checkout, even when this file is
# launched directly from the Examples directory or another working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from sjvisualizer import Canvas
from sjvisualizer import DataHandler
from sjvisualizer import BarRace
from sjvisualizer import PieRace
from sjvisualizer import Date
from sjvisualizer import StackedBarChart
from sjvisualizer import StaticImage
from sjvisualizer import LineChart
from sjvisualizer import AreaChart
import time
import json

def main(fps = 60, duration = 0.35):

    number_of_frames = duration*60*fps

    # load colors
    with (EXAMPLE_DIR / "colors" / "colors.json").open() as f:
        colors = json.load(f)

    df = DataHandler.DataHandler(
        excel_file=EXAMPLE_DIR / "Data" / "browsers.xlsx",
        number_of_frames=number_of_frames,
    ).df

    canvas = Canvas.canvas()

    width = int(canvas.canvas["width"])
    height = int(canvas.canvas["height"])

    chart_height = int(height/3.5)

    # add bar chart
    bar_chart = BarRace.bar_race(canvas=canvas.canvas, df=df, title="Bar race", colors=colors, height=chart_height, width=int(width/6), x_pos=int(height/3/2), y_pos=int(width/5)/2)
    canvas.add_sub_plot(bar_chart)

    # add pie chart
    pie_plot = PieRace.pie_plot(canvas=canvas.canvas, df=df, title="Pie race", colors=colors, height=chart_height,
                                 width=int(width / 6), x_pos=int(height / 3 / 2 * 3), y_pos=int(width / 5) / 2)
    canvas.add_sub_plot(pie_plot)

    # add stacked bar chart
    stacked = StackedBarChart.stacked_bar_chart(canvas=canvas.canvas, df=df, title="Stacked", colors=colors, height=chart_height,
                                 width=int(width / 6), x_pos=int(height / 3 / 2 * 5.5), y_pos=int(width / 5) / 2, number_of_bars=25)
    canvas.add_sub_plot(stacked)

    # creating events for the line chart
    events = {
        "Event 1": ["28/01/1998", "28/01/2000"],
        "Event 2": ["28/01/2018", "28/01/2019"]
    }

    # add a line chart
    line = LineChart.line_chart(canvas=canvas, df=df, title="Line chart", colors=colors, height=chart_height,
                                 width=int(width / 6), x_pos=int(height/3/2), y_pos=int(width / 5) + 1.05*chart_height, events=events)
    canvas.add_sub_plot(line)

    # add an area chart
    area = AreaChart.area_chart(canvas=canvas, df=df, title="Area chart", colors=colors, height=chart_height,
                                width=int(width / 6), x_pos=int(height / 3 * 2),
                                y_pos=int(width / 5) + 1.05 * chart_height,
                                label_position="right")
    canvas.add_sub_plot(area)

    # add time indication
    date = Date.date(canvas=canvas.canvas, height=int(height / 20),
                                 width=int(width / 20), x_pos=int(height / 3 / 2 * 8), y_pos=int(width / 5), time_indicator="month", df=df)
    canvas.add_sub_plot(date)

    # adding a static image
    img = StaticImage.static_image(canvas=canvas.canvas, file=str(EXAMPLE_DIR / "assets" / "Made with SJvisualzer.png"), width=height/20, height=height/20, x_pos=width/3*2.25, y_pos=height/1.4)
    canvas.add_sub_plot(img)

    # save colors for next run
    with (EXAMPLE_DIR / "colors" / "colors.json").open("w") as file:
        json.dump(colors, file, indent=4)

    canvas.play(fps=fps)

if __name__ == "__main__":
    main()
