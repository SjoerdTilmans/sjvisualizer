import datetime
import os
import os.path
from pathlib import Path

import numpy
import pandas as pd


class DataHandler:
    """Class to handle the data, and interpolate values between each data point

    :param excel_file: source Excel file to get the data
    :type excel_file: str

    :param number_of_frames: number of frames in your animation. Typically you want to aim for 60*FPS*Duration
    :type number_of_frames: int
    """

    def __init__(self, excel_file=None, number_of_frames=0, log_scale=False, **kwargs):
        # Backwards compatible signature, with optional extras via kwargs:
        # - tail_frames: frames to hold the last value (default 60*3)
        # - cache: enable/disable caching (default True)
        self.excel_file = excel_file
        self.number_of_frames = int(number_of_frames) + 7  # keep legacy +7 behaviour
        self.log_scale = log_scale

        self.tail_frames = int(kwargs.get("tail_frames", 60 * 3))
        self.cache = bool(kwargs.get("cache", True))

        if not self.excel_file:
            raise ValueError("excel_file must be provided")

        src_path = Path(str(self.excel_file))
        stem = src_path.stem
        frames_tag = str(int(self.number_of_frames))

        cache_dir = Path("_pandas_cache")
        cache_dir.mkdir(exist_ok=True)

        # New cache locations (fast + robust)
        self.cache_location_pkl = str(cache_dir / f"{stem}.{frames_tag}.pkl")
        self.cache_location_xlsx = str(cache_dir / f"{stem}.{frames_tag}.xlsx")

        # Legacy cache path attempt (old split-based logic)
        self.cache_location_legacy_xlsx = None
        try:
            legacy_name = "{}{}.xlsx".format(str(self.excel_file).split(".")[0].split("/")[1], int(self.number_of_frames))
            self.cache_location_legacy_xlsx = str(cache_dir / legacy_name)
        except Exception:
            pass

        # Keep the original attribute name for compatibility
        self.cache_location = self.cache_location_xlsx

        if self.cache and self._load_from_cache_if_fresh():
            return

        print("loading new data frame")
        self.df = pd.read_excel(self.excel_file, index_col=[0])
        self._prep_data()

        if self.cache:
            self._save_cache()

    def _source_mtime(self) -> float:
        try:
            return os.path.getmtime(self.excel_file)
        except Exception:
            return 0.0

    def _cache_is_fresh(self, path: str) -> bool:
        try:
            return os.path.isfile(path) and os.path.getmtime(path) > self._source_mtime()
        except Exception:
            return False

    def _load_from_cache_if_fresh(self) -> bool:
        # Prefer pickle (fast), then new xlsx, then legacy xlsx
        if self._cache_is_fresh(self.cache_location_pkl):
            print(f"Loading cached data frame {self.cache_location_pkl}")
            self.df = pd.read_pickle(self.cache_location_pkl)
            self.df = self.df.loc[:, ~self.df.columns.str.contains("^Unnamed")]
            self.temp_df = self.df
            return True

        if self._cache_is_fresh(self.cache_location_xlsx):
            print(f"Loading cached data frame {self.cache_location_xlsx}")
            self._load_excel(self.cache_location_xlsx)
            return True

        if self.cache_location_legacy_xlsx and self._cache_is_fresh(self.cache_location_legacy_xlsx):
            print(f"Loading cached data frame {self.cache_location_legacy_xlsx}")
            self._load_excel(self.cache_location_legacy_xlsx)
            return True

        return False

    def _load_excel(self, path: str):
        self.df = pd.read_excel(path, index_col=[0])
        self.df = self.df.loc[:, ~self.df.columns.str.contains("^Unnamed")]
        self.temp_df = self.df

    def _prep_data(self):
        # Normalize index to datetime (legacy behaviour)
        if isinstance(self.df.index[0], numpy.int64) or isinstance(self.df.index[0], float):
            self.df.index = [datetime.datetime(year=int(i), month=12, day=31) for i in self.df.index]

        self.df.index = pd.to_datetime(self.df.index)
        self.df = self.df.sort_index()
        self.df = self.df.loc[:, ~self.df.columns.str.contains("^Unnamed")]

        print("Preping data")

        if len(self.df.index) < 2:
            temp_df = self.df.copy()
            self.dt = datetime.timedelta(seconds=1)
        else:
            # Build a uniform frame index and interpolate vectorized (fast)
            frame_index = pd.date_range(self.df.index[0], self.df.index[-1], periods=int(self.number_of_frames))
            self.dt = (frame_index[1] - frame_index[0]).to_pytimedelta()

            temp = self.df.copy()

            # Keep original intent: only coerce non-string columns
            for col in temp.columns:
                first_val = temp[col].iloc[0]
                if isinstance(first_val, str):
                    continue
                try:
                    temp[col] = pd.to_numeric(temp[col], errors="ignore")
                except Exception:
                    pass

            merged_index = temp.index.union(frame_index)
            temp = temp.reindex(merged_index)

            print("Interpolating")
            try:
                temp = temp.interpolate(method="time", limit_area="inside")
            except Exception:
                temp = temp.interpolate(limit_area="inside")

            temp_df = temp.reindex(frame_index)

        # Replace nulls with 0 (legacy)
        temp_df = temp_df.fillna(0)

        # Append a tail that holds the last value (legacy intent, but fixed)
        if self.tail_frames > 0 and len(temp_df.index) >= 2:
            delta = temp_df.index[-1] - temp_df.index[-2]
            if delta <= pd.Timedelta(0):
                delta = pd.Timedelta(seconds=1)

            tail_index = pd.date_range(
                temp_df.index[-1] + delta,
                periods=self.tail_frames,
                freq=delta,
            )
            tail = pd.DataFrame(
                [temp_df.iloc[-1].to_list()] * len(tail_index),
                index=tail_index,
                columns=temp_df.columns,
            )
            temp_df = pd.concat([temp_df, tail], axis=0)

        if self.log_scale:
            # Only log numeric columns; clip to avoid -inf on zeros/negatives
            numeric_cols = temp_df.select_dtypes(include=["number"]).columns
            temp_df.loc[:, numeric_cols] = numpy.log10(temp_df.loc[:, numeric_cols].clip(lower=1e-12))
            temp_df.replace([-numpy.inf], -1000000000, inplace=True)

        self.df = temp_df.loc[:, ~temp_df.columns.str.contains("^Unnamed")].fillna(0)
        self.temp_df = self.df

    def _save_cache(self):
        print("Saving cache")

        # Fast cache
        try:
            self.df.to_pickle(self.cache_location_pkl)
        except Exception:
            pass

        # Keep Excel cache for backwards compatibility
        try:
            self.df.to_excel(self.cache_location_xlsx)
        except Exception:
            pass


class SizeCompareDataHandler:
    def __init__(self, excel_file=None, number_of_frames=0, area=True):
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
                    value_array[i] = float(v) + value_array[i - 1]
        else:
            for i, v in enumerate(value_array):
                if i > 0:
                    value_array[i] = float(v) + 0.75 * value_array[i - 1]

        for i in range(len(value_array) - 1):
            smooth_array = smooth_array + list(value_array[i] + (value_array[i + 1] - value_array[i]) * (1 - sigma))

        for i in range(60 * 30):
            smooth_array.append(smooth_array[-1] + 0.01)

        self.scales = smooth_array
