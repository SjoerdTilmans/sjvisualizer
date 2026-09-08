"""Framework regression tests using fake Tk widgets and video writers."""

import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from PIL import Image

from sjvisualizer.core.canvas import canvas
from sjvisualizer.core.axis import axis
from sjvisualizer.core.subplot import sub_plot
from sjvisualizer.charts.line_chart import line_chart, _Line
from sjvisualizer.charts.bar_race import bar, bar_race
from sjvisualizer.data.handler import DataHandler


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.cv = canvas.__new__(canvas)
        self.cv.width, self.cv.height = 32, 24
        self.cv.include_logo = False
        self.cv.canvas = Mock()
        self.cv.canvas.winfo_rootx.return_value = 100
        self.cv.canvas.winfo_rooty.return_value = 200
        self.cv.tk = Mock()
        self.sub = Mock(df=pd.DataFrame({"A": [1, 2, 3]}))
        self.cv.sub_canvas = [self.sub]

    def test_playback_updates_each_frame_without_repacking_or_logging(self):
        with patch("sjvisualizer.core.canvas.time.sleep"), contextlib.redirect_stdout(io.StringIO()) as output:
            self.cv.play()
        self.assertEqual(self.sub.update.call_count, 3)
        self.assertEqual(self.cv.tk.update.call_count, 3)
        self.cv.canvas.pack.assert_not_called()
        self.assertEqual(output.getvalue(), "")

    def test_invalid_fps_and_empty_frames_fail_before_updating(self):
        for fps in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                self.cv.play(fps=fps)
        with self.assertRaises(ValueError):
            self.cv.play(df=pd.DataFrame())
        self.sub.update.assert_not_called()

    def test_duplicate_registration_is_ignored(self):
        self.cv.add_sub_plot(self.sub)
        self.assertEqual(len(self.cv.sub_canvas), 1)
        self.sub.set_root.assert_not_called()

    def test_recording_includes_first_frames_and_uses_canvas_position(self):
        writer = Mock()
        with patch("cv2.VideoWriter", return_value=writer) as factory, \
                patch("PIL.ImageGrab.grab", side_effect=lambda **kw: Image.new("RGB", (32, 24), "red")) as grab, \
                patch("sjvisualizer.core.canvas.time.sleep"):
            self.cv.play(record=True)
        self.assertEqual(factory.call_args.args[-1], (32, 24))
        self.assertEqual(writer.write.call_count, 3)
        np.testing.assert_array_equal(writer.write.call_args.args[0][0, 0], [0, 0, 255])
        grab.assert_called_with(bbox=(100, 200, 132, 224))
        writer.release.assert_called_once()

    def test_writer_is_released_when_rendering_fails(self):
        writer = Mock()
        self.sub.update.side_effect = RuntimeError("render failed")
        with patch("cv2.VideoWriter", return_value=writer):
            with self.assertRaisesRegex(RuntimeError, "render failed"):
                self.cv.play(record=True)
        writer.release.assert_called_once()

    def test_unavailable_encoder_fails_clearly(self):
        writer = Mock()
        writer.isOpened.return_value = False
        with patch("cv2.VideoWriter", return_value=writer):
            with self.assertRaisesRegex(RuntimeError, "video writer"):
                self.cv.play(record=True)
        writer.release.assert_called_once()
        self.sub.update.assert_not_called()


class AxisTests(unittest.TestCase):
    def setUp(self):
        self.surface = Mock()
        self.surface.create_line.side_effect = range(1000)
        self.surface.create_text.side_effect = range(1000, 2000)
        with patch("sjvisualizer.core.axis.font.Font") as make_font:
            self.axis = axis(self.surface, n=1, tick_length=15)
            make_font.assert_called_once()

    def test_tick_capacity_can_grow_after_draw(self):
        self.axis.draw(0, 10)
        initial = len(self.axis.ticks)
        self.axis.n = 10
        self.axis.update(0, 10)
        self.assertGreater(len(self.axis.ticks), initial)
        self.assertTrue(all(hasattr(t, "line") and t.length == 15 for t in self.axis.ticks))

    def test_unchanged_ticks_skip_geometry_and_text_updates(self):
        self.axis.draw(0, 10)
        self.surface.reset_mock()
        for _ in range(100):
            self.axis.update(0, 10)
        self.surface.coords.assert_not_called()
        self.surface.itemconfig.assert_not_called()
        self.axis.update(0, 20)
        self.assertGreater(self.surface.coords.call_count, 0)

    def test_position_calculation_does_not_mutate_limits(self):
        self.axis.draw(0, 0)
        self.assertEqual(self.axis.calc_positions(0), 0)
        self.assertEqual(self.axis.max_val, 0)

    def test_bulk_positions_match_scalar_mapping(self):
        for lo, hi, log in ((0, 0, False), (-100, 300, False), (1, 1000, True)):
            self.axis.min_val, self.axis.max_val = lo, hi
            self.axis.is_log_scale = log
            values = [-10, 0, 1, 25, 100, 1000]
            np.testing.assert_allclose(self.axis.calc_positions_many(values),
                                       [self.axis.calc_positions(v) for v in values])
        self.axis.is_date = True
        self.axis.min_val, self.axis.max_val = pd.Timestamp("2000"), pd.Timestamp("2020")
        np.testing.assert_allclose(self.axis.calc_positions_many(values),
                                   [self.axis.calc_positions(v) for v in values])

    def test_date_ticks_use_sticky_limits(self):
        self.axis.is_date = True
        start, end = pd.Timestamp("2000-01-01"), pd.Timestamp("2020-01-01")
        self.axis.draw(start, end)
        self.surface.reset_mock()
        self.axis.update(pd.Timestamp("2010-01-01"), pd.Timestamp("2015-01-01"))
        self.surface.coords.assert_not_called()


