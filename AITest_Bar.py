from sjvisualizer import DataHandler, Canvas, BarRace

dh = DataHandler.DataHandler(excel_file="sjvisualizerAI/data/Area Dev.xlsx", number_of_frames=60*60)

df = dh.df

colors = {
    "Instagram": (0,0,0)
}

c = Canvas.canvas()
chart = BarRace.bar_race(
    canvas=c,
    df=df,
    number_of_bars=17,
    colors=colors,
    title="Hello World!"
)
c.add_sub_plot(chart)

c.play(df=df, fps=60, record=False)