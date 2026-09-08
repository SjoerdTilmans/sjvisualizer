"""Load numbered examples for regression tests without starting playback."""
from functools import lru_cache
from pathlib import Path
import runpy
from types import SimpleNamespace


@lru_cache(maxsize=None)
def load_example(title):
    root = Path(__file__).resolve().parents[1]
    path, = root.glob(f"[0-9][0-9]. {title}.py")
    return SimpleNamespace(**runpy.run_path(str(path)))


def demo_data(frames):
    return load_example("Histogram").demo_data(frames)


def build_chart(title, canvas, df):
    return load_example(title).build_chart(canvas, df)
