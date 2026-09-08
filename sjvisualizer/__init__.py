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

__all__ = [
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
