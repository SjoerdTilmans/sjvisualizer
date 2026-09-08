"""Regional map geometry, loading and rendering regressions."""
import copy
import json
from pathlib import Path
import tempfile
import tkinter
import unittest
from unittest.mock import Mock

import numpy as np
import pandas as pd

from example_loader import build_chart, demo_data
from sjvisualizer import Map
from sjvisualizer.data.maps import geometry, MAP_NAMES


class RegionalMapTests(unittest.TestCase):
    def setUp(self):
        self.cv = Mock(spec=tkinter.Canvas)
        ids = iter(range(100000))
        for method in ("create_polygon", "create_rectangle", "create_text"):
            getattr(self.cv, method).side_effect = lambda *a, **kw: next(ids)

    def test_presets_have_expected_regions(self):
        cases = {"europe": ("Netherlands", "Brazil"), "africa": ("Nigeria", "Germany"),
                 "north_america": ("Mexico", "Russia"), "asia": ("Russia", "France"),
                 "usa_states": ("California", "Puerto Rico")}
        for name, (included, excluded) in cases.items():
            data = geometry(name)
            self.assertIn(included, data)
            self.assertNotIn(excluded, data)
        states = geometry("usa_states")
        self.assertEqual(len(states), 51)
        self.assertTrue({"Alaska", "Hawaii", "District of Columbia"} <= states.keys())
        self.assertEqual(states["California"]["Aliases"], ["CA"])

    def test_high_resolution_maps_keep_legacy_keys_and_small_regions(self):
        for name, minimum in (("europe", 90000), ("asia", 150000)):
            data = geometry(name)
            self.assertGreater(sum(len(r) for v in data.values() for r in v["Polygons"]), minimum)
            self.assertTrue(all(v["Source"].startswith("Natural Earth 1:10m") for v in data.values()))
        europe, asia = geometry("europe"), geometry("asia")
        self.assertTrue({"Czech Rep.", "Macedonia", "Netherlands", "Monaco", "Malta"} <= europe.keys())
        self.assertEqual(europe["Czech Rep."]["Aliases"], ["Czechia"])
        self.assertIn("Laos", asia["Lao PDR"]["Aliases"])
        self.assertTrue({"China", "India", "Japan", "Singapore", "Bahrain"} <= asia.keys())

    def test_all_presets_fit_and_preserve_geometry(self):
        df = pd.DataFrame({"China": [10., 20.], "Germany": [12., 24.]})
        for name in MAP_NAMES:
            with self.subTest(map=name):
                before = copy.deepcopy(geometry(name))
                self.cv.reset_mock()
                for width, height in ((900, 400), (300, 700)):
                    c = Map.map(self.cv, df, map_name=name, x_pos=20, y_pos=30,
                                          width=width, height=height)
                    self.cv.reset_mock()
                    c.draw(0)
                    for call in self.cv.create_polygon.call_args_list:
                        points = np.asarray(call.args).reshape(-1, 2)
                        self.assertTrue(np.isfinite(points).all())
                        self.assertTrue((points >= [20-1e-6, 30-1e-6]).all())
                        self.assertTrue((points <= [20+width+1e-6, 30+height+1e-6]).all())
                    self.cv.reset_mock()
                    c.update(1)
                    c.update(0)
                    self.cv.create_polygon.assert_not_called()
                self.assertEqual(before, geometry(name))

    def test_state_aliases_and_unrelated_columns(self):
        df = pd.DataFrame({"CA": [20., np.nan], "texas": [30., 40.], "China": [1e9, 1e9]})
        c = Map.map(self.cv, df, map_name="USA states")
        c.draw(0)
        self.assertEqual(c.current_max_value, 30)
        self.assertNotEqual(c._fills["California"], c.missing_color)
        self.assertEqual(c._fills["Alaska"], c.missing_color)
        c.update(1)
        self.assertEqual(c._fills["California"], c.missing_color)
        self.assertEqual(c.current_max_value, 40)

    def test_map_name_aliases_and_invalid_name(self):
        df = demo_data(2)
        self.assertEqual(Map.map(self.cv, df).map_name, "world")
        for value, expected in (("Afrika", "africa"), ("North America", "north_america"),
                                ("US", "usa_states"), ("Europe", "europe")):
            self.assertEqual(Map.map(self.cv, df, map_name=value).map_name, expected)
        with self.assertRaises(ValueError):
            Map.map(self.cv, df, map_name="unknown")

    def test_custom_contour_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"custom.json"
            data = {"Test": {"Polygons": [[[5, 5], [10, 5], [10, 10]]], "Aliases": ["T"]}}
            path.write_text(json.dumps(data), encoding="utf-8")
            c = Map.map(self.cv, pd.DataFrame({"T": [10]}), map_file=path)
            c.draw(0)
            self.assertEqual(set(c.countries), {"Test"})
            self.assertNotEqual(c._fills["Test"], c.missing_color)
            malformed = Path(directory)/"invalid.json"
            malformed.write_text('{"Bad": {"Polygons": [[[0, 0]]]}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                Map.map(self.cv, demo_data(2), map_file=malformed)

    def test_new_demos_draw_and_seek(self):
        for name in ("Europe Map", "USA States Map", "Africa Map", "North America Map", "Asia Map"):
            df = demo_data(4)
            c = build_chart(name, self.cv, df)
            c.draw(df.index[0])
            c.update(df.index[-1])
            c.update(df.index[0])
            self.assertTrue(any(color != c.missing_color for color in c._fills.values()))


if __name__ == "__main__":
    unittest.main()
