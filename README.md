# sjvisualizer

Animate time-series data in Python with pandas and Tkinter. Combine charts,
legends, dates, text, and images on one canvas, then play or record the animation.

## Installation

Use Python 3.9 or newer with Tkinter and a graphical desktop. Python 3.11 is
used for local verification. To install this refactored checkout:

```shell
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

The published package can be installed with `python -m pip install sjvisualizer`,
but may differ from this checkout. On Linux, install your distribution's Tk
package (commonly `python3-tk`). `python -m tkinter` should open a test window.

## Quick start

```python
import numpy as np
import pandas as pd
from sjvisualizer import Canvas, BarRace

frames = 180
index = pd.date_range("2000-01-01", "2025-01-01", periods=frames)
df = pd.DataFrame({"Solar": np.linspace(10, 90, frames),
                   "Wind": np.linspace(70, 40, frames)}, index=index)

cv = Canvas.canvas(width=1200, height=800, include_logo=False)
cv.tk.attributes("-fullscreen", False)
cv.add_title("Energy production")
chart = BarRace.bar_race(canvas=cv, df=df, x_pos=100, y_pos=150,
                         width=900, height=450, number_of_bars=2, unit=" GWh")
cv.add_sub_plot(chart)
cv.add_time(df, time_indicator="year")
cv.play(df=df, fps=30)
cv.tk.mainloop()
```

## Charts and examples

The 24 numbered scripts in the repository root generate their own data and
need no Excel files or downloads:

```shell
python "01. Bar Race Horizontal.py"
python "02. Bar Race Vertical.py" --seconds 20 --fps 60
python "11. Bubble Linear Axes.py" --smoke
```

Available charts include horizontal/vertical bar races, stacked bars,
preaggregated histograms, date/numeric/logarithmic line charts, dynamic lines,
pie/donut races, bubbles, stacked areas, dynamic matrices, and maps. Map presets
cover the world, Europe, US states, Africa, North America, and Asia. Supporting
subplots provide dates, totals, legends, static text/images, and a custom-chart
template.

All numbered examples accept `--seconds`, `--fps`, and `--smoke`. Smoke mode
renders several frames in a hidden Tk window and exits; Tk still needs a display.
See the [example catalogue](docs/chart_migration.md) for every script and API,
and [chart options](docs/chart-options.md) for bounds, labels, bubbles, and areas.
`Examples/Catalogue.py` combines chart types using the bundled Excel data.

## Data and recording

Charts accept pandas DataFrames: rows are animation frames and columns are
categories. Use sorted, unique, timezone-naive dates for time series. Numeric
indices are supported by some charts; see each chart's API. Direct DataFrames
are rendered row by row without automatic interpolation.

Excel input is optional. The first column holds years or Excel dates and the
remaining columns hold numeric category values:

```python
from sjvisualizer import DataHandler

df = DataHandler.DataHandler(
    excel_file="Examples/Data/browsers.xlsx",
    number_of_frames=300,
    tail_frames=0,
    cache=False,
).df
```

The loader interpolates dates and preserves the historical extra seven frames.
Its default final hold is 180 frames. Caching defaults to local pickle files in
`_pandas_cache/`; use `cache_excel=True` for an additional Excel cache. Use caches
you generated yourself, since loading pickle data can execute code.

To record, replace the playback call with:

```python
cv.play(df=df, fps=30, record=True, file_name="output.mp4")
```

Recording uses OpenCV and screen capture: keep the canvas visible and unobscured.
Capture dimensions default to the canvas size. Recording closes the Tk window
when finished, so omit `cv.tk.mainloop()` in that case. Playback is synchronous;
`show_fps=True` enables timing output.

## Migration and documentation

Implementations live in `sjvisualizer/core`, `charts`, `data`, and `utils`.
Package-root module imports such as `from sjvisualizer import Canvas, LineChart`
remain supported. `AreaPlot.area_plot` aliases the stacked area implementation.
The separate `sjvisualizer_legacy` directory and old `plot` convenience API have
been removed. Use chart classes with `Canvas.canvas` as shown above.
Replace `x_lims`/`y_lims` with `x_min`, `x_max`, `y_min`, and `y_max`.

- [Getting started](docs/getting-started.md)
- [Example catalogue and migration behavior](docs/chart_migration.md)
- [Chart configuration](docs/chart-options.md)
- [Framework and playback notes](docs/framework-review.md)
- [Map formats, sources, and rebuild instructions](sjvisualizer/maps/README.md)
- [Contributing, validation, and packaging](docs/contributing.md)

Build the API documentation locally:

```shell
python -m pip install -r docs/requirements.txt
python -m sphinx -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` after building.

## License and support

Released under the [MIT License](LICENSE). Map sources and attribution are
listed in the [map asset guide](sjvisualizer/maps/README.md).
Attribution in your animations is appreciated:

> Made with sjvisualizer, the open-source data animation library for Python

Questions and contributions are welcome through GitHub issues and pull requests.
You can also contact info@sjdataviz.com or
[support the project](https://www.buymeacoffee.com/sjoerdtilmans).
