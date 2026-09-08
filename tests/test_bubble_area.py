"""Rendering regressions without opening a Tk window."""
import tkinter
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from sjvisualizer import bubble_chart, area_chart


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.font = patch("tkinter.font.Font").start()
        self.addCleanup(patch.stopall)
        self.cv = Mock(spec=tkinter.Canvas)
        self.cv.bbox.return_value = (40, 20, 60, 30)
        ids = iter(range(10000))
        for name in ("create_polygon", "create_line", "create_text", "create_oval", "create_rectangle"):
            getattr(self.cv, name).side_effect = lambda *a, **kw: next(ids)
        self.idx = pd.date_range("2020-01-01", periods=3, freq="h")

    def bubble(self, **kwargs):
        df = pd.DataFrame({"A": [-1., 0., 2.], "B": [3., 4., 5.]}, index=self.idx)
        chart = bubble_chart(canvas=self.cv, df_x=df, df_y=df, **kwargs)
        chart.draw(self.idx[0])
        return chart

    def test_linear_negative_and_disabled_labels(self):
        chart = self.bubble(display_label=False)
        chart.update(self.idx[1])
        self.assertEqual(chart.x_axis.min_val, -1)
        self.assertTrue(all(label is None for _, label in chart.bubbles.values()))
        self.assertTrue(all(c.args[0] is not None for c in self.cv.tag_raise.call_args_list))

    def test_log_invalid_points_and_recovery(self):
        chart = self.bubble(x_log=True, y_log=True)
        marker = chart.bubbles["A"][0]
        self.cv.itemconfig.assert_any_call(marker, state="hidden")
        chart.update(self.idx[2])
        self.cv.itemconfig.assert_any_call(marker, state="normal")
        self.assertGreater(chart.x_axis.min_val, 0)

    def test_size_area_ratio_alignment_and_zero(self):
        sizes = pd.DataFrame({"B": [4., 0., 4.], "A": [1., 1., 1.]}, index=self.idx)
        chart = self.bubble(df_size=sizes, max_bubble_size=100)
        calls = {c.args[0]: c.args[1:] for c in self.cv.coords.call_args_list}
        diameters = [calls[m][2]-calls[m][0] for m, _ in chart.bubbles.values()]
        self.assertAlmostEqual(diameters[1]/diameters[0], 2)
        chart.update(self.idx[1])
        self.cv.itemconfig.assert_any_call(chart.bubbles["B"][0], state="hidden")
        self.cv.reset_mock()
        chart.update(self.idx[1])
        self.cv.coords.assert_not_called()

    def test_area_stack_intraday_seek_and_item_reuse(self):
        df = pd.DataFrame({"A": [2., 3., 4.], "B": [1., 1., 2.]}, index=self.idx)
        chart = area_chart(canvas=self.cv, df=df, x_pos=0, y_pos=0, width=100, height=60)
        chart.draw(self.idx[0])
        self.cv.reset_mock()
        chart.update(self.idx[2])
        calls = {c.args[0]: c.args[1:] for c in self.cv.coords.call_args_list}
        np.testing.assert_allclose(calls[chart.areas["A"]], [0,30,50,20,100,0,100,40,50,50,0,50])
        self.cv.create_polygon.assert_not_called()
        chart.update(self.idx[0])
        self.assertEqual(chart.axis2.max_val, 3)
        self.cv.reset_mock()
        chart.update(self.idx[0])
        self.cv.coords.assert_not_called()

    def test_area_right_labels_follow_latest_band_midpoint(self):
        df = pd.DataFrame({"A": [2., 6., 0.], "B": [2., 2., 8.]}, index=self.idx)
        chart = area_chart(canvas=self.cv, df=df, x_pos=20, y_pos=30,
                           width=100, height=80, label_position="right", display_values=True)
        chart.draw(self.idx[0])
        label = chart._labels["A"]
        self.cv.itemconfig.assert_any_call(label, anchor="w")
        self.cv.coords.assert_any_call(label, 130., 50.)
        self.cv.reset_mock()
        chart.update(self.idx[1])
        self.cv.coords.assert_any_call(label, 130., 60.)
        self.cv.coords.assert_any_call(chart._labels["B"], 130., 100.)
        self.cv.itemconfig.assert_any_call(label, text="A  6")
        chart.update(self.idx[2])
        self.cv.itemconfig.assert_any_call(label, state="hidden")
        chart.update(self.idx[0])
        self.cv.itemconfig.assert_any_call(label, state="normal")
        self.cv.create_text.assert_not_called()

    def test_area_sampling_retains_exact_axis_maximum(self):
        df = pd.DataFrame({"A": [1, 100, 2, 3, 4]}, index=pd.date_range("2020", periods=5))
        chart = area_chart(canvas=self.cv, df=df, max_points=2)
        chart.draw(df.index[0])
        chart.update(df.index[-1])
        self.assertEqual(chart.axis2.max_val, 100)
        call = next(c for c in reversed(self.cv.coords.call_args_list) if c.args[0] == chart.areas["A"])
        self.assertEqual(len(call.args)-1, 8)

    def test_area_labels_follow_band_middle_and_hide_when_too_thin(self):
        df = pd.DataFrame({"A": [2., 2., 0.], "B": [2., 2., 4.]}, index=self.idx)
        chart = area_chart(canvas=self.cv, df=df, x_pos=0, y_pos=0,
                           width=100, height=100, label_position="area")
        chart.draw(self.idx[0])
        label = chart._labels["A"]
        self.cv.itemconfig.assert_any_call(label, state="hidden")
        chart.update(self.idx[1])
        self.cv.coords.assert_any_call(label, 50., 25.)
        self.cv.itemconfig.assert_any_call(label, state="normal")
        self.cv.bbox.return_value = (40, 0, 60, 100)
        self.cv.reset_mock()
        chart.update(self.idx[2])
        self.cv.itemconfig.assert_any_call(label, state="hidden")
        self.cv.create_text.assert_not_called()

    def test_validation_and_compatibility(self):
        from sjvisualizer.Bubble import bubble_chart as bubble
        from sjvisualizer.AreaChart import area_chart as area
        from sjvisualizer.AreaPlot import area_plot
        self.assertIs(bubble, bubble_chart)
        self.assertIs(area, area_chart)
        self.assertIs(area_plot, area_chart)
        with self.assertRaises(ValueError):
            area_chart(canvas=self.cv, df=pd.DataFrame({"A": [-1]}, index=self.idx[:1]))
        with self.assertRaises(ValueError):
            self.bubble(df_size=pd.DataFrame({"wrong": [1]}, index=self.idx[:1]))

    def test_demo_playback(self):
        import AITest_Area
        import AITest_Bubble
        for demo in (AITest_Area, AITest_Bubble):
            root = Mock()
            with patch("sjvisualizer.core.canvas.Tk", return_value=root), \
                 patch("sjvisualizer.core.canvas.TkCanvas", return_value=self.cv), \
                 patch("sjvisualizer.core.canvas.canvas._add_sj_logo"), \
                 patch("sjvisualizer.core.canvas.time.sleep"), \
                 patch("sys.argv", [demo.__name__, "--seconds", "1", "--fps", "3"]):
                demo.main()
            self.assertEqual(root.update.call_count, 3)
            root.mainloop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