class SubplotTests(unittest.TestCase):
    def test_empty_charts_and_invalid_bar_counts_fail_clearly(self):
        for chart_type in (line_chart, bar_race):
            with self.assertRaises(ValueError):
                chart_type(df=pd.DataFrame())
        for count in (0, -1):
            with self.assertRaisesRegex(ValueError, "number_of_bars"):
                bar_race(df=pd.DataFrame({"A": [1]}), number_of_bars=count)

    def test_line_geometry_and_markers_match_axis_positions(self):
        surface = Mock()
        with patch("sjvisualizer.core.axis.font.Font"):
            xaxis, yaxis = axis(surface), axis(surface)
        xaxis.min_val, xaxis.max_val = 0, 10
        yaxis.min_val, yaxis.max_val = -10, 10
        chart = Mock(height=200, x_pos=10, y_pos=20, avoid_label_overlap=False)
        line = _Line("A", surface, chart, "red", xaxis, yaxis, True, 2, False, None)
        time = pd.Timestamp("2000-01-01 12:00")
        line.seed(1, 2, time, False)
        line.update(3, 4, time, False)
        expected = [10 + xaxis.calc_positions(1), 220 - yaxis.calc_positions(2),
                    10 + xaxis.calc_positions(3), 220 - yaxis.calc_positions(4)]
        np.testing.assert_allclose(surface.create_line.call_args.args, expected)
        self.assertEqual(surface.create_oval.call_count, 2)

    def test_line_chart_with_root_draws_after_initialization_once(self):
        import tkinter
        root = Mock()
        wrapper = Mock(canvas=Mock(spec=tkinter.Canvas), colors={})
        df = pd.DataFrame({"A": [1]}, index=pd.date_range("2000", periods=1))
        drawn = []

        def draw(chart, time):
            drawn.append((chart.df, chart.lines, time))

        with patch.object(line_chart, "draw", draw):
            chart = line_chart(df=df, canvas=wrapper, root=root)
            chart.set_root(root)
        self.assertEqual(len(drawn), 1)
        self.assertIs(drawn[0][0], df)
        self.assertIs(chart.colors, wrapper.colors)

    def test_deleting_an_absent_bar_does_no_tk_work(self):
        item = bar.__new__(bar)
        item.canvas = Mock()
        item.exists = False
        item.rect = 1
        item.delete()
        item.canvas.delete.assert_not_called()


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        previous = os.getcwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, previous)
        Path("source.xlsx").touch()
        self.source = pd.DataFrame({"A": [1., 100.]}, index=[2000, 2001])

    def load(self, **kwargs):
        options = dict(excel_file="source.xlsx", number_of_frames=3, tail_frames=2)
        options.update(kwargs)
        with patch("pandas.read_excel", return_value=self.source.copy()), contextlib.redirect_stdout(io.StringIO()):
            return DataHandler(**options)

    def test_cache_round_trip_restores_frame_delta(self):
        first = self.load()
        with patch("pandas.read_excel", side_effect=AssertionError("cache miss")):
            second = DataHandler("source.xlsx", number_of_frames=3, tail_frames=2)
        pd.testing.assert_frame_equal(first.df, second.df)
        self.assertEqual(first.dt, second.dt)
        self.assertFalse(Path(first.cache_location_xlsx).exists())
        self.assertFalse(list(Path("_pandas_cache").glob("*.tmp")))

    def test_options_and_source_identity_do_not_collide(self):
        first = self.load()
        log = self.load(log_scale=True)
        tail = self.load(tail_frames=5)
        Path("other").mkdir()
        Path("other/source.xlsx").touch()
        other = self.load(excel_file="other/source.xlsx")
        self.assertEqual(len({x.cache_location_pkl for x in (first, log, tail, other)}), 4)
        self.assertAlmostEqual(log.df.iloc[-1, 0], 2.)
        self.assertEqual(len(tail.df) - len(first.df), 3)

    def test_source_change_invalidates_cache(self):
        first = self.load()
        Path("source.xlsx").write_text("changed")
        second = self.load()
        self.assertNotEqual(first.cache_location_pkl, second.cache_location_pkl)

    def test_corrupt_cache_is_rebuilt(self):
        first = self.load()
        Path(first.cache_location_pkl).write_bytes(b"broken pickle")
        second = self.load()
        pd.testing.assert_frame_equal(first.df, second.df)

    def test_disabled_cache_does_not_create_directory(self):
        self.load(cache=False)
        self.assertFalse(Path("_pandas_cache").exists())

    def test_excel_export_can_be_requested_after_cache_hit(self):
        self.load()
        with patch.object(pd.DataFrame, "to_excel") as export:
            loaded = self.load(cache_excel=True)
        export.assert_called_once_with(loaded.cache_location_xlsx)

    def test_empty_and_duplicate_data_fail_clearly(self):
        for source in (pd.DataFrame(), pd.DataFrame({"A": [1, 2]}, index=[2000, 2000])):
            self.source = source
            with self.assertRaises(ValueError):
                self.load(cache=False)

    def test_numeric_column_names_and_single_row(self):
        self.source = pd.DataFrame({1: [5.]}, index=[2000])
        first = self.load()
        second = self.load()
        pd.testing.assert_frame_equal(first.df, second.df)
        self.assertEqual(first.dt, second.dt)


if __name__ == "__main__":
    unittest.main()
