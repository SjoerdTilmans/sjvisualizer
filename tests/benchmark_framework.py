"""Run with: python tests/benchmark_framework.py (no GUI required).

Compare the original per-point coordinate mapping with the bulk mapping used
by line charts. This measures Python projection cost, not end-to-end Tk FPS.
"""

from pathlib import Path
import sys
import timeit

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sjvisualizer.core.axis import axis


def main():
    xaxis = axis.__new__(axis)
    xaxis.min_val, xaxis.max_val = 0, 1000
    xaxis.length = 1200
    xaxis.is_date = xaxis.is_log_scale = False
    yaxis = axis.__new__(axis)
    yaxis.min_val, yaxis.max_val = -100, 100
    yaxis.length = 600
    yaxis.is_date = yaxis.is_log_scale = False

    for count in (100, 1000, 10000):
        xs = np.linspace(0, 1000, count).tolist()
        ys = np.linspace(-100, 100, count).tolist()

        def scalar():
            coords = []
            for xv, yv in zip(xs, ys):
                coords.extend([100 + xaxis.calc_positions(xv),
                               700 - yaxis.calc_positions(yv)])
            return coords

        def bulk():
            coords = np.empty((count, 2))
            coords[:, 0] = 100 + xaxis.calc_positions_many(xs)
            coords[:, 1] = 700 - yaxis.calc_positions_many(ys)
            return coords.ravel().tolist()

        np.testing.assert_allclose(scalar(), bulk())
        repetitions = max(100, 100000 // count)
        before = min(timeit.repeat(scalar, number=repetitions, repeat=3)) / repetitions
        after = min(timeit.repeat(bulk, number=repetitions, repeat=3)) / repetitions
        print(f"{count:5} points: scalar {before * 1e6:8.1f} us; "
              f"bulk {after * 1e6:8.1f} us; {before / after:.2f}x")


if __name__ == "__main__":
    main()
