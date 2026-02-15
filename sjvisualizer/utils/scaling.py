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


def _get_primary_monitor_size() -> tuple[int, int]:
    try:
        from screeninfo import get_monitors  # type: ignore

        m = get_monitors()[0]
        return int(m.width), int(m.height)
    except Exception:
        return 1920, 1080


WIDTH, HEIGHT = _get_primary_monitor_size()
