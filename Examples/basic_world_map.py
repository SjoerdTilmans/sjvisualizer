from sjvisualizer import Canvas
from sjvisualizer import DataHandler
from sjvisualizer import WorldMap
from sjvisualizer import Date
import time
import json

def main(fps = 30, duration = 0.1):

    number_of_frames = duration*60*fps

    with open('colors/colors.json') as f:
        colors = json.load(f)

    df = DataHandler.DataHandler(excel_file="data/Coffee Production.xlsx", number_of_frames=number_of_frames).df

    canvas = Canvas.canvas()

    # add bar chart
    map = WorldMap.world_map(canvas=canvas, df=df, colors=colors, time_indicator="month", color_bar_color=[[210,210,210], [100,40,10]], unit=" MTonnes")
    canvas.add_sub_plot(map)

    d = Date.date(canvas=canvas, df=df, height=50)
    canvas.add_sub_plot(d)

    canvas.play(fps=fps)

if __name__ == "__main__":
    main()