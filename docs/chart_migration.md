# Migrated charts

The remaining chart implementations now live under `sjvisualizer/charts` and
use the new `core.subplot`, `core.axis`, and shared color/format helpers. The
legacy directory is retained as an archive; migrated implementations do not
import it. `AreaPlot` and the old BarRace variants already have replacements,
so no duplicate implementations were added for them.

| Root example | Public API |
| --- | --- |
| `01. Bar Race Horizontal.py` | `BarRace.bar_race` |
| `02. Bar Race Vertical.py` | `BarRace.bar_race` |
| `03. Stacked Bar Chart.py` | `StackedBarChart.stacked_bar_chart` |
| `04. Histogram.py` | `Histogram.histogram` |
| `05. Line Single Axis.py` | `LineChart.line_chart` |
| `06. Line Numeric XY.py` | `LineChart.line_chart` |
| `07. Line Log Y.py` | `LineChart.line_chart` |
| `08. Line Log XY.py` | `LineChart.line_chart` |
| `09. Dynamic Line.py` | `DynamicLine.dynamic_curve` |
| `10. Pie Race.py` | `PieRace.pie_plot` |
| `11. Bubble Linear Axes.py` | `Bubble.bubble_chart` |
| `12. Bubble Log Axes.py` | `Bubble.bubble_chart` |
| `13. Area Chart.py` | `AreaChart.area_chart` |
| `14. Dynamic Matrix.py` | `DynamicMatrix.dynamic_matrix` |
| `15. World Map.py` | `Map.map` |
| `16. Europe Map.py` | `Map.map` |
| `17. USA States Map.py` | `Map.map` |
| `18. Africa Map.py` | `Map.map` |
| `19. North America Map.py` | `Map.map` |
| `20. Asia Map.py` | `Map.map` |
| `21. Date.py` | `Date.date` |
| `22. Total.py` | `Total.total` |
| `23. Legend.py` | `Legend.legend` |
| `24. Empty.py` | `MovingDot` |

Run from the repository root:

```shell
python "01. Bar Race Horizontal.py"
python "02. Bar Race Vertical.py"
python "15. World Map.py" --seconds 20 --fps 60
```

Each example contains its own data generation, chart configuration, argument
parsing, and playback loop. There is no shared demo runner. All examples work
without downloads or Excel files. Close the window after playback.
`--smoke` renders the initial, middle, final, and initial frames again in a
withdrawn Tk window, then exits. It requires a working Tk installation.

The line examples cover a date X axis with a single Y scale, numeric X/Y
values (the former MultiAxis example), logarithmic Y, and logarithmic X/Y.
Bubble examples cover linear X/Y and logarithmic X/Y, with a separate linear
size variable. Bubble supports `--no-labels`; area and pie support `--excel`;
pie also supports `--solid` and `--no-sort`.

Both historical and direct class imports are supported:

```python
from sjvisualizer import Canvas, Histogram, histogram
from sjvisualizer.Histogram import histogram
from sjvisualizer.charts.histogram import histogram
```

Use `canvas.add_sub_plot(chart)` to attach a chart and draw its initial frame.
Pass `df` to `canvas.play`, or let playback infer it from an attached chart.

## Data and behavior

- Rows are animation frames and columns are categories. Frames must be sorted,
  unique, and nonmissing; column names must be unique. Numeric frame indices
  require exact lookup. Datetime indices use the nearest available row.
- Numeric data is copied and cached at construction. Construct a new chart to
  reflect edited data. Missing/infinite values become zero, except maps show
  missing data in `missing_color`. Stacked bars reject negative values.
- Histogram retains the legacy meaning: preaggregated categorical bars,
  rather than raw observations requiring binning. It supports negative bars.
- Dynamic Line connects categories in column order. For X/Y data, use the
  existing LineChart with two dataframes.
- Histogram and Dynamic Line use cumulative bounds by default, recomputed correctly
  when seeking backward. `allow_decrease=True` uses the current frame's bounds.
- Stacked bars sample up to `number_of_bars` evenly spaced rows, including the
  endpoints when there is more than one bar. Each bar appears at its sampled
  frame. Item counts are bounded, skipped frames work, and short/single-row or
  zero-valued datasets are supported. New bars rise with a damped spring;
  the first bar spans the chart width and existing bars narrow smoothly as
  new ones enter. `animation_frames=24` controls the transition length in
  playback frames (use 0 for instant transitions), and `bar_gap=0.08` controls
  spacing. Repeated updates at the final timestamp settle the last bar; the
  root example includes this hold automatically. Seeking restores animation
  progress from the destination frame. The legacy 600-frame pause is removed.
- World Map loads packaged `world.json` lazily, preserves source coordinates
  across instances, fits both dimensions, and only updates changed fills.
  Countries and legend share five discrete equal-width color ranges by default;
  set `legend_bins` to change the count. Grey countries have missing data and
  a separate "No data" legend entry. Zero is valid data. Finite values outside
  the scale clamp to its endpoint colors, relative to `min_value`. Data columns must
  match the names in `world.json`; `USSR` and `USSR/Russia` also color Russia.
  This is the archived map geometry, not an updated geopolitical dataset.
  Automatic boundaries use round steps (1, 2, or 5 times a power of ten),
  rounding the scale outward to cover the data. For example, a maximum of 83
  produces boundaries 0, 20, 40, 60, 80, 100 with the default settings.
  Set `legend_values=[0, 10, 25, 50, 100, 200]` to supply fixed boundaries,
  including unequal ranges. This overrides `legend_bins` and `min_value`;
  country colors use those exact boundaries throughout playback. Values
  outside the boundaries use the first or last color. Each range still gets
  an equally sized legend swatch.
  `map_name` defaults to `"world"`; choose `"europe"`, `"usa_states"`,
  `"africa"` (also `"afrika"`), `"north_america"`, or `"asia"` for regional
  contours. US states accept names or postal abbreviations, including DC.
  All map presets support the same legend, colors, and playback options.
  `map_file` accepts a custom contour JSON. See the
  [map asset guide](../sjvisualizer/maps/README.md) for the format, coverage,
  projections, source attribution, and the asset rebuild command.
- Dynamic Matrix clips positions to the configured sentiment levels and blends
  endpoint colors through neutral gray. The old special five-color palette is
  replaced by this consistent scale for all level counts.
- Legend supports stable value ranking and vertical/horizontal layouts. Rank
  changes are immediate and deterministic rather than spring-based. Date and
  Total format the initial frame correctly and skip unchanged text updates.
- Empty is a no-op template; its example subclasses it to animate a dot.

The old `plot.py` convenience functions remain in the legacy archive. This
migration concerns chart classes and supporting subplots, not that wrapper API.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

`tests/test_migrated_charts.py` checks initial rendering, object reuse, seeking,
zero/negative/missing data, category positions, geometry
isolation, formatting, validation, and compatibility imports using a mocked
Tk canvas. Use the examples' `--smoke` option for actual Tk rendering.
