# Chart options

The snippets below assume you have created a canvas and dataframes as in the
[getting started guide](getting-started.md).

## Custom axis bounds


Set line chart bounds independently; any bound left unset scales automatically:

```python
from sjvisualizer.charts.line_chart import line_chart
from sjvisualizer.charts.bar_race import bar_race

# Date x-axis; use numbers for x_min/x_max when supplying numeric x_df.
lines = line_chart(df=df, canvas=cv,
                   x_min="2000-01-01", x_max="2025-01-01",
                   y_min=50, y_max=500)

# Applies to the value axis for both horizontal and vertical bars.
bars = bar_race(df=df, canvas=cv, axis_min=50)
```

These options default to `None`, preserving automatic bounds. `y_min` overrides
`y_zero_based`. If both bounds are set, the minimum must be less than the maximum.
The former `x_lims=(a, b)` and `y_lims=(a, b)` options have been removed; use
`x_min=a, x_max=b` and `y_min=a, y_max=b` instead.
Bars are clipped at `axis_min`. Choose line chart
bounds that include the data you want to display, as lines are not clipped.

## Line labels


Line charts automatically stack nearby end labels on date axes. When lines
overtake each other, labels smoothly exchange vertical positions while keeping
their endpoint x coordinates. Labels may briefly overlap during the swap.

```python
from sjvisualizer import LineChart

chart = LineChart.line_chart(
    df=df,
    canvas=canvas,
    avoid_label_overlap=True,  # also enables stacking for numeric x_df charts
    label_padding=4,           # extra vertical space between labels, in pixels
    label_relax_iterations=14, # frames per vertical label swap
    label_relax_strength=0.18, # following speed; lower values move more slowly
)
```

Set `avoid_label_overlap=False` to retain independent end labels. If the text
cannot fit within the chart height, the stack extends below the plot instead
of reducing the spacing below the text height.

Line labels whose absolute values round to zero at `y_decimal_places` are
hidden. Set `label_min_value` to use an explicit cutoff.

## Bubble and stacked area charts


Run the self-contained demos from the repository root:

```shell
python "11. Bubble Linear Axes.py"
python "13. Area Chart.py"
```

Both accept `--seconds 15 --fps 60` and `--smoke`. Bubble also accepts
`--no-labels`; use `12. Bubble Log Axes.py` for logarithmic X and Y axes.
Area and pie accept `--excel path/to/data.xlsx`; pie also accepts `--solid`
and `--no-sort`.

```python
from sjvisualizer import Bubble, AreaChart

bubbles = Bubble.bubble_chart(canvas=canvas, df_x=df_x, df_y=df_y, df_size=df_size)
areas = AreaChart.area_chart(canvas=canvas, df=df, display_values=True)
```

Implementations live in `sjvisualizer/charts/bubble.py` and
`sjvisualizer/charts/area_chart.py`. Package-root compatibility imports remain
available, including `AreaPlot.area_plot`, which now uses the complete stacked
area implementation. The separate legacy source directory has been removed.

Bubble frames must have matching indices and categories. Bubble area is
proportional to size; zero, negative, and missing sizes hide the bubble.
Without `df_size`, all markers have diameter `marker_size`. Log axes hide
nonpositive coordinates. Optional `x_min`, `x_max`, `y_min`, and `y_max` fix bounds.

Area data needs sorted, unique, timezone-naive dates and nonnegative values.
Missing/nonfinite values become zero. Colors follow column order, first on top.
The legend supports `external_legend`, `display_legend`, `display_values`, and
`unit`. Set `label_position="right"` to place labels outside the right edge,
centered vertically in each band's latest height (used by `13. Area Chart.py`).
Bands whose values round to zero hide their labels; `label_min_value` sets an
explicit cutoff. Alternatively, `label_position="area"`
places contrasting labels inside each band, hiding labels that cannot fit.
Event ranges use
`events={"Name": ["01/01/2010", "01/01/2013"]}`.
Rendering reuses polygons and samples at most `max_points=1000` history points;
use `max_points=None` to preserve every point, including narrow spikes. Axis
maxima use the full data. Intraday geometry is preserved; shared date ticks
still format dates rather than hours.

