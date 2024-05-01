from sjvisualizer import Canvas
from sjvisualizer import DataHandler
from sjvisualizer import BarRace
from sjvisualizer import Date
import time
import json

def main(fps = 60, duration = 0.35):

    number_of_frames = duration*60*fps

    # load colors
    with open('colors/colors.json') as f:
        colors = json.load(f)

    df = DataHandler.DataHandler(excel_file="data/Insta.xlsx", number_of_frames=number_of_frames).df

    canvas = Canvas.canvas()

    # add bar chart
    bar_chart = BarRace.bar_race(canvas=canvas.canvas, df=df, colors=colors, height=720, width=720, x_pos=175, y_pos=200, back_ground_color=(255,0,0))
    canvas.add_sub_plot(bar_chart)

    # add static text
    static_text = canvas.canvas.create_text(720/2 + 150, 100, text="Most Followed Instagram Accounts", font=("Purisa", 30))

    # add time indication
    date = Date.date(canvas=canvas.canvas, x_pos=250, y_pos=1000, width=0, height=50, time_indicator="month", df=df)
    canvas.add_sub_plot(date)

    square = canvas.canvas.create_rectangle(0, 0, 1080, 1080)

    # save colors for next run
    with open("colors/colors.json", "w") as file:
        json.dump(colors, file, indent=4)

    canvas.play(fps=fps)

if __name__ == "__main__":
    main()