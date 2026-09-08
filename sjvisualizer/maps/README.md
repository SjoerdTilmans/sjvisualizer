# Packaged contour maps

These files use the existing `world.json` structure: a JSON object keyed by
country or state name. Each record contains `Continent`, `Polygon_Type`, and
`Polygons` (a list of rings of `[x, y]` points). Coordinates are already
projected for drawing, with Y increasing downward. The US map also includes
`Aliases` containing each state's postal abbreviation.

## Sources and generation

- `africa.json` and `north_america.json` are derived
  from this repository's existing `sjvisualizer/world.json`, using its
  `Continent` fields. These retain the source's simplified borders, country
  names, and omissions of some small countries/islands. They are regional
  views of that dataset, not a replacement with updated borders.
- `europe.json` and `asia.json` use **Natural Earth 1:10 million Admin 0
  Countries**, from the Natural Earth vector repository's `v5.1.2` tag:
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_0_countries.geojson
  Dataset documentation and public-domain license:
  https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/
  https://www.naturalearthdata.com/about/terms-of-use/
  Source SHA-256: `239eec57ac17f100a11e2536cffc56752c318b50ae765b0918ff7aab4ce8f255`.
  The maps retain the exterior contour detail without line simplification:
  Europe has 91,052 points (previously 1,650), and Asia has 152,371 points
  (previously 2,916). Files are approximately 2.1 MB and 3.5 MB. Contours are
  clipped to the view, projected, and rounded to five decimal places in drawing
  coordinates. The higher-detail source also adds small regions and territories.
  Existing keys are retained, including `Czech Rep.`, `Macedonia`, and `Lao PDR`;
  their modern source names are accepted as aliases. Natural Earth's default
  boundary representation is retained, including separately represented
  disputed areas; the chart does not reinterpret their status.
- `usa_states.json` is derived from the US Census Bureau's **2024 Cartographic
  Boundary File, State and Equivalent Entities, 1:20,000,000**:
  https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_us_state_20m.zip
  Documentation: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
  Census-produced geographic data is public domain. The JSON includes the 50
  states and DC; Puerto Rico and other territories are excluded. Postal codes
  come from the source `STUSPS` field. Only exterior rings are retained.

The US map uses spherical Albers equal-area projections, with Alaska and
Hawaii separately scaled and repositioned as insets. Inset sizes and locations
are for readability and are not geographically comparable to the mainland.

Europe includes Turkey, Cyprus, and the South Caucasus for context. The view
clips eastern Russia and overseas French territory to longitude -25..51 and
latitude 32..72. Asia includes Russia, with longitude 23..180 and latitude
-12..82, excluding the wrapped fragments across the antimeridian. Both views
use Mercator projection. These rectangular crops are display viewports, not definitions
of continental borders. North America includes Central America, the
Caribbean, and Greenland as represented in the original dataset.

Rebuild the five files without additional Python dependencies:

```powershell
python scripts/build_map_assets.py --states-zip path/to/cb_2024_us_state_20m.zip
python scripts/build_highres_maps.py --countries-geojson path/to/ne_10m_admin_0_countries.geojson
```

The first script builds Africa, North America, and US states. The second
builds Europe and Asia from the pinned Natural Earth GeoJSON. Neither adds a
runtime dependency. The runtime chart never downloads data. Restart Python
after regenerating assets to clear the geometry cache.

## Custom maps

Use `from sjvisualizer import Map` and `Map.map(canvas=cv, df=df)` for the
default world view. Set `map_name="europe"` (or another preset) to select a
region. Direct imports are also available from `sjvisualizer.Map` and
`sjvisualizer.charts.map`.

Pass `map_file="path/to/contours.json"` to use your own projected geometry:

```json
{
  "Region A": {
    "Polygons": [[[0, 0], [100, 0], [100, 80], [0, 80]]],
    "Aliases": ["A"]
  }
}
```

Match dataframe columns to JSON keys or aliases (case-insensitive). The chart
fits the contours to its bounding box without mutating the source geometry.
Regions with no valid values stay grey. Unmatched dataframe columns do not
affect the legend scale. If both a name and its alias have values, the larger
valid value is used, consistent with the existing Russia/USSR aliases.

Historical nested Polygon/MultiPolygon arrays are accepted as well. Rings are
rendered as filled polygons; holes are not subtracted. JSON files are cached
by map name/path, so start a new Python process after editing a custom file.
