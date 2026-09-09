"""Load packaged or custom contour JSON files without changing source geometry."""
from functools import lru_cache
import json
from pathlib import Path

import numpy as np

MAP_NAMES = ("world", "europe", "usa_states", "africa", "north_america", "asia")
_ALIASES = {"afrika": "africa", "usa": "usa_states", "us": "usa_states",
            "us_states": "usa_states", "united_states": "usa_states"}


def map_name(value):
    key = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    key = _ALIASES.get(key, key)
    if key not in MAP_NAMES:
        raise ValueError(f"Unknown map {value!r}; choose from {', '.join(MAP_NAMES)}")
    return key


def _rings(coords):
    if not isinstance(coords, list) or not coords:
        raise ValueError("Polygons must contain nonempty coordinate arrays")
    if isinstance(coords[0], list) and coords[0] and isinstance(coords[0][0], (int, float)):
        points = np.asarray(coords, dtype=float)
        if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3 or not np.isfinite(points).all():
            raise ValueError("Each polygon needs at least three finite [x, y] points")
        yield points.tolist()
    else:
        for child in coords:
            yield from _rings(child)


@lru_cache(maxsize=16)
def geometry(name="world", custom_path=None):
    """Return normalized records; callers must treat this cached value as read-only.

    Coordinate rings may use the historical Polygon/MultiPolygon nesting or
    a flat list of rings. Coordinates are projected pixels, with Y downward.
    """
    root = Path(__file__).resolve().parents[1]
    path = Path(custom_path) if custom_path else root/"world.json" if name == "world" else root/"maps"/(name+".json")
    with path.open(encoding="utf-8") as stream:
        records = json.load(stream)
    if not isinstance(records, dict) or not records:
        raise ValueError("Map JSON must be a nonempty object keyed by region name")
    normalized = {}
    for key, record in records.items():
        if not isinstance(record, dict) or "Polygons" not in record:
            raise ValueError(f"Map region {key!r} needs a Polygons array")
        aliases = record.get("Aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise ValueError(f"Aliases for {key!r} must be a list of strings")
        normalized[key] = {**record, "Polygons": list(_rings(record["Polygons"])), "Aliases": list(aliases)}
    return normalized
