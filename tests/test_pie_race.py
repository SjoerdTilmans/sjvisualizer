"""PieRace regressions using a canvas mock, without opening a window."""

import tkinter
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from sjvisualizer import PieRace, pie_plot
from sjvisualizer.PieRace import pie_plot as compatibility_pie_plot


class PieRaceTests(unittest.TestCase):
    def chart(self, data, **kwargs):
        surface = Mock(spec=tkinter.Canvas)
        ids = iter(range(10000))
        for method in ("create_arc", "create_text", "create_line", "create_image", "create_oval"):
            getattr(surface, method).side_effect = lambda *a, **k: next(ids)
        chart = pie_plot(df=pd.DataFrame(data), canvas=surface,
                         width=800, height=600, x_pos=0, y_pos=0,
                         display_images=False, **kwargs)
        chart.set_root(Mock())
        return chart, surface

    def test_imports(self):
        self.assertIs(PieRace.pie_plot, pie_plot)
        self.assertIs(compatibility_pie_plot, pie_plot)

    def test_aggregation_and_sort(self):
        chart, _ = self.chart({"A": [60], "B": [36], "tiny": [1], "Other": [2], "Others": [1]})
        self.assertEqual(list(chart._targets(0)), ["A", "B", "Other"])
        self.assertAlmostEqual(chart._shares["Other"], 0.04)
        self.assertAlmostEqual(sum(chart._shares.values()), 1)

    def test_invalid_and_empty_frames_recover(self):
        chart, cv = self.chart({"A": [1, 0, 5], "B": [np.nan, -1, np.inf]}, smoothing=1)
        chart.update(1)
        self.assertEqual(sum(chart._shares.values()), 0)
        chart.update(2)
        self.assertEqual(chart._shares["A"], 1)
        self.assertTrue(all(np.isfinite(v) for v in chart._shares.values()))
        self.assertTrue(any(call.kwargs.get("extent") == 359.999999 for call in cv.itemconfig.call_args_list))

    def test_overflow_safe_normalization(self):
        chart, _ = self.chart({"A": [1e308], "B": [1e308]})
        self.assertEqual(chart._shares["A"], 0.5)
        self.assertEqual(chart._shares["B"], 0.5)

    def test_fade_out_and_reappearance_reuse_items(self):
        chart, cv = self.chart({"A": [80, 0, 80], "B": [20, 100, 20]}, smoothing=0.25)
        original = chart.pies["A"].arc
        for _ in range(100):
            chart.update(1)
            self.assertAlmostEqual(sum(chart._shares.values()), 1)
            self.assertTrue(all(v >= 0 for v in chart._shares.values()))
        self.assertEqual(chart._shares["A"], 0)
        cv.reset_mock()
        chart.update(2)
        self.assertEqual(chart.pies["A"].arc, original)
        cv.create_arc.assert_not_called()
        cv.delete.assert_not_called()

    def test_percentages_without_names_and_stable_frames(self):
        chart, cv = self.chart({"A": [75], "B": [25]}, display_label=False)
        self.assertIsNone(chart.pies["A"].label)
        self.assertIsNotNone(chart.pies["A"].percent)
        cv.reset_mock()
        chart.update(0)
        cv.coords.assert_not_called()
        cv.itemconfig.assert_not_called()
        cv.tag_raise.assert_not_called()
        chart.draw(0)
        cv.create_arc.assert_not_called()

    def test_smoothed_frames_settle_and_stop_redrawing(self):
        chart, cv = self.chart({"A": [80, 20], "B": [20, 80]})
        for _ in range(150):
            chart.update(1)
        cv.reset_mock()
        chart.update(1)
        cv.coords.assert_not_called()
        cv.itemconfig.assert_not_called()

    def test_root_demo_playback_wiring(self):
        from example_loader import load_example
        main = load_example("Pie Race")

        _, surface = self.chart({"A": [1]})
        root = Mock()
        with patch("sjvisualizer.core.canvas.Tk", return_value=root), \
                patch("sjvisualizer.core.canvas.TkCanvas", return_value=surface), \
                patch("sjvisualizer.core.canvas.font.Font"), \
                patch("sjvisualizer.core.canvas.canvas._add_sj_logo"), \
                patch("sjvisualizer.charts.pie_race.ImageTk.PhotoImage"), \
                patch("sjvisualizer.core.canvas.time.sleep"), \
                patch("sys.argv", ["10. Pie Race.py", "--seconds", "1", "--fps", "10"]):
            main.main()
        self.assertEqual(root.update.call_count, 10)
        root.mainloop.assert_called_once()

    def test_rank_swap_moves_slices_and_labels_gradually(self):
        chart, cv = self.chart({"A": [51, 49], "B": [49, 51]}, smoothing=0.2)
        old = {name: item._last[0] for name, item in chart.pies.items()}
        cv.reset_mock()
        chart.update(1)
        self.assertGreater(chart._starts["A"], old["A"])
        self.assertLess(chart._starts["A"], 40)
        self.assertLess(chart._starts["B"], old["B"])
        self.assertGreater(chart._starts["B"], 140)
        item = chart.pies["A"]
        angle = np.deg2rad(item._last[0] + item._last[1] * 180)
        label_call = next(call for call in cv.coords.call_args_list if call.args[0] == item.label)
        np.testing.assert_allclose(label_call.args[1:], [
            chart._cx + 1.12 * chart._radius * np.cos(angle),
            chart._cy - 1.12 * chart._radius * np.sin(angle),
        ])
        cv.create_arc.assert_not_called()
        for _ in range(150):
            chart.update(1)
        self.assertAlmostEqual(chart._starts["B"], 0)
        self.assertAlmostEqual(chart._starts["A"], 0.51 * 360)

    def test_rank_change_during_swap_continues_from_displayed_position(self):
        chart, _ = self.chart({"A": [51, 49], "B": [49, 51]}, smoothing=0.2)
        chart.update(1)
        previous = chart._starts["A"]
        chart.update(0)
        self.assertGreater(chart._starts["A"], 0)
        self.assertLess(chart._starts["A"], previous)
        self.assertAlmostEqual(chart._starts["A"], previous * 0.8)
        # Explicit draws reset both size and position without residual motion.
        chart.draw(1)
        self.assertEqual(chart._starts["B"], 0)
        self.assertAlmostEqual(chart._starts["A"], 0.51 * 360)

    def test_unsorted_slices_remain_contiguous_while_sizes_animate(self):
        chart, _ = self.chart({"A": [80, 20], "B": [20, 80]}, sort=False)
        chart.update(1)
        self.assertEqual(chart._starts["A"], 0)
        self.assertAlmostEqual(chart._starts["B"], chart._shares["A"] * 360)

    def test_smoothing_one_applies_rank_change_immediately(self):
        chart, _ = self.chart({"A": [80, 20], "B": [20, 80]}, smoothing=1)
        chart.update(1)
        self.assertEqual(chart._starts["B"], 0)
        self.assertAlmostEqual(chart._starts["A"], 0.8 * 360)

    def assert_canvas_circle_covered(self, chart, cv):
        """Check the union of actual Tk arc commands, including wraparound."""
        states = {}
        for call in cv.itemconfig.call_args_list:
            states.setdefault(call.args[0], {}).update(call.kwargs)
        for layer in ("arc", "shade"):
            intervals = []
            for item in chart.pies.values():
                config = states[getattr(item, layer)]
                if config["state"] == "hidden":
                    continue
                start = config["start"] % 360
                end = start + config["extent"]
                intervals.append((start, min(end, 360)))
                if end > 360:
                    intervals.append((0, end - 360))
            if not any(chart._shares.values()):
                self.assertEqual(intervals, [])
                continue
            covered = 0
            for start, end in sorted(intervals):
                # Tk's full-circle workaround leaves <0.000001 degrees.
                self.assertLessEqual(start, covered + 2e-6, (layer, intervals))
                covered = max(covered, end)
            self.assertAlmostEqual(covered, 360, places=5)

    def test_circle_stays_filled_during_rank_swap_and_size_changes(self):
        for sort in (True, False):
            chart, cv = self.chart({"A": [51, 49, 80], "B": [49, 51, 20]}, sort=sort)
            for frame in [1] * 12 + [2] * 12 + [0] * 100:
                chart.update(frame)
                self.assert_canvas_circle_covered(chart, cv)
            for name, item in chart.pies.items():
                self.assertAlmostEqual(item._last_extent, chart._shares[name] * 360, places=5)

    def test_circle_coverage_during_retargeting_disappearance_and_empty_frames(self):
        rng = np.random.default_rng(14)
        values = rng.uniform(0, 100, (60, 6))
        values[values < 30] = 0
        values[20] = 0
        values[40] = [100, 0, 0, 0, 0, 0]
        chart, cv = self.chart(pd.DataFrame(values), smoothing=0.3)
        for frame in range(len(values)):
            chart.update(frame)
            self.assert_canvas_circle_covered(chart, cv)

    def test_covering_edges_handle_equal_angles_and_wraparound(self):
        chart, cv = self.chart({"A": [40], "B": [40], "C": [20]})
        chart._starts.update(A=350, B=350, C=710)
        extents = chart._covering_extents()
        for name, item in chart.pies.items():
            item.render(chart._starts[name], chart._shares[name], extents[name])
        self.assert_canvas_circle_covered(chart, cv)
        # A neighbor moving away must update a stationary wedge's fill too.
        item = chart.pies["A"]
        cv.reset_mock()
        item.render(350, 0.4, 200)
        item.render(350, 0.4, 220)
        arc_calls = [call for call in cv.itemconfig.call_args_list if call.args[0] == item.arc]
        self.assertEqual([call.kwargs["extent"] for call in arc_calls], [200, 220])

    def test_unsorted_order_and_exact_shares(self):
        chart, _ = self.chart({"A": [10, 90], "B": [90, 10]}, sort=False, smoothing=1)
        self.assertEqual(chart._order, ["A", "B", "Other"])
        chart.update(1)
        self.assertEqual(chart._order, ["A", "B", "Other"])
        self.assertAlmostEqual(chart._shares["A"], 0.9)

    def test_icon_is_loaded_only_once_when_visible(self):
        chart, _ = self.chart({"A": [0, 100, 0, 100], "B": [100, 0, 100, 0]}, smoothing=1)
        chart.display_images = True
        with patch("sjvisualizer.charts.pie_race.Image.open", side_effect=FileNotFoundError) as opened:
            chart.update(1)
            chart.update(2)
            chart.update(3)
        self.assertEqual(opened.call_count, 2)

    def test_fading_slices_never_send_subpixel_arcs_to_tk(self):
        chart, cv = self.chart({"A": [80, 80, 80], "B": [20, 0, 20]})
        for frame in [1] * 90 + [2] * 90:
            chart.update(frame)
            self.assert_canvas_circle_covered(chart, cv)
        for call in cv.itemconfig.call_args_list:
            if "extent" in call.kwargs:
                if call.kwargs["state"] == "normal":
                    self.assertGreaterEqual(call.kwargs["extent"], chart._minimum_arc_extent())
                else:
                    self.assertEqual(call.kwargs["extent"], 0)

    def test_subpixel_slice_is_hidden_and_neighbors_cover_its_space(self):
        for size in (50, 600, 2000):
            chart, cv = self.chart({"A": [50], "B": [49.99999], "tiny": [0.00001]}, min_slice=0)
            chart._radius = size * 0.34
            chart.draw(0)
            extents = chart._covering_extents()
            self.assertEqual(extents["tiny"], 0)
            self.assertLess(extents["A"], 181)
            self.assertLess(extents["B"], 181)
            self.assert_canvas_circle_covered(chart, cv)

    def test_bad_configuration(self):
        with self.assertRaises(ValueError):
            pie_plot(df=pd.DataFrame())
        for kwargs in ({"smoothing": 0}, {"inner_radius": 1}, {"min_slice": -1},
                       {"min_percentage": np.nan}, {"decimal_places": -1}):
            with self.assertRaises(ValueError):
                pie_plot(df=pd.DataFrame({"A": [1]}), **kwargs)
        with self.assertRaisesRegex(ValueError, "unique"):
            pie_plot(df=pd.DataFrame([[1, 2]], columns=["A", "A"]))


if __name__ == "__main__":
    unittest.main()
