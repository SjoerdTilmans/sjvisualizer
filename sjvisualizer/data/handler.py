"""Data handling and interpolation."""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import pickle
import tempfile
from pathlib import Path

import numpy
import pandas as pd


class DataHandler:
    """Load and interpolate time-series data for animations.

    The original SJVisualizer workflow is:

    1. Load an Excel sheet (index column = time)
    2. Interpolate to a fixed number of animation frames
    3. Optionally cache the interpolated dataframe for faster reruns

    Attributes
    ----------
    df:
        The interpolated dataframe used for playback.
    dt:
        Time delta between generated frames.
    """

    def __init__(self, excel_file=None, number_of_frames=0, log_scale=False, **kwargs):
        # Backwards compatible signature, with optional extras via kwargs:
        # - tail_frames: frames to hold the last value (default 60*3)
        # - cache: enable/disable caching (default True)
        # - cache_excel: also export a human-readable Excel cache (default False)
        self.excel_file = excel_file
        self.number_of_frames = int(number_of_frames) + 7  # keep legacy +7 behaviour
        self.log_scale = log_scale

        self.tail_frames = int(kwargs.get("tail_frames", 60 * 3))
        self.cache = bool(kwargs.get("cache", True))
        self.cache_excel = bool(kwargs.get("cache_excel", False))
        if self.number_of_frames < 2 or self.tail_frames < 0:
            raise ValueError("Frame count must produce at least two frames and tail_frames must be non-negative")

        if not self.excel_file:
            raise ValueError("excel_file must be provided")

        src_path = Path(str(self.excel_file))
        # Include the full source identity and every interpolation option.
        # Old caches have no settings metadata and cannot be safely reused.
        stat = src_path.stat()
        identity = (str(src_path.resolve()), stat.st_mtime_ns, stat.st_size,
                    self.number_of_frames, self.tail_frames, bool(self.log_scale), 2)
        digest = hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:24]
        stem = f"{src_path.stem}.{digest}"
        frames_tag = str(int(self.number_of_frames))

        cache_dir = Path("_pandas_cache")
        if self.cache:
            cache_dir.mkdir(exist_ok=True)

        # New cache locations (fast + robust)
        self.cache_location_pkl = str(cache_dir / f"{stem}.{frames_tag}.pkl")
        self.cache_location_xlsx = str(cache_dir / f"{stem}.{frames_tag}.xlsx")

        # Retained attribute; settings-free legacy caches are intentionally ignored.
        self.cache_location_legacy_xlsx = None

        # Point the convenience attribute at the cache actually written.
        self.cache_location = self.cache_location_xlsx if self.cache_excel else self.cache_location_pkl

        if self.cache and self._load_from_cache_if_fresh():
            if self.cache_excel and not os.path.exists(self.cache_location_xlsx):
                self.df.to_excel(self.cache_location_xlsx)
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
        if self._cache_is_fresh(self.cache_location_pkl):
            try:
                cached = pd.read_pickle(self.cache_location_pkl)
                if not isinstance(cached, pd.DataFrame) or "sjvisualizer_dt" not in cached.attrs:
                    return False
            except (OSError, ValueError, EOFError, ImportError, pickle.UnpicklingError):
                return False
            self.df = cached
            self.dt = cached.attrs["sjvisualizer_dt"]
            self.temp_df = self.df
            return True

        return False

    def _load_excel(self, path: str):
        self.df = pd.read_excel(path, index_col=[0])
        self.df = self.df.loc[:, ~self.df.columns.astype(str).str.contains("^Unnamed")]
        self.temp_df = self.df

    def _prep_data(self):
        if self.df.empty:
            raise ValueError("Source dataframe must contain rows and columns")
        if isinstance(self.df.index[0], (int, numpy.integer, float)):
            self.df.index = [datetime.datetime(year=int(i), month=12, day=31) for i in self.df.index]

        self.df.index = pd.to_datetime(self.df.index)
        if self.df.index.hasnans or not self.df.index.is_unique:
            raise ValueError("Source timestamps must be non-missing and unique")
        self.df = self.df.sort_index()
        self.df = self.df.loc[:, ~self.df.columns.astype(str).str.contains("^Unnamed")]

        print("Preping data")

        if len(self.df.index) < 2:
            temp_df = self.df.copy()
            self.dt = datetime.timedelta(seconds=1)
        else:
            frame_index = pd.date_range(self.df.index[0], self.df.index[-1], periods=int(self.number_of_frames))
            self.dt = (frame_index[1] - frame_index[0]).to_pytimedelta()

            temp = self.df.copy()

            merged_index = temp.index.union(frame_index)
            temp = temp.reindex(merged_index)

            print("Interpolating")
            numeric_cols = temp.select_dtypes(include=["number"]).columns
            temp[numeric_cols] = temp[numeric_cols].interpolate(method="time", limit_area="inside")

            temp_df = temp.reindex(frame_index)

        temp_df = temp_df.fillna(0)

        if self.tail_frames > 0 and len(temp_df.index) >= 2:
            delta = temp_df.index[-1] - temp_df.index[-2]
            if delta <= pd.Timedelta(0):
                delta = pd.Timedelta(seconds=1)

            tail_index = pd.date_range(temp_df.index[-1] + delta, periods=self.tail_frames, freq=delta)
            tail = pd.DataFrame([temp_df.iloc[-1].to_list()] * len(tail_index), index=tail_index, columns=temp_df.columns)
            temp_df = pd.concat([temp_df, tail], axis=0)

        if self.log_scale:
            numeric_cols = temp_df.select_dtypes(include=["number"]).columns
            temp_df[numeric_cols] = numpy.log10(temp_df[numeric_cols].clip(lower=1e-12))
            temp_df.replace([-numpy.inf], -1000000000, inplace=True)

        self.df = temp_df.fillna(0)
        self.df.attrs["sjvisualizer_dt"] = self.dt
        self.temp_df = self.df

    def _save_cache(self):
        print("Saving cache")

        # Replace atomically so another reader never sees a partial pickle.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=Path(self.cache_location_pkl).parent,
                                             suffix=".tmp", delete=False) as file:
                temporary = file.name
            self.df.to_pickle(temporary)
            os.replace(temporary, self.cache_location_pkl)
        except OSError:
            pass
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)

        if self.cache_excel:
            self.df.to_excel(self.cache_location_xlsx)


class SizeCompareDataHandler:
    """Helper to generate a smooth scale factor sequence from a single-row sheet.

    This is a niche legacy helper used by size/area comparison-style charts.
    It reads a single row of values and builds a smooth transition curve
    between consecutive points.
    """

    def __init__(self, excel_file=None, number_of_frames=0, area=True):
        self.excel_file = excel_file
        self.number_of_frames = number_of_frames

        self.df = pd.read_excel(excel_file)
        self.area = area

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
