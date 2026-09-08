"""Regression coverage for migrated charts without a display server."""
import importlib
import tkinter
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from example_loader import build_chart, demo_data
from sjvisualizer import Histogram, DynamicLine, DynamicMatrix, StackedBarChart, Map, Total
from sjvisualizer.charts.map import _geometry


class MigrationTests(unittest.TestCase):
    def setUp(self):
        patch("tkinter.font.Font").start()
        self.addCleanup(patch.stopall)
        self.cv = Mock(spec=tkinter.Canvas)
        self.cv.bbox.return_value = (0, 0, 50, 20)
        ids = iter(range(100000))
        for method in ("create_line", "create_rectangle", "create_oval", "create_polygon", "create_text"):
            getattr(self.cv, method).side_effect = lambda *a, **kw: next(ids)
        self.df = demo_data(5)

    def test_all_demos_draw_seek_and_reuse_items(self):
        for name in ("Histogram", "Dynamic Line", "Dynamic Matrix", "Stacked Bar Chart",
                     "World Map", "Date", "Total", "Legend", "Empty"):
            with self.subTest(name=name):
                chart = build_chart(name, self.cv, self.df)
                chart.draw(self.df.index[0])
                self.cv.reset_mock()
                for k in (4, 1, 0, 0):
                    chart.update(self.df.index[k])
                for method in ("create_line", "create_rectangle", "create_oval", "create_polygon", "create_text"):
                    getattr(self.cv, method).assert_not_called()
                for call in self.cv.coords.call_args_list:
                    self.assertTrue(np.isfinite(np.asarray(call.args[1:], dtype=float)).all())

    def test_short_zero_stacked_data_and_seek_visibility(self):
        df = self.df.iloc[:2]*0
        c = StackedBarChart.stacked_bar_chart(self.cv, df, number_of_bars=20)
        c.draw(df.index[0])
        self.assertEqual(list(c.samples), [0, 1])
        c.update(df.index[1])
        c.update(df.index[0])
        for bar in c.bars[1]:
            self.cv.itemconfig.assert_any_call(bar, state="hidden")

    def test_negative_histogram_and_seek_scale(self):
        df = pd.DataFrame({"A": [-2, -10, 0], "B": [2, 100, 0]})
        c = Histogram.histogram(self.cv, df)
        c.draw(0)
        c.update(1)
        self.assertEqual(c.axis.max_val, 100)
        c.update(0)
        self.assertEqual((c.axis.min_val, c.axis.max_val), (-2, 2))
        self.cv.reset_mock()
        c.update(0)
        self.cv.coords.assert_not_called()

    def test_stacked_spring_and_expanding_layout(self):
        df = pd.DataFrame({"A": np.full(101, 6.), "B": np.full(101, 4.)})
        c = StackedBarChart.stacked_bar_chart(self.cv, df, number_of_bars=3,
            animation_frames=20, bar_gap=0, x_pos=0, y_pos=0, width=300, height=100)
        c.draw(0)

        def rectangle(i, j=0):
            return next(call.args[1:] for call in reversed(self.cv.coords.call_args_list)
                        if call.args[0] == c.bars[i][j])

        self.assertEqual(rectangle(0)[::2], (0, 300))
        c.update(50)
        self.assertEqual(rectangle(0)[::2], (0, 300))
        self.assertEqual(rectangle(1)[1], 100)  # New stack starts at baseline.
        c.update(55)
        self.assertLess(rectangle(0)[2], 300)
        self.assertGreater(rectangle(0)[2], 150)
        self.assertAlmostEqual(rectangle(0)[2], rectangle(1)[0])
        self.assertLess(rectangle(1)[1], 0)  # Spring overshoots its target.
        self.assertAlmostEqual(rectangle(1)[3], rectangle(1, 1)[1])
        c.update(70)
        self.assertEqual(rectangle(0)[::2], (0, 150))
        self.assertEqual(rectangle(1), (150, 0, 300, 60))
        c.update(100)
        for _ in range(20):
            c.update(100)
        self.assertEqual(rectangle(2), (200, 0, 300, 60))
        c.update(55)
        sought = rectangle(1)
        c.update(0)
        c.update(55)
        self.assertEqual(rectangle(1), sought)

    def test_stacked_animation_options(self):
        for options in ({"animation_frames": -1}, {"animation_frames": 1.5}, {"bar_gap": 1}):
            with self.assertRaises(ValueError):
                StackedBarChart.stacked_bar_chart(self.cv, self.df, **options)
        c = StackedBarChart.stacked_bar_chart(self.cv, self.df, animation_frames=0)
        c.draw(self.df.index[0])
        self.cv.reset_mock()
        c.update(self.df.index[0])
        self.cv.coords.assert_not_called()

    def test_dynamic_line_keeps_category_positions_when_seeking(self):
        c = DynamicLine.dynamic_curve(self.cv, self.df)
        c.draw(self.df.index[0])
        for time in self.df.index[::-1]:
            c.update(time)
            self.assertEqual((c.x_axis.min_val, c.x_axis.max_val), (0, len(self.df.columns)))

    def test_map_geometry_not_mutated_and_fill_clamped(self):
        import copy
        before = copy.deepcopy(_geometry())
        for width in (200, 900):
            c = Map.map(self.cv, self.df, width=width, min_value=10)
            c.draw(self.df.index[0])
            self.assertEqual(c._color(10, 20), "#dcebfa")
            self.assertEqual(c._color(100, 20), "#235ab4")
        self.assertEqual(before, _geometry())

    def test_map_discrete_bins_missing_data_and_zero(self):
        df = pd.DataFrame({"China": [0., np.nan], "Brazil": [100., 50.]})
        c = Map.map(self.cv, df, allow_decrease=True)
        c.draw(0)
        self.assertEqual(len(c._legend_swatches), 5)
        self.assertEqual(c._fills["China"], c._bin_colors[0])
        self.assertEqual(c._fills["Brazil"], c._bin_colors[-1])
        self.assertEqual(c._fills["Canada"], "#bebebe")
        self.assertTrue(any(call.kwargs.get("text") == "No data"
                            for call in self.cv.create_text.call_args_list))
        for i in range(5):
            self.assertEqual(c._color(i*20, 100), c._bin_colors[i])
            self.assertEqual(c._color(i*20+19.9, 100), c._bin_colors[i])
        self.assertEqual(c._color(-1, 100), c._bin_colors[0])
        self.assertEqual(c._color(np.nan, 100), c.missing_color)
        c.update(1)
        self.assertEqual(c._fills["China"], c.missing_color)
        np.testing.assert_array_equal(c.bin_edges, [0, 10, 20, 30, 40, 50])
        c.update(0)
        self.assertEqual(c._fills["China"], c._bin_colors[0])

    def test_map_bin_configuration_and_degenerate_range(self):
        for bins in (0, -1, 1.5, np.inf):
            with self.assertRaises(ValueError):
                Map.map(self.cv, self.df, legend_bins=bins)
        c = Map.map(self.cv, pd.DataFrame({"China": [0.]}), legend_bins=1)
        c.draw(0)
        self.assertEqual(len(c._legend_swatches), 1)
        self.assertEqual(c._color(0, 0), c._bin_colors[0])
        self.assertNotEqual(c._fills["China"], c.missing_color)

    def test_map_round_automatic_boundaries(self):
        c = Map.map(self.cv, self.df)
        np.testing.assert_array_equal(c._legend_edges(83), [0, 20, 40, 60, 80, 100])
        np.testing.assert_allclose(c._legend_edges(.083), [0, .02, .04, .06, .08, .1])
        self.assertTrue(np.all(np.diff(c._legend_edges(0)) > 0))
        c = Map.map(self.cv, self.df, min_value=13)
        edges = c._legend_edges(83)
        self.assertLessEqual(edges[0], 13)
        self.assertGreaterEqual(edges[-1], 83)
        self.assertEqual(len(edges), 6)

    def test_map_fixed_unequal_legend_boundaries(self):
        boundaries = [0, 10, 25, 100]
        c = Map.map(self.cv, self.df, legend_values=boundaries)
        boundaries[-1] = 999
        c.draw(self.df.index[0])
        self.assertEqual(len(c._legend_swatches), 3)
        for value, expected in ((-1, 0), (9.9, 0), (10, 1), (24.9, 1), (25, 2), (500, 2)):
            self.assertEqual(c._color(value), c._bin_colors[expected])
        c.update(self.df.index[-1])
        np.testing.assert_array_equal(c.bin_edges, [0, 10, 25, 100])
        for label, text in zip(c._legend_labels, ("0", "10", "25", "100")):
            self.cv.itemconfig.assert_any_call(label, text=text)
        for values in ([], [0], [0, 0], [10, 0], [0, np.nan], [[0, 10]]):
            with self.assertRaises(ValueError):
                Map.map(self.cv, self.df, legend_values=values)

    def test_matrix_clips_and_total_formats_initial_frame(self):
        c = DynamicMatrix.dynamic_matrix(self.cv, pd.DataFrame({"A": [-100, 100]}),
                                         x_pos=0, y_pos=0, width=100, height=100)
        c.draw(0)
        c.update(1)
        coords = [v for v in self.cv.coords.call_args_list if v.args[0] == c.bars[0]][-1].args
        self.assertAlmostEqual(coords[3], 100)
        total = Total.total(self.cv, pd.DataFrame({"A": [12], "B": [3]}), unit="$", prefix="Sum: ")
        total.draw(0)
        self.cv.itemconfig.assert_any_call(total.text_id, text="Sum: $15")

    def test_validation_and_nonfinite_values(self):
        for cls in (Histogram.histogram, DynamicLine.dynamic_curve, DynamicMatrix.dynamic_matrix,
                    StackedBarChart.stacked_bar_chart, Map.map):
            with self.subTest(cls=cls):
                with self.assertRaises(ValueError):
                    cls(self.cv, pd.DataFrame())
                with self.assertRaises(ValueError):
                    cls(self.cv, pd.DataFrame({"a": [1, 2]}, index=[0, 0]))
                c = cls(self.cv, pd.DataFrame({"a": [np.nan, np.inf]}))
                c.draw(0)
                c.update(1)
        with self.assertRaises(ValueError):
            StackedBarChart.stacked_bar_chart(self.cv, -self.df)

    def test_compatibility_imports(self):
        for module, name in (("Histogram", "histogram"), ("DynamicLine", "dynamic_curve"),
                             ("DynamicMatrix", "dynamic_matrix"),
                             ("StackedBarChart", "stacked_bar_chart"), ("Map", "map"),
                             ("Date", "date"), ("Total", "total"), ("Legend", "legend"), ("Empty", "empty")):
            self.assertTrue(callable(getattr(importlib.import_module("sjvisualizer."+module), name)))


if __name__ == "__main__":
    unittest.main()
