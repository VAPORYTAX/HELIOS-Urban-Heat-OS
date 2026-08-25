from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import httpx
from pyproj import Transformer
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import transform

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32612", always_xy=True).transform

@dataclass(frozen=True)
class OSMFeature:
    osm_type: str
    osm_id: int
    tags: dict[str, str]
    geometry: Any

def build_query(south: float, west: float, north: float, east: float) -> str:
    bbox = f"{south},{west},{north},{east}"
    lines = [
        "[out:json][timeout:45];",
        "(",
        f'  nwr["building"]({bbox});',
        f'  way["highway"]({bbox});',
        f'  nwr["landuse"~"grass|forest|meadow|recreation_ground"]({bbox});',
        f'  nwr["leisure"~"park|garden"]({bbox});',
        f'  nwr["natural"~"wood|scrub"]({bbox});',
        f'  nwr["amenity"~"school|hospital|clinic|childcare|nursing_home"]({bbox});',
        f'  nwr["public_transport"~"platform|station"]({bbox});',
        f'  node["highway"="bus_stop"]({bbox});',
        ");",
        "out geom;",
    ]
    return "\n".join(lines)

def _geometry(element: dict):
    if element.get("type") == "node" and "lat" in element and "lon" in element:
        return Point(element["lon"], element["lat"])
    coords = [(p["lon"], p["lat"]) for p in element.get("geometry", []) if "lon" in p and "lat" in p]
    if len(coords) >= 4 and coords[0] == coords[-1]:
        poly = Polygon(coords)
        if poly.is_valid and not poly.is_empty:
            return poly
    if len(coords) >= 2:
        return LineString(coords)
    center = element.get("center")
    if center and "lon" in center and "lat" in center:
        return Point(center["lon"], center["lat"])
    return None

def parse_elements(payload: dict) -> list[OSMFeature]:
    rows = []
    for e in payload.get("elements", []):
        geom = _geometry(e)
        if geom is None or geom.is_empty:
            continue
        rows.append(OSMFeature(
            osm_type=e.get("type", "unknown"),
            osm_id=int(e.get("id", 0)),
            tags=dict(e.get("tags") or {}),
            geometry=geom,
        ))
    return rows

def fetch_bbox(south: float, west: float, north: float, east: float, timeout: float = 60.0):
    headers = {"User-Agent": "HELIOS-Urban-Heat-Research/0.7"}
    with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
        r = client.post(OVERPASS_URL, data={"data": build_query(south, west, north, east)})
        r.raise_for_status()
        return parse_elements(r.json())

def road_width_m(tags: dict[str, str]) -> float:
    return {
        "motorway": 18, "trunk": 16, "primary": 14, "secondary": 12,
        "tertiary": 10, "residential": 8, "service": 6, "unclassified": 7,
        "living_street": 6, "pedestrian": 5, "footway": 2.5,
        "cycleway": 3, "path": 2,
    }.get(tags.get("highway", ""), 6)

def classify_facility(tags: dict[str, str]):
    amenity = tags.get("amenity")
    if amenity == "school":
        return "school", 2.0
    if amenity in {"hospital", "clinic"}:
        return "healthcare", 2.5
    if amenity in {"childcare", "nursing_home"}:
        return "vulnerable_care", 2.4
    if tags.get("public_transport") in {"platform", "station"} or tags.get("highway") == "bus_stop":
        return "transit", 1.2
    return None
