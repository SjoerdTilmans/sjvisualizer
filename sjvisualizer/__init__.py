"""sjvisualizer package.

New internal layout:
- core/   : canvas + subplot base classes
- data/   : data handlers
- charts/ : chart implementations
- utils/  : shared helpers

Backwards-compatible imports are preserved for the common pattern:
    from sjvisualizer import Canvas, Axis, DataHandler
"""

from __future__ import annotations

from importlib import import_module

# Expose module-like namespaces for backwards compatibility
Canvas = import_module(".core.canvas", __name__)
Axis = import_module(".core.axis", __name__)
DataHandler = import_module(".data.handler", __name__)

StaticImage = import_module(".charts.static_image", __name__)
StaticText = import_module(".charts.static_text", __name__)
BarRace = import_module(".charts.bar_race", __name__)
PieRace = import_module(".charts.pie_race", __name__)
Bubble = import_module(".charts.bubble", __name__)
AreaChart = import_module(".charts.area_chart", __name__)
AreaPlot = AreaChart
Histogram = import_module(".charts.histogram", __name__)
DynamicLine = import_module(".charts.dynamic_line", __name__)
DynamicMatrix = import_module(".charts.dynamic_matrix", __name__)
StackedBarChart = import_module(".charts.stacked_bar_chart", __name__)
Map = import_module(".charts.map", __name__)
Date = import_module(".charts.date", __name__)
Total = import_module(".charts.total", __name__)
Legend = import_module(".charts.legend", __name__)
Empty = import_module(".charts.empty", __name__)

# Convenience: expose most-used classes directly too
from .core.canvas import canvas  # noqa: E402
from .core.subplot import sub_plot  # noqa: E402
from .core.axis import axis  # noqa: E402

from .data.handler import DataHandler as DataHandlerClass, SizeCompareDataHandler  # noqa: E402

from .charts.bar_race import bar_race  # noqa: E402
from .charts.pie_race import pie_plot  # noqa: E402
from .charts.bubble import bubble_chart  # noqa: E402
from .charts.area_chart import area_chart, area_plot  # noqa: E402
from .charts.static_image import static_image  # noqa: E402
from .charts.static_text import static_text  # noqa: E402
from .charts.histogram import histogram  # noqa: E402
from .charts.dynamic_line import dynamic_curve  # noqa: E402
from .charts.dynamic_matrix import dynamic_matrix  # noqa: E402
from .charts.stacked_bar_chart import stacked_bar_chart  # noqa: E402
from .charts.map import map  # noqa: E402
from .charts.date import date  # noqa: E402
from .charts.total import total  # noqa: E402
from .charts.legend import legend  # noqa: E402
from .charts.empty import empty  # noqa: E402

__all__ = [
    "histogram",
    "dynamic_curve",
    "dynamic_matrix",
    "stacked_bar_chart",
    "map",
    "date",
    "total",
    "legend",
    "empty",
    "Histogram",
    "DynamicLine",
    "DynamicMatrix",
    "StackedBarChart",
    "Map",
    "Date",
    "Total",
    "Legend",
    "Empty",
    "Canvas",
    "Axis",
    "DataHandler",
    "StaticImage",
    "StaticText",
    "BarRace",
    "PieRace",
    "Bubble",
    "AreaChart",
    "AreaPlot",
    "bubble_chart",
    "area_chart",
    "area_plot",
    "canvas",
    "sub_plot",
    "axis",
    "DataHandlerClass",
    "SizeCompareDataHandler",
    "bar_race",
    "pie_plot",
    "static_image",
    "static_text",
]
