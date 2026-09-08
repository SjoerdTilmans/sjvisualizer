"""End-label animation regression tests without a display or video encoder."""

import unittest
from types import SimpleNamespace

from sjvisualizer.charts.line_chart import _Line, line_chart


class Canvas:
    def __init__(self):
        self.items = {}

    def create_text(self, x, y, **kwargs):
        key = len(self.items)
        self.items[key] = [x, y, kwargs['text']]
        return key

    def coords(self, key, x, y):
        self.items[key][:2] = [x, y]

    def bbox(self, key):
        x, y, text = self.items[key]
        return x - 2, y - 10, x + len(text) * 8 + 2, y + 10


def chart_for(positions, height=200):
    chart = line_chart.__new__(line_chart)
    chart.canvas = Canvas()
    chart.height = height
    chart.y_pos = 0
    chart.label_at_end = chart.avoid_label_overlap = True
    chart.label_padding = 2
    chart.label_min_separation = None
    chart.label_relax_iterations = 8
    chart.label_relax_strength = 0.18
    chart._font = SimpleNamespace(metrics=lambda _: 20, measure=lambda s: len(s) * 8)
    chart.lines = {}
    for i, y in enumerate(positions):
        name = 'Series ' + str(i)
        line = _Line(name, chart.canvas, chart, 'red', None, None,
                     False, 2, True, chart._font)
        line.desired_label_x = 100
        line.desired_label_y = y
        chart.lines[name] = line
    return chart


class LabelLayoutTests(unittest.TestCase):
    def assert_no_overlap(self, chart):
        boxes = [chart.canvas.bbox(line.label_id) for line in chart.lines.values()]
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0]
                                or a[3] <= b[1] + 1e-8 or b[3] <= a[1] + 1e-8,
                                (a, b))

    def test_dense_stack_and_bounds(self):
        for positions in ([1] * 8, [199] * 8, [100] * 8):
            chart = chart_for(positions)
            for _ in range(50):
                chart._layout_end_labels()
                self.assert_no_overlap(chart)
                for line in chart.lines.values():
                    box = chart.canvas.bbox(line.label_id)
                    self.assertGreaterEqual(box[1], -1e-8)
                    self.assertLessEqual(box[3], 200 + 1e-8)

    def test_crossing_swaps_smoothly_at_the_same_x(self):
        chart = chart_for([80, 82, 84])
        chart._layout_end_labels()
        lines = list(chart.lines.values())
        lines[0].desired_label_y = 86
        previous = {line: list(chart.canvas.items[line.label_id][:2]) for line in lines}
        for _ in range(150):
            chart._layout_end_labels()
            if chart._label_swap is None:
                self.assert_no_overlap(chart)
            for line in lines:
                current = chart.canvas.items[line.label_id][:2]
                self.assertEqual(current[0], 100)
                self.assertLess(abs(current[1] - previous[line][1]), 10)
                previous[line] = list(current)
        self.assertLess(lines[1]._label_y, lines[2]._label_y)
        self.assertLess(lines[2]._label_y, lines[0]._label_y)
        self.assertTrue(all(chart.canvas.items[line.label_id][0] == 100 for line in lines))

    def test_moving_endpoints_and_repeated_crossings(self):
        import math
        chart = chart_for([40, 80, 120, 160])
        for frame in range(500):
            for i, line in enumerate(chart.lines.values()):
                line.desired_label_y = 100 + 70 * math.sin(frame / 35 + i)
                line.desired_label_x = 100 + i * 15 + frame / 10
            chart._layout_end_labels()
            for line in chart.lines.values():
                self.assertEqual(chart.canvas.items[line.label_id][0], line.desired_label_x)
            if chart._label_swap is None:
                self.assert_no_overlap(chart)
        for _ in range(100):
            chart._layout_end_labels()
        self.assert_no_overlap(chart)
        self.assertEqual(chart._label_order,
                         sorted(chart.lines.values(), key=lambda line: line.desired_label_y))

    def test_overfull_chart_keeps_text_readable(self):
        chart = chart_for([50] * 15, height=100)
        chart._layout_end_labels()
        self.assert_no_overlap(chart)

    def test_ties_keep_order_and_disabled_layout_does_nothing(self):
        chart = chart_for([100, 100])
        for _ in range(100):
            chart._layout_end_labels()
        self.assertIsNone(chart._label_swap)
        self.assertEqual(chart._label_order, list(chart.lines.values()))
        before = {k: list(v) for k, v in chart.canvas.items.items()}
        chart.avoid_label_overlap = False
        chart.lines['Series 0'].desired_label_y = 190
        chart._layout_end_labels()
        self.assertEqual(before, chart.canvas.items)

    def test_empty_and_single_series(self):
        chart = chart_for([])
        chart._layout_end_labels()
        chart = chart_for([100])
        chart._layout_end_labels()
        self.assertEqual(chart.lines['Series 0']._label_y, 100)

    def test_seed_positions_labels_before_first_update(self):
        import datetime
        chart = chart_for([100, 100])
        chart.x_pos = 0
        for line in chart.lines.values():
            line.xaxis = line.yaxis = SimpleNamespace(calc_positions=lambda v: v)
            line.seed(50, 100, datetime.datetime(2020, 1, 1), x_is_date=False)
        chart._layout_end_labels()
        self.assert_no_overlap(chart)
        self.assertTrue(all(chart.canvas.items[line.label_id][0] == 60
                            for line in chart.lines.values()))


if __name__ == '__main__':
    unittest.main()
