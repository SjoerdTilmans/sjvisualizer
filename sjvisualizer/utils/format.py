"""Formatting helpers."""

from __future__ import annotations

import math
from typing import Any


months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# Common default used across charts
format_str = "%d-%m-%Y"


def format_date(time_obj, time_indicator: str, format: str = "Europe") -> str:
    if time_indicator == "year":
        return str(time_obj.year)
    if time_indicator == "month":
        return f"{months[time_obj.month]} {time_obj.year}"
    if time_indicator == "day":
        if format == "USA":
            return f"{months[time_obj.month]} {time_obj.day} {time_obj.year}"
        return f"{time_obj.day} {months[time_obj.month]} {time_obj.year}"
    return ""


def format_value(number: Any, decimal: int = 0) -> str:
    """Human-friendly SI-ish suffix formatting (k/m/b/t)."""

    units = ["k", "m", "b", "t"]
    unit_index = 0

    try:
        n = float(number)
    except Exception:
        n = 0.0

    while abs(n) >= 1000 and unit_index < len(units):
        n /= 1000.0
        unit_index += 1

    formatted = f"{n:.{decimal}f}".rstrip(".")
    if formatted.endswith("."):
        formatted = formatted[:-1]

    if unit_index > 0:
        formatted += units[unit_index - 1]

    return formatted


def truncate(n: float, decimals: int = 1) -> float:
    multiplier = 10 ** decimals
    if not math.isnan(n):
        return round(n * multiplier) / multiplier
    return 0.0


def calc_spacing(value: float, current_spacing: float, n: int) -> float:
    # Legacy helper used by some charts to pick tick spacing.
    if current_spacing * 4 < value:
        current_spacing = round(current_spacing * 2, -len(str(round(value))) + 1)
    if not current_spacing:
        current_spacing = 1
    return current_spacing
