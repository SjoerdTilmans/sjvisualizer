from sjvisualizer import Canvas, DataHandler, ColumnRace

df = DataHandler.DataHandler(excel_file="Examples/Data/browsers.xlsx", number_of_frames=60*10).df

canvas = Canvas.canvas()

empty_chart = ColumnRace.column_race(canvas=canvas, font_size=25, df=df, neutral_string="Neutral", level_count=3)
canvas.add_sub_plot(empty_chart)

canvas.add_time(df=df, time_indicator="day")
canvas.add_title("Dynamic Matrix")

canvas.play(fps=60)