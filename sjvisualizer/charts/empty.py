"""Minimal subplot template for custom animations."""
from ..core.subplot import sub_plot

__all__ = ["empty"]


class empty(sub_plot):
    """Override draw and update to build a custom animation."""
    def draw(self, time=None):
        pass

    def update(self, time):
        pass
