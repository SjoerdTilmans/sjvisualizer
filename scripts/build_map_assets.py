"""Rebuild Africa, North America and US states (Europe/Asia use build_highres_maps.py).

Usage: python scripts/build_map_assets.py --states-zip path/to/cb_2024_us_state_20m.zip
Only the standard library is needed. See sjvisualizer/maps/README.md for sources.
"""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def rings(coords):
    if not coords:
        return
    if isinstance(coords[0][0], (int, float)):
        yield coords
    else:
        for child in coords:
            yield from rings(child)


def clip_ring(points, bounds):
    """Clip in projected space, keeping regional views inside their viewport."""
    for dimension, bound, sign in ((0, bounds[0], 1), (0, bounds[2], -1),
                                   (1, bounds[1], 1), (1, bounds[3], -1)):
        result = []
        if not points:
            break
        previous = points[-1]
        for point in points:
            inside = sign*(point[dimension]-bound) >= 0
            was_inside = sign*(previous[dimension]-bound) >= 0
            if inside != was_inside:
                t = (bound-previous[dimension])/(point[dimension]-previous[dimension])
                result.append([previous[j]+t*(point[j]-previous[j]) for j in (0, 1)])
            if inside:
                result.append(list(point))
            previous = point
        points = result
    return points if len(points) >= 3 else []


def write_map(name, data):
    path = ROOT/"sjvisualizer"/"maps"/(name+".json")
    path.parent.mkdir(exist_ok=True)
    for record in data.values():
        record["Polygons"] = [[[round(x, 5), round(y, 5)] for x, y in ring]
                              for ring in record["Polygons"]]
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"))+"\n", encoding="utf-8")
    print(f"{name}: {len(data)} regions")


def build_continents():
    world = json.loads((ROOT/"sjvisualizer"/"world.json").read_text(encoding="utf-8"))
    for name, continent, bounds, extra in (
        ("africa", "Africa", None, set()),
        ("north_america", "North America", None, set()),
    ):
        data = {}
        for country, record in world.items():
            if record.get("Continent") != continent and country not in extra:
                continue
            polygons = [clip_ring(r, bounds) if bounds else r for r in rings(record["Polygons"])]
            polygons = [r for r in polygons if r]
            if polygons:
                data[country] = dict(Continent=record["Continent"], Polygon_Type="MultiPolygon", Polygons=polygons)
        write_map(name, data)


def albers(lon, lat, center, parallels, origin):
    """Spherical Albers equal-area projection; outputs drawing coordinates."""
    p1, p2, lat0 = map(math.radians, (*parallels, origin))
    n = (math.sin(p1)+math.sin(p2))/2
    c = math.cos(p1)**2+2*n*math.sin(p1)
    rho0 = math.sqrt(c-2*n*math.sin(lat0))/n
    rho = math.sqrt(c-2*n*math.sin(math.radians(lat)))/n
    delta = (lon-center+180)%360-180
    theta = n*math.radians(delta)
    return [rho*math.sin(theta), rho*math.cos(theta)-rho0]


def fit_group(data, names, box):
    points = [p for name in names for ring in data[name]["Polygons"] for p in ring]
    low = [min(p[i] for p in points) for i in (0, 1)]
    high = [max(p[i] for p in points) for i in (0, 1)]
    scale = min(box[2]/(high[0]-low[0]), box[3]/(high[1]-low[1]))
    shift = [box[i]+(box[i+2]-(high[i]-low[i])*scale)/2 for i in (0, 1)]
    for name in names:
        data[name]["Polygons"] = [[[shift[i]+(p[i]-low[i])*scale for i in (0, 1)]
                                   for p in ring] for ring in data[name]["Polygons"]]


def build_states(path):
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    with zipfile.ZipFile(path) as archive:
        xml = archive.read(next(n for n in archive.namelist() if n.endswith(".kml")))
    data = {}
    for place in ET.fromstring(xml).findall(".//k:Placemark", ns):
        fields = {e.attrib["name"]: e.text for e in place.findall(".//k:SimpleData", ns)}
        if int(fields["STATEFP"]) > 56:
            continue  # 50 states plus DC; territories are not states.
        name = fields["NAME"]
        projection = (-154, (55, 65), 58) if name == "Alaska" else (-157, (8, 18), 20) if name == "Hawaii" else (-96, (29.5, 45.5), 37.5)
        polygons = []
        for node in place.findall(".//k:outerBoundaryIs/k:LinearRing/k:coordinates", ns):
            points = [tuple(map(float, token.split(",")[:2])) for token in node.text.split()]
            polygons.append([albers(lon, lat, *projection) for lon, lat in points])
        data[name] = dict(Continent="North America", Polygon_Type="MultiPolygon",
                          Aliases=[fields["STUSPS"]], Polygons=polygons)
    if len(data) != 51:
        raise ValueError(f"Expected 50 states and DC, got {len(data)}")
    fit_group(data, [n for n in data if n not in ("Alaska", "Hawaii")], (0, 0, 1000, 600))
    fit_group(data, ["Alaska"], (0, 500, 240, 175))
    fit_group(data, ["Hawaii"], (270, 550, 140, 100))
    write_map("usa_states", data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--states-zip", required=True, type=Path)
    args = parser.parse_args()
    build_continents()
    build_states(args.states_zip)
