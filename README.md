[![Downloads](https://static.pepy.tech/badge/sjvisualizer)](https://pepy.tech/project/sjvisualizer)
# sjvisualizer 📊
sjvisualizer is a data visualization and animation library for Python for time-series data. 

Like this project? Please consider starring ⭐ the project on GitHub!

Or buying me a coffee. It will make my day! [Buy me a Coffee](https://www.buymeacoffee.com/sjoerdtilmans)

## Installation
sjvisualizer is now available on pypi! Simply use pip to install it:

```
pip install sjvisualizer
```

## Basic examples
Using sjvisualizer, you can create a basic data animation with one simple line of code.

### Bar Race


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/9340572c-56f8-4abd-97c5-e8ed674a6751


```python
from sjvisualizer import plot as plt

plt.bar(excel="data/DesktopOS.xlsx", 
        title="Desktop Operating System Market Share", 
        unit="%")
```

### Pie Race


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/5db0d056-578e-4070-b1ba-713e590acd3d


```python
from sjvisualizer import plot as plt

plt.pie(excel="data/browsers.xlsx", 
        title="Desktop Browser Market Share", 
        unit="%")
```

### Animated Line Chart
https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/deae9c3c-8a90-4e64-a036-39fd636746a7
```python
from sjvisualizer import plot as plt

colors = {
    "United States": [
        23,
        60,
        154
    ],
	"Russia": [
        255,
        50,
        50
    ]
}

plt.line(excel="data/military budget.xlsx",
        title="Military Budget of Selected Countries",
        sub_title="in millions of US$",
        colors=colors)
```

### Animated Area Chart


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/6304bb63-1076-4da8-b044-595f763d3546



```python
from sjvisualizer import plot as plt

colors = {
    "United States": [
        23,
        60,
        154
    ],
	"Russia": [
        255,
        50,
        50
    ]
}

plt.stacked_area(excel="data/Nuclear.xlsx",
        title="Nuclear Warheads by Country",
        colors=colors)
```
### Custom axis bounds (non-legacy package)

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

## Data format
Currently sjvisualizer reads data from an Excel file. The format should be as shown in the picture below:

<img width="377" alt="example data format" src="https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/fb5b0665-77f0-4d08-81d5-05c84e02804e">

In this file the first column should contain the dates, and each subsequent column holds the data for the data categories, in this example the different countries.

The date can either be shown as just the year, or as a full date as shown below. In this case, please make sure that Excel recognises the cell as a date.

<img width="651" alt="example data format_long" src="https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/999d1f19-60d6-4a16-a5fb-ea2d17671013">


## More advanced animations
Using sjvisualizer, you can also mix and match chart types and positions like in the following example:


https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/420ed4a0-5bfb-436a-8f61-4e77c640f78f


## Learn sjvisualizer

Want to learn more about sjvisualizer:
- Find additional examples and full documentation on my [website](https://www.sjdataviz.com/software)
- Or follow my course on [Udemy](https://www.sjdataviz.com/course-link)

## Roadmap

![Purple Colorful Modern Roadmap Timeline Infographic (1)](https://github.com/SjoerdTilmans/sjvisualizer/assets/37220662/542e02ec-113c-4fb7-a46a-fc3b65abddd2)


## Usage

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

sjvisualizer is a free and open-source data animation library, please include the following attribution in any publications you use it in.
```
Made with sjvisualizer, the open-source data animation library for Python
```
## SJVisualizer Supporters
<img width="556" height="280" alt="logos-exact_size_vontobel (1)" src="https://github.com/user-attachments/assets/0efa0605-068b-401d-92e8-252c70a09402" />

Do you like what we are doing and want to support this project, get in touch at info@sjdataviz.com

## Bubble and stacked area charts

Run the self-contained demos from the repository root:

```shell
python AITest_Bubble.py
python AITest_Area.py
```

Both accept `--seconds 15 --fps 60`. Bubble also accepts `--log` and
`--no-labels`; area accepts `--excel path/to/data.xlsx`.

```python
from sjvisualizer import Bubble, AreaChart

bubbles = Bubble.bubble_chart(canvas=canvas, df_x=df_x, df_y=df_y, df_size=df_size)
areas = AreaChart.area_chart(canvas=canvas, df=df, display_values=True)
```

Implementations live in `sjvisualizer/charts/bubble.py` and
`sjvisualizer/charts/area_chart.py`. Package-root compatibility imports remain
available, including `AreaPlot.area_plot`, which now uses the complete stacked
area implementation. The original legacy sources remain available for reference.

Bubble frames must have matching indices and categories. Bubble area is
proportional to size; zero, negative, and missing sizes hide the bubble.
Without `df_size`, all markers have diameter `marker_size`. Log axes hide
nonpositive coordinates. Optional `x_min`, `x_max`, `y_min`, and `y_max` fix bounds.

Area data needs sorted, unique, timezone-naive dates and nonnegative values.
Missing/nonfinite values become zero. Colors follow column order, first on top.
The legend supports `external_legend`, `display_legend`, `display_values`, and
`unit`. Set `label_position="right"` to place labels outside the right edge,
centered vertically in each band's latest height (used by `AITest_Area.py`).
Zero-height bands hide their labels. Alternatively, `label_position="area"`
places contrasting labels inside each band, hiding labels that cannot fit.
Event ranges use
`events={"Name": ["01/01/2010", "01/01/2013"]}`.
Rendering reuses polygons and samples at most `max_points=1000` history points;
use `max_points=None` to preserve every point, including narrow spikes. Axis
maxima use the full data. Intraday geometry is preserved; shared date ticks
still format dates rather than hours.

## Contributing
Contributions are always welcome! A couple of ideas to contribute:
- Improve documentation of this project. I have been thinking of setting up a readthedocs page.
- Add additional example scripts. If you do so, please includy any data files and image files so that the example is fully running
- Add new chart types. I have uploaded an example skeleton of new chart types in Empty.py, this is a setup that should serve as a good starting point. (https://github.com/SjoerdTilmans/sjvisualizer/blob/main/sjvisualizer/Empty.py)

Before making any changes, please create your own development branch here on GitHub. Once ready submit a pull request and set me as reviewer!

## Support this project
If you like this project, please concider supporting me using PayPal [Buy me a Coffee](https://www.buymeacoffee.com/sjoerdtilmans).

## License
sjvisualizer is released under the MIT License. See the LICENSE file for more details.

## Contact
If you have any questions or suggestions regarding sjvisualizer, post it on my [forum](https://www.sjdataviz.com/howto-sjvisualizer).
