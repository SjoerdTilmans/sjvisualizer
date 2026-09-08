"""Build Europe/Asia contour JSONs from Natural Earth 1:10m GeoJSON.

python scripts/build_highres_maps.py --countries-geojson path/to/ne_10m_admin_0_countries.geojson
Source: Natural Earth vector repository, tag v5.1.2, geojson/ne_10m_admin_0_countries.geojson.
No simplification is applied; exterior rings are clipped to regional views.
"""
import argparse
import json
import math
from pathlib import Path

from build_map_assets import clip_ring, write_map


LEGACY_NAMES = {"Czechia": "Czech Rep.", "North Macedonia": "Macedonia", "Laos": "Lao PDR"}
VIEWS = {
    "europe": ("Europe", (-25, 32, 51, 72), {"Turkey", "Cyprus", "N. Cyprus", "Georgia", "Armenia", "Azerbaijan"}),
    "asia": ("Asia", (23, -12, 180, 82), {"Russia"}),
}


def project(lon, lat):
    """Mercator in drawing coordinates; latitude is bounded by the viewport."""
    return [(lon+180)*2000/360, 1000-2000/(2*math.pi)*math.log(math.tan(math.pi/4+math.radians(lat)/2))]


def build(path):
    source = json.loads(Path(path).read_text(encoding="utf-8"))
    for name, (continent, bounds, extra) in VIEWS.items():
        records = {}
        for feature in source["features"]:
            props = feature["properties"]
            source_name = props["NAME"]
            if props["CONTINENT"] != continent and source_name not in extra:
                continue
            shape = feature["geometry"]
            if shape["type"] not in ("Polygon", "MultiPolygon"):
                raise ValueError(f"Unsupported geometry: {shape['type']}")
            polygons = shape["coordinates"] if shape["type"] == "MultiPolygon" else [shape["coordinates"]]
            contours = []
            for polygon in polygons:
                ring = clip_ring(polygon[0], bounds)
                if not ring:
                    continue
                area = sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(ring, ring[1:]+ring[:1]))
                if abs(area) < 1e-12:
                    continue
                contours.append([project(*point[:2]) for point in ring])
            if contours:
                key = LEGACY_NAMES.get(source_name, source_name)
                aliases = [source_name] if key != source_name else []
                records[key] = dict(Continent=props["CONTINENT"], Polygon_Type="MultiPolygon",
                    Polygons=contours, Aliases=aliases, Source="Natural Earth 1:10m, repository v5.1.2")
        write_map(name, records)
        print(f"  {sum(len(r) for v in records.values() for r in v['Polygons']):,} contour points")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries-geojson", required=True, type=Path)
    build(parser.parse_args().countries_geojson)
