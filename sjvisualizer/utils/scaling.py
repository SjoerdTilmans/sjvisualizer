"""Scaling and display-size utilities.

Centralizes:
- SCALEFACTOR (Windows DPI scaling)
- WIDTH/HEIGHT (primary monitor resolution)

All values are computed safely (won't crash in headless/CI).
"""

from __future__ import annotations

import ctypes
import platform


def _get_scalefactor() -> float:
    system = platform.system()
    if system == "Windows":
        try:
            return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        except Exception:
            return 1.0
    # macOS/Linux default to 1 unless you add explicit detection
    return 1.0


SCALEFACTOR: float = _get_scalefactor()

# Font sizes exposed by the public chart API are logical pixels.  Tk expects
# positive font sizes in points, so compensate for Windows display scaling in
# one place instead of letting individual charts apply different conversions.
DEFAULT_FONT_SIZE: int = 25


def tk_font_size(size: float, *, minimum: int = 1) -> int:
    """Convert a public logical font size to the size expected by Tk."""

    return max(int(minimum), int(float(size) / SCALEFACTOR))


def _get_primary_monitor_size() -> tuple[int, int]:
    try:
        from screeninfo import get_monitors  # type: ignore

        m = get_monitors()[0]
        return int(m.width), int(m.height)
    except Exception:
        return 1920, 1080


WIDTH, HEIGHT = _get_primary_monitor_size()
