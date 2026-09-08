"""Chart starting values stay fixed as animated data changes."""

import tkinter
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from sjvisualizer.charts.line_chart import line_chart
from sjvisualizer.charts.bar_race import bar_race


class AxisStartTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({"A": [100., 200., 20.]},
                               index=pd.date_range("2020-01-01", periods=3))
        self.surface = Mock(spec=tkinter.Canvas)
        self.surface.bbox.return_value = (0, 0, 40, 20)
        self.surface.create_rectangle.side_effect = range(100, 200)
        self.font = patch("tkinter.font.Font").start()
        self.addCleanup(patch.stopall)

    def line(self, **kwargs):
        chart = line_chart(df=self.df, canvas=self.surface,
                           label_at_end=False, draw_points=False, **kwargs)
        chart.draw(self.df.index[0])
        return chart

    def test_line_numeric_minima_persist_and_maxima_grow(self):
        chart = self.line(x_df=self.df, x_min=40, y_min=50)
        self.assertEqual((chart.axis_x.min_val, chart.axis_y.min_val), (40, 50))
        chart.update(self.df.index[1])
        self.assertEqual((chart.axis_x.max_val, chart.axis_y.max_val), (200, 200))
        chart.update(self.df.index[2])
        self.assertEqual((chart.axis_x.min_val, chart.axis_y.min_val), (40, 50))
        self.assertEqual((chart.axis_x.max_val, chart.axis_y.max_val), (200, 200))

    def test_date_start_accepts_string_and_keeps_growing(self):
        chart = self.line(x_min="2019-01-01", y_min=-50)
        chart.update(self.df.index[1])
        self.assertEqual(chart.axis_x.min_val, pd.Timestamp("2019-01-01"))
        self.assertEqual(chart.axis_x.max_val, self.df.index[1])
        self.assertEqual(chart.axis_y.min_val, -50)

    def test_all_four_bounds_stay_fixed(self):
        chart = self.line(x_df=self.df, x_min=50, x_max=150,
                          y_min=60, y_max=160)
        chart.update(self.df.index[1])
        chart.update(self.df.index[2])
        self.assertEqual((chart.axis_x.min_val, chart.axis_x.max_val), (50, 150))
        self.assertEqual((chart.axis_y.min_val, chart.axis_y.max_val), (60, 160))

    def test_maxima_only_leave_minima_automatic(self):
        chart = self.line(x_df=self.df, x_max=150, y_max=160, y_zero_based=False)
        self.assertEqual((chart.axis_x.min_val, chart.axis_y.min_val), (100, 100))
        chart.update(self.df.index[1])
        chart.update(self.df.index[2])
        self.assertEqual((chart.axis_x.min_val, chart.axis_y.min_val), (20, 20))
        self.assertEqual((chart.axis_x.max_val, chart.axis_y.max_val), (150, 160))

    def test_date_bounds_and_maximum_only(self):
        for lower in (None, "2019-01-01"):
            chart = self.line(x_min=lower, x_max="2020-01-02")
            chart.update(self.df.index[2])
            self.assertEqual(chart.axis_x.min_val, pd.Timestamp(lower or "2020-01-01"))
            self.assertEqual(chart.axis_x.max_val, pd.Timestamp("2020-01-02"))

    def test_invalid_bound_pairs_fail(self):
        for prefix in ("x", "y"):
            for upper in (50, 40):
                with self.assertRaisesRegex(ValueError, "must be less than"):
                    self.line(x_df=self.df, **{f"{prefix}_min": 50, f"{prefix}_max": upper})
        with self.assertRaisesRegex(ValueError, "must be less than"):
            self.line(x_min="2021-01-01", x_max="2020-01-01")

    def test_removed_limits_fail_with_migration_hint(self):
        for name in ("x_lims", "y_lims"):
            with self.assertRaisesRegex(TypeError, "was removed; use"):
                self.line(**{name: (0, 100)})

    def test_maximum_below_all_data_does_not_invert_axis(self):
        chart = self.line(x_df=self.df, x_max=-50, y_max=-50)
        self.assertEqual((chart.axis_x.max_val, chart.axis_y.max_val), (-50, -50))
        self.assertLess(chart.axis_x.min_val, chart.axis_x.max_val)
        self.assertLess(chart.axis_y.min_val, chart.axis_y.max_val)

    def test_default_line_axes_are_unchanged(self):
        chart = self.line()
        chart.update(self.df.index[1])
        self.assertEqual(chart.axis_x.min_val, self.df.index[0])
        self.assertEqual(chart.axis_y.min_val, 0)

    def test_bar_minimum_and_clipped_geometry_in_both_orientations(self):
        for orientation in ("horizontal", "vertical"):
            for allow_decrease in (True, False):
                with self.subTest(orientation=orientation, allow_decrease=allow_decrease):
                    chart = bar_race(df=self.df, canvas=self.surface, axis_min=50,
                                     orientation=orientation, allow_decrease=allow_decrease)
                    chart.draw(self.df.index[0])
                    chart.update(self.df.index[1])
                    self.assertEqual(chart.axis1.max_val, 200)
                    self.surface.coords.reset_mock()
                    chart.update(self.df.index[2])
                    self.assertEqual(chart.axis1.min_val, 50)
                    self.assertGreater(chart.axis1.max_val, 50)
                    rect = chart.graph_elements["A"].rect
                    coords = [c.args[1:] for c in self.surface.coords.call_args_list
                              if c.args[0] == rect][-1]
                    # A value below the visible range has zero visible length.
                    if orientation == "horizontal":
                        self.assertEqual(coords[0], chart.axis1.x)
                        self.assertEqual(coords[2], chart.axis1.x)
                    else:
                        self.assertEqual(coords[1], chart.axis1.y)
                        self.assertEqual(coords[3], chart.axis1.y)

    def test_nonfinite_starts_fail(self):
        for value in (float("nan"), float("inf")):
            for name in ("x_min", "x_max", "y_min", "y_max"):
                with self.assertRaises(ValueError):
                    self.line(x_df=self.df, **{name: value})
            with self.assertRaises(ValueError):
                bar_race(df=self.df, canvas=self.surface, axis_min=value)

    def test_start_above_all_data_does_not_invert_axis(self):
        chart = self.line(x_df=self.df, x_min=500, y_min=500)
        self.assertGreater(chart.axis_x.max_val, chart.axis_x.min_val)
        self.assertGreater(chart.axis_y.max_val, chart.axis_y.min_val)


if __name__ == "__main__":
    unittest.main()
