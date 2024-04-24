from sjvisualizer import DataHandler, Canvas
from sjvisualizer import BarRace, PieRace, LineChart, AreaChart, WorldMap
import os

def bar(excel="", title="", sub_title="", duration=1, fps=60, record=False, output_video="output.mp4", unit="", time_indicator="year", font_color=(0, 0, 0), background_color=(255, 255, 255), colors={}, n=8):
    """Function to create a bar chart race

        :param excel: excel file containing the data
        :type excel: string

        :param title: title on top of the animation
        :type title: string

        :param sub_title: sub-title to provide extra context, displayed just under the main title
        :type sub_title: string

        :param duration: length of the animation
        :type duration: integer

        :param fps: number of frames per second
        :type fps: integer

        :param record: should the animation be saved as an mp4? Defaults to False. If set to True, the render speed on screen is reduced, however, the playback speed of the video is correct.
        :type record: boolean

        :param output_video: name of the saved video.
        :type record: string

        :param unit: unit to be displayed in the graph
        :type record: string

        :param time_indicator: should the time format show year, month or day
        :type time_indicator: string, 'day', 'month', or 'year'

        :param font_color: color of the texts rendered to the screen. In RGB colors.
        :type font_color: tuple (R, G, B)

        :param background_color: color of the background. In RGB colors.
        :type background_color: tuple (R, G, B)

        :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
            corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
                {
                    "United States": [
                        23,
                        60,
                        225
                    ]
                }, default is {}
        :type colors: dict

        :param n: number of bars to display
        :type n: integer
    """

    if not os.path.exists(excel):
        raise FileNotFoundError("Please provide a valid Excel file")

    # creating the dataframe
    df = DataHandler.DataHandler(excel_file=excel, number_of_frames=fps*duration*60).df

    # creating the canvas
    canvas = Canvas.canvas(bg=background_color)

    # creating the bar_race
    b = BarRace.bar_race(canvas=canvas, df=df, number_of_bars=n, colors=colors, font_color=font_color, back_ground_color=background_color, unit=unit)
    canvas.add_sub_plot(b)

    # adding title
    canvas.add_title(text=title, color=font_color)

    # adding sub-title
    canvas.add_sub_title(text=sub_title, color=font_color)

    # adding time indicator
    canvas.add_time(df=df, time_indicator=time_indicator, color=font_color)

    # play the animation
    canvas.play(fps=fps, record=record, file_name=output_video)

def world_map(excel="", title="", sub_title="", duration=1, fps=60, record=False, output_video="output.mp4", unit="", time_indicator="year", font_color=(0, 0, 0), background_color=(255, 255, 255), colors={}, color_bar_color=[[210,210,210], [100,40,10]]):
    """Function to create a bar chart race

        :param excel: excel file containing the data
        :type excel: string

        :param title: title on top of the animation
        :type title: string

        :param sub_title: sub-title to provide extra context, displayed just under the main title
        :type sub_title: string

        :param duration: length of the animation
        :type duration: integer

        :param fps: number of frames per second
        :type fps: integer

        :param record: should the animation be saved as an mp4? Defaults to False. If set to True, the render speed on screen is reduced, however, the playback speed of the video is correct.
        :type record: boolean

        :param output_video: name of the saved video.
        :type record: string

        :param unit: unit to be displayed in the graph
        :type record: string

        :param time_indicator: should the time format show year, month or day
        :type time_indicator: string, 'day', 'month', or 'year'

        :param font_color: color of the texts rendered to the screen. In RGB colors.
        :type font_color: tuple (R, G, B)

        :param background_color: color of the background. In RGB colors.
        :type background_color: tuple (R, G, B)

        :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
            corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
                {
                    "United States": [
                        23,
                        60,
                        225
                    ]
                }, default is {}
        :type colors: dict

        :param color_bar_color: list that holds start and end color of color bar in RGB values, example: color_bar_color=[[210,210,210], [100,40,10]]
        :type color_bar_color: list[lists]
    """

    if not os.path.exists(excel):
        raise FileNotFoundError("Please provide a valid Excel file")

    # creating the dataframe
    df = DataHandler.DataHandler(excel_file=excel, number_of_frames=fps*duration*60).df

    # creating the canvas
    canvas = Canvas.canvas(bg=background_color)

    # creating the bar_race
    map = WorldMap.world_map(canvas=canvas, df=df, colors=colors, font_color=font_color, back_ground_color=background_color, unit=unit, color_bar_color=color_bar_color)
    canvas.add_sub_plot(map)

    # adding title
    canvas.add_title(text=title, color=font_color)

    # adding sub-title
    canvas.add_sub_title(text=sub_title, color=font_color)

    # adding time indicator
    canvas.add_time(df=df, time_indicator=time_indicator, color=font_color)

    # play the animation
    canvas.play(fps=fps, record=record, file_name=output_video)

