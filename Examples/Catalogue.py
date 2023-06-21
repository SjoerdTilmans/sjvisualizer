from sjvisualizer import Canvas
from sjvisualizer import DataHandler
from sjvisualizer import BarRace
from sjvisualizer import PieRace
from sjvisualizer import Date
from sjvisualizer import StackedBarChart
from sjvisualizer import StaticImage
import time
import json

def main(fps = 60, duration = 0.35):

    number_of_frames = duration*60*fps

    # load colors
    with open('colors/colors.json') as f:
        colors = json.load(f)

    df = DataHandler.DataHandler(excel_file="data/browsers.xlsx", number_of_frames=number_of_frames).df

    canvas = Canvas.canvas()

    width = int(canvas.canvas["width"])
    height = int(canvas.canvas["height"])

    # add bar chart
    bar_chart = BarRace.bar_race(canvas=canvas.canvas, df=df, title="Bar race", colors=colors, height=int(height/2.5), width=int(width/6), x_pos=int(height/3/2), y_pos=int(width/5)/2)
    canvas.add_sub_plot(bar_chart)

    # add pie chart
    pie_plot = PieRace.pie_plot(canvas=canvas.canvas, df=df, title="Pie race", colors=colors, height=int(height / 2.5),
                                 width=int(width / 6), x_pos=int(height / 3 / 2 * 3), y_pos=int(width / 5) / 2)
    canvas.add_sub_plot(pie_plot)

    # add stacked bar chart
    stacked = StackedBarChart.stacked_bar_chart(canvas=canvas.canvas, df=df, title="Stacked", colors=colors, height=int(height / 2.5),
                                 width=int(width / 6), x_pos=int(height / 3 / 2 * 5.5), y_pos=int(width / 5) / 2)
    canvas.add_sub_plot(stacked)

    # add time indication
    date = Date.date(canvas=canvas.canvas, height=int(height / 20),
                                 width=int(width / 20), x_pos=int(height / 3 / 2 * 8), y_pos=int(width / 5), time_indicator="month", df=df)
    canvas.add_sub_plot(date)

    # adding a static image
    img = StaticImage.static_image(canvas=canvas.canvas, file="assets/Made with SJvisualzer.png", width=height/10, height=height/10, x_pos=width/2, y_pos=height/1.4)
    canvas.add_sub_plot(img)

    # save colors for next run
    with open("colors/colors.json", "w") as file:
        json.dump(colors, file, indent=4)

    canvas.play(fps=fps)

if __name__ == "__main__":
    main()