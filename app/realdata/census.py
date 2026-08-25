from __future__ import annotations
import math
import os
from pathlib import Path
import httpx
from shapely.geometry import shape

ACS_BASE = "https://api.census.gov/data/2024/acs/acs5"
TIGER_TRACTS_QUERY = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/7/query"

STATE = "04"
COUNTY = "013"

VARIABLES = [
    "NAME",
    "B01001_001E", "B01001_001M",
    "B01001_003E", "B01001_003M",
    "B01001_027E", "B01001_027M",
    "B01001_020E", "B01001_020M",
    "B01001_021E", "B01001_021M",
    "B01001_022E", "B01001_022M",
    "B01001_023E", "B01001_023M",
    "B01001_024E", "B01001_024M",
    "B01001_025E", "B01001_025M",
    "B01001_044E", "B01001_044M",
    "B01001_045E", "B01001_045M",
    "B01001_046E", "B01001_046M",
    "B01001_047E", "B01001_047M",
    "B01001_048E", "B01001_048M",
    "B01001_049E", "B01001_049M",
    "B17001_001E", "B17001_001M",
    "B17001_002E", "B17001_002M",
    "B08201_001E", "B08201_001M",
    "B08201_002E", "B08201_002M",
]

AGE65_EST = [f"B01001_{i:03d}E" for i in list(range(20, 26)) + list(range(44, 50))]
AGE65_MOE = [x[:-1] + "M" for x in AGE65_EST]
UNDER5_EST = ["B01001_003E", "B01001_027E"]
UNDER5_MOE = ["B01001_003M", "B01001_027M"]

def _read_env_file(path: Path) -> dict[str, str]:
    out = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out

def census_key() -> str | None:
    direct = os.getenv("CENSUS_API_KEY")
    if direct:
        return direct.strip()
    env = _read_env_file(Path(r"D:\HELIOS\.env"))
    value = env.get("CENSUS_API_KEY")
    return value.strip() if value else None

def _num(row: dict, key: str) -> float:
    raw = row.get(key)
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if v < -1e8:
        return 0.0
    return max(0.0, v)

def _rss(row: dict, keys: list[str]) -> float:
    return math.sqrt(sum(_num(row, k) ** 2 for k in keys))

def fetch_acs_tracts(key: str | None = None) -> list[dict]:
    key = key or census_key()
    if not key:
        raise RuntimeError("CENSUS_API_KEY is not configured in D:\\HELIOS\\.env")
    params = {
        "get": ",".join(VARIABLES),
        "for": "tract:*",
        "in": f"state:{STATE} county:{COUNTY}",
        "key": key,
    }
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        r = client.get(ACS_BASE, params=params)
        r.raise_for_status()
        data = r.json()
    header = data[0]
    out = []
    for values in data[1:]:
        row = dict(zip(header, values))
        geoid = row["state"] + row["county"] + row["tract"]
        out.append({
            "geoid": geoid,
            "name": row["NAME"],
            "state": row["state"],
            "county": row["county"],
            "tract": row["tract"],
            "population": _num(row, "B01001_001E"),
            "population_moe": _num(row, "B01001_001M"),
            "under5_population": sum(_num(row, k) for k in UNDER5_EST),
            "under5_moe": _rss(row, UNDER5_MOE),
            "age65_population": sum(_num(row, k) for k in AGE65_EST),
            "age65_moe": _rss(row, AGE65_MOE),
            "poverty_universe": _num(row, "B17001_001E"),
            "poverty_population": _num(row, "B17001_002E"),
            "poverty_population_moe": _num(row, "B17001_002M"),
            "households": _num(row, "B08201_001E"),
            "no_vehicle_households": _num(row, "B08201_002E"),
            "no_vehicle_households_moe": _num(row, "B08201_002M"),
        })
    return out

def fetch_tiger_tract_geometries() -> dict[str, object]:
    params = {
        "where": "STATE='04' AND COUNTY='013'",
        "outFields": "GEOID,STATE,COUNTY,TRACT,BASENAME",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        r = client.get(TIGER_TRACTS_QUERY, params=params)
        r.raise_for_status()
        payload = r.json()
    out = {}
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        geoid = props.get("GEOID")
        geom = feature.get("geometry")
        if geoid and geom:
            out[str(geoid)] = shape(geom)
    if not out:
        raise RuntimeError("TIGERweb returned no Maricopa County tract geometries")
    return out

def status() -> dict:
    return {
        "provider": "US Census ACS 5-Year 2024",
        "configured": census_key() is not None,
        "requires_api_key": True,
        "truth_category": "observed",
        "geography": "census tract",
        "state_fips": STATE,
        "county_fips": COUNTY,
    }