def pie(excel="", title="", sub_title="", duration=1, fps=60, record=False, output_video="output.mp4", unit="", time_indicator="year", font_color=(0, 0, 0), background_color=(255, 255, 255), colors={}, sort=True):
    """Function to create a bar chart race

        :param excel: excel file containing the data
        :type excel: string

        :param title: title on top of the animation
        :type title: string

        :param sub_title: sub-title to provide extra context, displayed just under the main title
        :type sub_title: string

        :param duration: length of the animation
        :type duration: integer

        :param fps: number of frames per second
        :type fps: integer

        :param record: should the animation be saved as an mp4? Defaults to False. If set to True, the render speed on screen is reduced, however, the playback speed of the video is correct.
        :type record: boolean

        :param output_video: name of the saved video.
        :type record: string

        :param unit: unit to be displayed in the graph
        :type record: string

        :param time_indicator: should the time format show year, month or day
        :type time_indicator: string, 'day', 'month', or 'year'

        :param font_color: color of the texts rendered to the screen. In RGB colors.
        :type font_color: tuple (R, G, B)

        :param background_color: color of the background. In RGB colors.
        :type background_color: tuple (R, G, B)

        :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
            corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
                {
                    "United States": [
                        23,
                        60,
                        225
                    ]
                }, default is {}
        :type colors: dict

        :param sort: should the data be sorted by descending order?
        :type sort: boolean
    """

    if not os.path.exists(excel):
        raise FileNotFoundError("Please provide a valid Excel file")

    # creating the dataframe
    df = DataHandler.DataHandler(excel_file=excel, number_of_frames=fps*duration*60).df

    # creating the canvas
    canvas = Canvas.canvas(bg=background_color)

    # creating the bar_race
    p = PieRace.pie_plot(canvas=canvas, df=df, colors=colors, font_color=font_color, back_ground_color=background_color, sort=sort, unit=unit)
    canvas.add_sub_plot(p)

    # adding title
    canvas.add_title(text=title, color=font_color)

    # adding sub-title
    canvas.add_sub_title(text=sub_title, color=font_color)

    # adding time indicator
    canvas.add_time(df=df, time_indicator=time_indicator, color=font_color)

    # play the animation
    canvas.play(fps=fps, record=record, file_name=output_video)

