import pandas as pd
import datetime
import os.path
import numpy

class DataHandler():
    """Class to handle the data, and interpolate values between each data point

    :param excel_file: source Excel file to get the data
    :type excel_file: str

    :param number_of_frames: number of frames in your animation. Typically you want to aim for 60*FPS*Duration
    :type number_of_frames: int
    """
    def __init__(self, excel_file=None, number_of_frames=0, log_scale=False):
        self.excel_file = excel_file
        self.number_of_frames = number_of_frames
        self.log_scale = log_scale

        # try to find cached location of the file
        try:
            self.cache_location = os.path.join("_pandas_cache","{}{}.xlsx".format(self.excel_file.split(".")[0].split("/")[1], int(self.number_of_frames)))
        except:
            self.cache_location = None

        # making sure last modified date of the cached file is always more recent than the last modified date of the data file
        if self.cache_location and os.path.isfile(self.cache_location) and os.path.getmtime(self.cache_location) > os.path.getmtime(excel_file):
            print("Loading cashed data frame {}".format(self.cache_location))
            self._load_file()
        else:
            print("loading new data frame")
            self.df = pd.read_excel(excel_file, index_col=[0])
            self._prep_data()

    def _load_file(self):
        self.df = pd.read_excel(self.cache_location, index_col=[0])
        self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

    def _prep_data(self):
        if isinstance(self.df.index[0], numpy.int64) or isinstance(self.df.index[0], float):
            self.df.index = [datetime.datetime(year=int(i), month=12, day=31) for i in self.df.index]

        total_time = list(self.df.index)[-1] - list(self.df.index)[1]
        self.dt = total_time / self.number_of_frames

        temp_df = pd.DataFrame(columns=self.df.columns)

        time = list(self.df.index)[0]

        length = len(self.df)

        print("Perparing data")

        for i, (index, row) in enumerate(self.df.iterrows()):
            print("Working on {}/{}".format(i, length))
            if i > 0:
                print(time)
                print(index)
                while time < index:
                    temp_df = pd.concat([temp_df, pd.DataFrame(None, index=[time], columns=self.df.columns)])
                    time = time + self.dt

                temp_df = pd.concat([temp_df, pd.DataFrame([list(row)], index=[index], columns=self.df.columns)])
                time = index + self.dt
            elif i == 0:
                temp_df = pd.concat([temp_df, pd.DataFrame([list(row)], index=[index], columns=self.df.columns)])
                time = time + self.dt

        print("Setting column to numerical value for interpolation")
        # set columns to numeric values for interpolation
        for col in temp_df:
            if not isinstance(temp_df[col][0], str):
                try:
                    temp_df[col] = pd.to_numeric(temp_df[col])
                except ValueError:
                    pass

        print("Interpolating")
        try:
            temp_df = temp_df.interpolate(method='time')
            temp_df = temp_df.ffill()
        except:
            temp_df = temp_df.interpolate()
            temp_df = temp_df.ffill()

        dt = datetime.timedelta(seconds=i)

        print("Appending values")
        for i in range(1, 60*10):
            time = temp_df.tail(1).index[0] + dt
            temp_df = pd.concat([temp_df, pd.DataFrame([list(row)], index=[time], columns=self.df.columns)])

        if self.log_scale:
            temp_df = numpy.log10(temp_df)
            temp_df.replace([-numpy.inf], -1000000000, inplace=True)

        self.df = temp_df.loc[:, ~temp_df.columns.str.contains('^Unnamed')]
        self.temp_df = temp_df.loc[:, ~temp_df.columns.str.contains('^Unnamed')]

        print("Saving to Excel")

        if not os.path.isdir('_pandas_cache'):
            os.mkdir('_pandas_cache')

        if self.cache_location:
            temp_df.to_excel(self.cache_location)

class SizeCompareDataHandler():

    def __init__(self, excel_file=None, number_of_frames=0, area = True):
        self.excel_file = excel_file
        self.number_of_frames = number_of_frames

        self.df = pd.read_excel(excel_file)
        self.area = area

        # speed of the smooth transition
        self.w = 0.1

        self._prep_data()


    def _prep_data(self):
        n_between_points = self.number_of_frames / (len(self.df.columns) - 1)

        x = numpy.linspace(0, 2, int(n_between_points))
        sigma = 1 / (numpy.exp(-(1 - x) / self.w) + 1)
        smooth_array = []

        value_array = [self.df[self.df.columns[i]].values[0] for i, col in enumerate(self.df.columns)]

        if self.area:
            for i, v in enumerate(value_array):
                if i > 0:
                    value_array[i] = v + value_array[i-1]
        else:
            for i, v in enumerate(value_array):
                if i > 0:
                    value_array[i] = v + 0.75*value_array[i-1]

        for i in range(len(value_array) - 1):
            smooth_array = smooth_array + list(value_array[i] + (value_array[i+1] - value_array[i]) * (1 - sigma))

        for i in range(60*30):
            smooth_array.append(smooth_array[-1] + 0.01)

        self.scales = smooth_array