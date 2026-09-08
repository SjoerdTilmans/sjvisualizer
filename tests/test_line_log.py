"""Log geometry and animated bounds, without a Tk window."""

import tkinter
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from sjvisualizer.charts.line_chart import line_chart


class LineLogTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({"A": [1., 10., 100.]},
                               index=pd.date_range("2020-01-01", periods=3))
        self.surface = Mock(spec=tkinter.Canvas)
        patcher = patch("tkinter.font.Font")
        patcher.start()
        self.addCleanup(patcher.stop)

    def chart(self, **kwargs):
        return line_chart(df=self.df, canvas=self.surface, label_at_end=False,
                          draw_points=False, **kwargs)

    def test_single_and_dual_log_geometry(self):
        for numeric, x_log, y_log in ((False, False, True), (True, True, False),
                                      (True, True, True)):
            chart = self.chart(x_df=self.df if numeric else None,
                               x_log=x_log, y_log=y_log)
            chart.draw(self.df.index[0])
            for time in self.df.index[1:]:
                chart.update(time)
            for ax, logged in ((chart.axis_x, x_log), (chart.axis_y, y_log)):
                self.assertEqual(ax.is_log_scale, logged)
                if logged:
                    self.assertEqual(ax.min_val, 1)
                    np.testing.assert_allclose(ax.calc_positions_many([1, 10, 100]),
                                               [0, ax.length / 2, ax.length])

    def test_small_ranges_and_values_reach_both_edges(self):
        for lo, hi in ((2., 5.), (1e-15, 5e-15)):
            chart = self.chart(y_log=True, y_min=lo, y_max=hi)
            chart.draw(self.df.index[0])
            ax = chart.axis_y
            np.testing.assert_allclose(ax.calc_positions_many([lo, np.sqrt(lo * hi), hi]),
                                       [0, ax.length / 2, ax.length], atol=1e-9)
            self.assertAlmostEqual(ax.calc_positions(hi), ax.length)

    def test_partial_fixed_bounds_stay_positive(self):
        for bounds in ({"y_max": .1}, {"y_min": 1000}):
            chart = self.chart(y_log=True, **bounds)
            chart.draw(self.df.index[0])
            chart.update(self.df.index[1])
            self.assertGreater(chart.axis_y.min_val, 0)
            self.assertGreater(chart.axis_y.max_val, chart.axis_y.min_val)

    def test_invalid_configuration(self):
        with self.assertRaisesRegex(ValueError, "numeric x_df"):
            self.chart(x_log=True)
        for name in ("x_min", "x_max", "y_min", "y_max"):
            with self.assertRaisesRegex(ValueError, "strictly positive"):
                self.chart(x_df=self.df, x_log=True, y_log=True, **{name: 0})

    def test_invalid_frame_does_not_change_axes_or_history(self):
        for prefix in ("x", "y"):
            for bad in (0, -1, np.nan, np.inf):
                chart = self.chart(x_df=self.df.copy(), x_log=True, y_log=True)
                chart.draw(self.df.index[0])
                data = chart.df_x if prefix == "x" else chart.df
                original = data.iloc[1, 0]
                data.iloc[1, 0] = bad
                with self.assertRaisesRegex(ValueError, "strictly positive"):
                    chart.update(self.df.index[1])
                self.assertEqual(chart.lines["A"].y_values, [1])
                self.assertEqual(chart.axis_y.min_val, 1)
                data.iloc[1, 0] = original


if __name__ == "__main__":
    unittest.main()