def line(excel="", title="", sub_title="", duration=1, fps=60, record=False, output_video="output.mp4", unit="", time_indicator="year", events={}, font_color=(0, 0, 0), background_color=(255, 255, 255), colors={}):
    """Function to create a bar chart race

        :param excel: excel file containing the data
        :type excel: string

        :param title: title on top of the animation
        :type title: string

        :param sub_title: sub-title to provide extra context, displayed just under the main title
        :type sub_title: string

        :param duration: length of the animation
        :type duration: integer

        :param fps: number of frames per second
        :type fps: integer

        :param record: should the animation be saved as an mp4? Defaults to False. If set to True, the render speed on screen is reduced, however, the playback speed of the video is correct.
        :type record: boolean

        :param output_video: name of the saved video.
        :type record: string

        :param unit: unit to be displayed in the graph
        :type record: string

        :param time_indicator: should the time format show year, month or day
        :type time_indicator: string, 'day', 'month', or 'year'

        :param font_color: color of the texts rendered to the screen. In RGB colors.
        :type font_color: tuple (R, G, B)

        :param background_color: color of the background. In RGB colors.
        :type background_color: tuple (R, G, B)

        :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
            corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
                {
                    "United States": [
                        23,
                        60,
                        225
                    ]
                }, default is {}
        :type colors: dict

        :parem events: dictionary to add additional context to the line chart. For example to indicate events in time. Example:
            events = {
                "{EVENT NAME}": ["START DATE DD/MM/YYYY", "END DATE DD/MM/YYYY"],
                "Event 1": ["28/01/2017", "28/01/2018"],
                "Event 2": ["28/01/2019", "28/01/2020"],
                "Last event": ["28/05/2020", "28/01/2021"]
            }
        :type events: dict
    """

    if not os.path.exists(excel):
        raise FileNotFoundError("Please provide a valid Excel file")

    # creating the dataframe
    df = DataHandler.DataHandler(excel_file=excel, number_of_frames=fps*duration*60).df

    # creating the canvas
    canvas = Canvas.canvas(bg=background_color)

    # creating the bar_race
    l = LineChart.line_chart(canvas=canvas, df=df, colors=colors, font_color=font_color, back_ground_color=background_color, unit=unit, events=events)
    canvas.add_sub_plot(l)

    # adding title
    canvas.add_title(text=title, color=font_color)

    # adding sub-title
    canvas.add_sub_title(text=sub_title, color=font_color)

    # adding time indicator
    canvas.add_time(df=df, time_indicator=time_indicator, color=font_color)

    # play the animation
    canvas.play(fps=fps, record=record, file_name=output_video)

def stacked_area(excel="", title="", sub_title="", duration=1, fps=60, record=False, output_video="output.mp4", unit="", time_indicator="year", events={}, font_color=(0, 0, 0), background_color=(255, 255, 255), colors={}):
    """Function to create a bar chart race

        :param excel: excel file containing the data
        :type excel: string

        :param title: title on top of the animation
        :type title: string

        :param sub_title: sub-title to provide extra context, displayed just under the main title
        :type sub_title: string

        :param duration: length of the animation
        :type duration: integer

        :param fps: number of frames per second
        :type fps: integer

        :param record: should the animation be saved as an mp4? Defaults to False. If set to True, the render speed on screen is reduced, however, the playback speed of the video is correct.
        :type record: boolean

        :param output_video: name of the saved video.
        :type record: string

        :param unit: unit to be displayed in the graph
        :type record: string

        :param time_indicator: should the time format show year, month or day
        :type time_indicator: string, 'day', 'month', or 'year'

        :param font_color: color of the texts rendered to the screen. In RGB colors.
        :type font_color: tuple (R, G, B)

        :param background_color: color of the background. In RGB colors.
        :type background_color: tuple (R, G, B)

        :param colors: dictionary that holds color information for each of the data categories. The key of the dict should
            corespond to the name of the data category (column). The value of the dict should be the RGB values of the color:
                {
                    "United States": [
                        23,
                        60,
                        225
                    ]
                }, default is {}
        :type colors: dict

        :parem events: dictionary to add additional context to the line chart. For example to indicate events in time. Example:
            events = {
                "{EVENT NAME}": ["START DATE DD/MM/YYYY", "END DATE DD/MM/YYYY"],
                "Event 1": ["28/01/2017", "28/01/2018"],
                "Event 2": ["28/01/2019", "28/01/2020"],
                "Last event": ["28/05/2020", "28/01/2021"]
            }
        :type events: dict
    """

    if not os.path.exists(excel):
        raise FileNotFoundError("Please provide a valid Excel file")

    # creating the dataframe
    df = DataHandler.DataHandler(excel_file=excel, number_of_frames=fps*duration*60).df

    # creating the canvas
    canvas = Canvas.canvas(bg=background_color)

    # creating the bar_race
    l = AreaChart.area_chart(canvas=canvas, df=df, colors=colors, font_color=font_color, back_ground_color=background_color, unit=unit, events=events)
    canvas.add_sub_plot(l)

    # adding title
    canvas.add_title(text=title, color=font_color)

    # adding sub-title
    canvas.add_sub_title(text=sub_title, color=font_color)

    # adding time indicator
    canvas.add_time(df=df, time_indicator=time_indicator, color=font_color)

    # play the animation
    canvas.play(fps=fps, record=record, file_name=output_video)