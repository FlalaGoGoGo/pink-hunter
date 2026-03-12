#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import requests
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import (  # noqa: E402
    CITY_BOUNDARY_HINTS,
    REGION_CITY_OVERRIDES,
    REGION_LABELS,
    bounds_for_geometry,
    load_boundary_catalog,
    slugify_token,
)

DATA_DIR = ROOT / "public" / "data"
REFERENCE_DIR = ROOT / "data" / "reference"
US_JUMP_CACHE_PATH = REFERENCE_DIR / "jump_us_areas.v1.json"

US_STATE_LAYER_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0/query"
US_PLACE_LAYER_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/18/query"
US_COUNTY_LAYER_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/55/query"

REGION_COUNTRY: dict[str, str] = {
    "az": "us",
    "ct": "us",
    "ga": "us",
    "il": "us",
    "mi": "us",
    "wa": "us",
    "ca": "us",
    "co": "us",
    "nv": "us",
    "or": "us",
    "tx": "us",
    "ut": "us",
    "dc": "us",
    "va": "us",
    "md": "us",
    "nj": "us",
    "ny": "us",
    "pa": "us",
    "ma": "us",
    "bc": "ca",
    "on": "ca",
    "qc": "ca",
}

REGION_FULL_NAMES: dict[str, str] = {
    "az": "Arizona",
    "ct": "Connecticut",
    "ga": "Georgia",
    "il": "Illinois",
    "mi": "Michigan",
    "wa": "Washington",
    "ca": "California",
    "co": "Colorado",
    "nv": "Nevada",
    "or": "Oregon",
    "tx": "Texas",
    "ut": "Utah",
    "dc": "Washington, DC",
    "va": "Virginia",
    "md": "Maryland",
    "nj": "New Jersey",
    "ny": "New York",
    "pa": "Pennsylvania",
    "ma": "Massachusetts",
    "bc": "British Columbia",
    "on": "Ontario",
    "qc": "Quebec",
}

US_STATE_META_BY_FIPS: dict[str, dict[str, str]] = {
    "01": {"code": "al", "label": "Alabama"},
    "02": {"code": "ak", "label": "Alaska"},
    "04": {"code": "az", "label": "Arizona"},
    "05": {"code": "ar", "label": "Arkansas"},
    "06": {"code": "ca", "label": "California"},
    "08": {"code": "co", "label": "Colorado"},
    "09": {"code": "ct", "label": "Connecticut"},
    "10": {"code": "de", "label": "Delaware"},
    "11": {"code": "dc", "label": "District of Columbia"},
    "12": {"code": "fl", "label": "Florida"},
    "13": {"code": "ga", "label": "Georgia"},
    "15": {"code": "hi", "label": "Hawaii"},
    "16": {"code": "id", "label": "Idaho"},
    "17": {"code": "il", "label": "Illinois"},
    "18": {"code": "in", "label": "Indiana"},
    "19": {"code": "ia", "label": "Iowa"},
    "20": {"code": "ks", "label": "Kansas"},
    "21": {"code": "ky", "label": "Kentucky"},
    "22": {"code": "la", "label": "Louisiana"},
    "23": {"code": "me", "label": "Maine"},
    "24": {"code": "md", "label": "Maryland"},
    "25": {"code": "ma", "label": "Massachusetts"},
    "26": {"code": "mi", "label": "Michigan"},
    "27": {"code": "mn", "label": "Minnesota"},
    "28": {"code": "ms", "label": "Mississippi"},
    "29": {"code": "mo", "label": "Missouri"},
    "30": {"code": "mt", "label": "Montana"},
    "31": {"code": "ne", "label": "Nebraska"},
    "32": {"code": "nv", "label": "Nevada"},
    "33": {"code": "nh", "label": "New Hampshire"},
    "34": {"code": "nj", "label": "New Jersey"},
    "35": {"code": "nm", "label": "New Mexico"},
    "36": {"code": "ny", "label": "New York"},
    "37": {"code": "nc", "label": "North Carolina"},
    "38": {"code": "nd", "label": "North Dakota"},
    "39": {"code": "oh", "label": "Ohio"},
    "40": {"code": "ok", "label": "Oklahoma"},
    "41": {"code": "or", "label": "Oregon"},
    "42": {"code": "pa", "label": "Pennsylvania"},
    "44": {"code": "ri", "label": "Rhode Island"},
    "45": {"code": "sc", "label": "South Carolina"},
    "46": {"code": "sd", "label": "South Dakota"},
    "47": {"code": "tn", "label": "Tennessee"},
    "48": {"code": "tx", "label": "Texas"},
    "49": {"code": "ut", "label": "Utah"},
    "50": {"code": "vt", "label": "Vermont"},
    "51": {"code": "va", "label": "Virginia"},
    "53": {"code": "wa", "label": "Washington"},
    "54": {"code": "wv", "label": "West Virginia"},
    "55": {"code": "wi", "label": "Wisconsin"},
    "56": {"code": "wy", "label": "Wyoming"},
}

CANADA_PROVINCE_META: dict[str, dict[str, Any]] = {
    "ab": {"label": "Alberta", "bounds": [[-120.0, 48.9], [-109.0, 60.0]]},
    "bc": {"label": "British Columbia", "bounds": [[-139.1, 48.2], [-114.0, 60.1]]},
    "mb": {"label": "Manitoba", "bounds": [[-102.1, 48.9], [-88.9, 60.0]]},
    "nb": {"label": "New Brunswick", "bounds": [[-69.2, 44.5], [-63.7, 48.1]]},
    "nl": {"label": "Newfoundland and Labrador", "bounds": [[-67.9, 46.5], [-52.5, 60.4]]},
    "ns": {"label": "Nova Scotia", "bounds": [[-66.5, 43.3], [-59.7, 47.1]]},
    "nt": {"label": "Northwest Territories", "bounds": [[-136.7, 59.9], [-102.0, 78.0]]},
    "nu": {"label": "Nunavut", "bounds": [[-109.0, 60.0], [-61.0, 83.2]]},
    "on": {"label": "Ontario", "bounds": [[-95.2, 41.7], [-74.3, 56.9]]},
    "pe": {"label": "Prince Edward Island", "bounds": [[-64.5, 45.9], [-61.9, 47.1]]},
    "qc": {"label": "Quebec", "bounds": [[-79.8, 44.9], [-57.1, 62.6]]},
    "sk": {"label": "Saskatchewan", "bounds": [[-110.1, 49.0], [-101.4, 60.0]]},
    "yt": {"label": "Yukon", "bounds": [[-141.1, 59.9], [-123.8, 69.7]]},
}

COUNTRY_META = {
    "us": {"label": "United States", "emoji": "🇺🇸"},
    "ca": {"label": "Canada", "emoji": "🇨🇦"},
}

STATE_FIPS_TO_REGION = {
    "53": "wa",
    "06": "ca",
    "08": "co",
    "32": "nv",
    "41": "or",
    "48": "tx",
    "49": "ut",
    "11": "dc",
    "51": "va",
    "24": "md",
    "34": "nj",
    "36": "ny",
    "42": "pa",
    "25": "ma",
}

COVERED_REGION_BY_STATE_CODE = {
    "wa": "wa",
    "ca": "ca",
    "co": "co",
    "nv": "nv",
    "or": "or",
    "tx": "tx",
    "ut": "ut",
    "dc": "dc",
    "va": "va",
    "md": "md",
    "nj": "nj",
    "ny": "ny",
    "pa": "pa",
    "ma": "ma",
    "bc": "bc",
    "on": "on",
    "qc": "qc",
}

DISPLAY_NAME_OVERRIDES = {
    "Arlington": "Arlington County",
    "Richmond BC": "Richmond",
    "Vancouver WA": "Vancouver",
}

JURISDICTION_TYPE_OVERRIDES = {
    "Arlington": "county",
    "Montgomery County": "county",
    "Washington DC": "district",
    "North Vancouver District": "district",
}


def titleize_slug(slug: str) -> str:
    special = {
        "new_york_city": "New York City",
        "washington_dc": "Washington DC",
        "richmond_bc": "Richmond BC",
        "vancouver_bc": "Vancouver BC",
        "vancouver_wa": "Vancouver WA",
        "langley_city": "Langley City",
        "west_vancouver": "West Vancouver",
        "white_rock": "White Rock",
        "san_diego": "San Diego",
        "san_francisco": "San Francisco",
        "san_jose": "San Jose",
        "san_mateo": "San Mateo",
        "san_rafael": "San Rafael",
        "south_san_francisco": "South San Francisco",
        "santa_ana": "Santa Ana",
        "santa_clara": "Santa Clara",
        "santa_cruz": "Santa Cruz",
        "santa_rosa": "Santa Rosa",
        "north_vancouver_city": "North Vancouver City",
        "north_vancouver_district": "North Vancouver District",
        "beaux_arts_village": "Beaux Arts Village",
        "lake_forest_park": "Lake Forest Park",
        "mountlake_terrace": "Mountlake Terrace",
        "new_westminster": "New Westminster",
        "port_orchard": "Port Orchard",
        "redwood_city": "Redwood City",
        "black_diamond": "Black Diamond",
        "federal_way": "Federal Way",
        "gig_harbor": "Gig Harbor",
        "granite_falls": "Granite Falls",
        "hunts_point": "Hunts Point",
        "lake_stevens": "Lake Stevens",
        "long_beach": "Long Beach",
        "los_angeles": "Los Angeles",
        "maple_valley": "Maple Valley",
        "mercer_island": "Mercer Island",
        "mountain_view": "Mountain View",
        "north_bend": "North Bend",
        "palo_alto": "Palo Alto",
        "sea_tac": "SeaTac",
        "white_rock": "White Rock",
        "yarrow_point": "Yarrow Point",
    }
    if slug in special:
        return special[slug]
    return " ".join(part.capitalize() for part in slug.split("_"))


def infer_region_for_jurisdiction(name: str) -> str | None:
    if name in REGION_CITY_OVERRIDES:
        return REGION_CITY_OVERRIDES[name]
    hint = CITY_BOUNDARY_HINTS.get(name, {})
    state = hint.get("state")
    if state and state in STATE_FIPS_TO_REGION:
        return STATE_FIPS_TO_REGION[state]
    if hint.get("boundary_source") in {
        "vancouver_bc_ods",
        "victoria_bc_arcgis",
        "burnaby_arcgis",
        "coquitlam_arcgis",
        "delta_arcgis",
        "metro_vancouver_admin",
        "richmond_bc_arcgis",
        "saanich_arcgis",
        "surrey_arcgis",
        "ottawa_arcgis",
        "toronto_zip",
        "montreal_arrondissements_geojson",
    }:
        if name in {"Ottawa", "Toronto"}:
            return "on"
        if name == "Montreal":
            return "qc"
        return "bc"
    return None


def infer_jurisdiction_type(name: str) -> str:
    if name in JURISDICTION_TYPE_OVERRIDES:
        return JURISDICTION_TYPE_OVERRIDES[name]
    if name.endswith(" County"):
        return "county"
    return "city"


def normalize_display_name(name: str) -> str:
    return DISPLAY_NAME_OVERRIDES.get(name, name)


def normalize_us_place_name(properties: dict[str, Any]) -> str:
    raw_name = str(properties.get("BASENAME") or properties.get("NAME") or "").strip()
    lowered = raw_name.lower()
    suffixes = (" city", " town", " village", " borough")
    for suffix in suffixes:
        if lowered.endswith(suffix):
            return raw_name[: -len(suffix)].strip()
    return raw_name


def normalize_us_county_name(properties: dict[str, Any]) -> tuple[str, str]:
    basename = str(properties.get("BASENAME") or "").strip()
    raw_name = str(properties.get("NAME") or basename).strip()
    lowered = raw_name.lower()
    if lowered.endswith(" city") and basename:
        return basename, "city"
    if raw_name.endswith("County"):
        return raw_name, "county"
    if raw_name.endswith(" County"):
        return raw_name, "county"
    return raw_name, "county"


def normalize_bounds(bounds: tuple[float, float, float, float] | list[list[float]] | None) -> list[list[float]] | None:
    if bounds is None:
        return None
    if isinstance(bounds, tuple):
        min_x, min_y, max_x, max_y = bounds
        return [[float(min_x), float(min_y)], [float(max_x), float(max_y)]]
    return [[float(bounds[0][0]), float(bounds[0][1])], [float(bounds[1][0]), float(bounds[1][1])]]


def union_bounds(all_bounds: list[list[list[float]]]) -> list[list[float]] | None:
    if not all_bounds:
        return None
    min_x = min(bounds[0][0] for bounds in all_bounds)
    min_y = min(bounds[0][1] for bounds in all_bounds)
    max_x = max(bounds[1][0] for bounds in all_bounds)
    max_y = max(bounds[1][1] for bounds in all_bounds)
    return [[min_x, min_y], [max_x, max_y]]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str, params: dict[str, Any]) -> Any:
    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    return response.json()


def fetch_us_state_extent(state_fips: str) -> list[list[float]] | None:
    payload = fetch_json(
        US_STATE_LAYER_URL,
        {
            "where": f"STATE='{state_fips}'",
            "returnExtentOnly": "true",
            "outSR": "4326",
            "f": "json",
        },
    )
    extent = payload.get("extent")
    if not extent:
        return None
    return normalize_bounds((extent["xmin"], extent["ymin"], extent["xmax"], extent["ymax"]))


def load_boundary_bounds(path: Path) -> list[list[float]] | None:
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features", [])
        if not features:
            return None
        return normalize_bounds(bounds_for_geometry(features[0].get("geometry")))
    if payload.get("type") == "Feature":
        return normalize_bounds(bounds_for_geometry(payload.get("geometry")))
    return None


def load_us_jump_areas() -> list[dict[str, Any]]:
    if US_JUMP_CACHE_PATH.exists():
        try:
            return load_json(US_JUMP_CACHE_PATH)
        except (OSError, json.JSONDecodeError):
            pass
    supported_state_codes = sorted(code for code in STATE_FIPS_TO_REGION if code != "11")
    place_features: list[dict[str, Any]] = []
    county_features: list[dict[str, Any]] = []

    try:
        for state_code in supported_state_codes:
            place_payload = fetch_json(
                US_PLACE_LAYER_URL,
                {
                    "where": f"STATE='{state_code}'",
                    "outFields": "STATE,BASENAME,NAME,LSADC,GEOID",
                    "returnGeometry": "true",
                    "geometryPrecision": "4",
                    "maxAllowableOffset": "0.01",
                    "f": "geojson"
                },
            )
            county_payload = fetch_json(
                US_COUNTY_LAYER_URL,
                {
                    "where": f"STATE='{state_code}'",
                    "outFields": "STATE,BASENAME,NAME,LSADC,GEOID",
                    "returnGeometry": "true",
                    "geometryPrecision": "4",
                    "maxAllowableOffset": "0.01",
                    "f": "geojson"
                },
            )
            place_features.extend(place_payload.get("features", []))
            county_features.extend(county_payload.get("features", []))
    except Exception:
        if US_JUMP_CACHE_PATH.exists():
            return load_json(US_JUMP_CACHE_PATH)
        raise

    areas: list[dict[str, Any]] = []

    for feature in place_features:
        properties = feature.get("properties", {})
        state = str(properties.get("STATE", "")).strip()
        state_meta = US_STATE_META_BY_FIPS.get(state)
        if not state_meta:
            continue
        jurisdiction = normalize_us_place_name(properties)
        bounds = normalize_bounds(bounds_for_geometry(feature.get("geometry")))
        if not jurisdiction or not bounds:
            continue
        areas.append(
            {
                "state_id": state_meta["code"],
                "jurisdiction": jurisdiction,
                "display_name": normalize_display_name(jurisdiction),
                "area_type": "city",
                "bounds": bounds,
                "region_hint": COVERED_REGION_BY_STATE_CODE.get(state_meta["code"]),
                "coverage_status": "untracked",
            }
        )

    for feature in county_features:
        properties = feature.get("properties", {})
        state = str(properties.get("STATE", "")).strip()
        state_meta = US_STATE_META_BY_FIPS.get(state)
        if not state_meta:
            continue
        jurisdiction, area_type = normalize_us_county_name(properties)
        bounds = normalize_bounds(bounds_for_geometry(feature.get("geometry")))
        if not jurisdiction or not bounds:
            continue
        areas.append(
            {
                "state_id": state_meta["code"],
                "jurisdiction": jurisdiction,
                "display_name": normalize_display_name(jurisdiction),
                "area_type": area_type,
                "bounds": bounds,
                "region_hint": COVERED_REGION_BY_STATE_CODE.get(state_meta["code"]),
                "coverage_status": "untracked",
            }
        )

    US_JUMP_CACHE_PATH.write_text(json.dumps(areas, ensure_ascii=False, indent=2), encoding="utf-8")
    return areas


def build_jump_index(data_dir: Path) -> dict[str, Any]:
    meta = load_json(data_dir / "meta.v2.json")
    coverage = load_json(data_dir / "coverage.v1.geojson")
    existing_jump_index_path = data_dir / "jump-index.v1.json"
    existing_jump_index = None
    if existing_jump_index_path.exists():
        try:
            existing_jump_index = load_json(existing_jump_index_path)
        except (OSError, json.JSONDecodeError):
            existing_jump_index = None
    region_meta_by_id = {
        str(entry.get("id")): entry for entry in meta.get("regions", [])
    }
    existing_state_bounds_by_id = {}
    if existing_jump_index:
        for state in existing_jump_index.get("states", []):
            state_id = str(state.get("id", "")).strip()
            bounds = state.get("bounds")
            if state_id and bounds:
                existing_state_bounds_by_id[state_id] = bounds

    area_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    coverage_status_map: dict[tuple[str, str, str], str] = {}
    for feature in coverage.get("features", []):
        properties = feature.get("properties", {})
        jurisdiction = str(properties.get("jurisdiction", "")).strip()
        if not jurisdiction:
            continue
        state_id = str(properties.get("state_id", "")).strip()
        country_id = str(properties.get("country_id", "")).strip()
        if not state_id:
            state_id = infer_region_for_jurisdiction(jurisdiction) or ""
        if not country_id and state_id:
            country_id = REGION_COUNTRY.get(state_id, "us")
        if not state_id or not country_id:
            continue
        coverage_status_map[(country_id, state_id, jurisdiction)] = str(properties.get("status", "untracked"))

    for area_index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        area_index = load_json(area_index_path)
        region = str(area_index.get("region", "")).strip()
        for item in area_index.get("items", []):
            jurisdiction = str(item.get("jurisdiction", "")).strip()
            if not jurisdiction:
                continue
            country_id = REGION_COUNTRY[region]
            key = (country_id, region, jurisdiction)
            area_map[key] = {
                "id": f"{region}:{slugify_token(jurisdiction)}",
                "country_id": country_id,
                "state_id": region,
                "jurisdiction": jurisdiction,
                "display_name": normalize_display_name(str(item.get("display_name") or jurisdiction)),
                "area_type": str(item.get("jurisdiction_type") or infer_jurisdiction_type(jurisdiction)),
                "bounds": item.get("bounds"),
                "region_hint": region,
                "coverage_status": "covered",
            }

    for feature in coverage.get("features", []):
        properties = feature.get("properties", {})
        status = str(properties.get("status", "")).strip()
        jurisdiction = str(properties.get("jurisdiction", "")).strip()
        if not jurisdiction or status != "official_unavailable":
            continue
        state_id = str(properties.get("state_id", "")).strip()
        country_id = str(properties.get("country_id", "")).strip()
        if not state_id:
            state_id = infer_region_for_jurisdiction(jurisdiction) or ""
        if not country_id and state_id:
            country_id = REGION_COUNTRY.get(state_id, "us")
        if not state_id or not country_id:
            continue
        key = (country_id, state_id, jurisdiction)
        if key in area_map:
            continue
        area_map[key] = {
            "id": f"{state_id}:{slugify_token(jurisdiction)}",
            "country_id": country_id,
            "state_id": state_id,
            "jurisdiction": jurisdiction,
            "display_name": normalize_display_name(jurisdiction),
            "area_type": str(properties.get("area_type") or infer_jurisdiction_type(jurisdiction)),
            "bounds": normalize_bounds(bounds_for_geometry(feature.get("geometry"))),
            "region_hint": state_id if state_id in REGION_LABELS else None,
            "coverage_status": "official_unavailable",
        }

    for item in load_boundary_catalog():
        country_id = str(item.get("country_id", "")).strip()
        state_id = str(item.get("state_id", "")).strip()
        jurisdiction = str(item.get("jurisdiction", "")).strip()
        if not country_id or not state_id or not jurisdiction:
            continue
        key = (country_id, state_id, jurisdiction)
        if key in area_map:
            continue
        bounds = item.get("bounds")
        if not bounds:
            continue
        area_map[key] = {
            "id": f"{state_id}:{slugify_token(jurisdiction)}",
            "country_id": country_id,
            "state_id": state_id,
            "jurisdiction": jurisdiction,
            "display_name": normalize_display_name(jurisdiction),
            "area_type": str(item.get("area_type") or infer_jurisdiction_type(jurisdiction)),
            "bounds": bounds,
            "region_hint": state_id if state_id in REGION_LABELS else None,
            "coverage_status": coverage_status_map.get((country_id, state_id, jurisdiction), "untracked"),
        }

    for boundary_path in sorted(REFERENCE_DIR.glob("boundary_*.geojson")):
        slug = boundary_path.stem.removeprefix("boundary_")
        jurisdiction = titleize_slug(slug)
        state_id = infer_region_for_jurisdiction(jurisdiction) or ""
        country_id = REGION_COUNTRY.get(state_id, "us") if state_id else ""
        if state_id and country_id and (country_id, state_id, jurisdiction) in area_map:
            continue

        payload = load_json(boundary_path)
        if payload.get("type") == "FeatureCollection":
            features = payload.get("features", [])
            if not features:
                continue
            feature = features[0]
        elif payload.get("type") == "Feature":
            feature = payload
        else:
            continue
        properties = feature.get("properties", {})
        jurisdiction = str(properties.get("jurisdiction", "")).strip() or jurisdiction
        state_id = str(properties.get("state_id", "")).strip() or state_id
        country_id = str(properties.get("country_id", "")).strip() or country_id
        if not state_id:
            state_id = infer_region_for_jurisdiction(jurisdiction) or ""
        if not country_id and state_id:
            country_id = REGION_COUNTRY.get(state_id, "us")
        if not state_id or not country_id:
            continue
        key = (country_id, state_id, jurisdiction)
        if key in area_map:
            continue
        bounds = load_boundary_bounds(boundary_path)
        if not bounds:
            continue
        area_map[key] = {
            "id": f"{state_id}:{slugify_token(jurisdiction)}",
            "country_id": country_id,
            "state_id": state_id,
            "jurisdiction": jurisdiction,
            "display_name": normalize_display_name(jurisdiction),
            "area_type": str(properties.get("area_type") or infer_jurisdiction_type(jurisdiction)),
            "bounds": bounds,
            "region_hint": state_id if state_id in REGION_LABELS else None,
            "coverage_status": coverage_status_map.get((country_id, state_id, jurisdiction), "untracked"),
        }

    existing_display_keys = {
        (str(item["state_id"]), normalize_display_name(str(item["jurisdiction"])))
        for item in area_map.values()
    }

    for item in load_us_jump_areas():
        state_id = str(item["state_id"]).strip()
        jurisdiction = str(item["jurisdiction"]).strip()
        if not state_id or not jurisdiction:
            continue
        region_hint = item.get("region_hint")
        country_id = "us"
        key = (country_id, state_id, jurisdiction)
        display_key = (state_id, normalize_display_name(jurisdiction))
        if key in area_map or display_key in existing_display_keys:
            continue
        area_map[key] = {
            "id": f"{state_id}:{slugify_token(jurisdiction)}",
            "country_id": "us",
            "state_id": state_id,
            "jurisdiction": jurisdiction,
            "display_name": str(item["display_name"]),
            "area_type": str(item["area_type"]),
            "bounds": item["bounds"],
            "region_hint": region_hint,
            "coverage_status": coverage_status_map.get((country_id, state_id, jurisdiction), "untracked"),
        }
        existing_display_keys.add(display_key)

    states: list[dict[str, Any]] = []
    for state_meta in US_STATE_META_BY_FIPS.values():
        state_id = state_meta["code"]
        state_bounds = None
        if state_id in existing_state_bounds_by_id:
            state_bounds = existing_state_bounds_by_id[state_id]
        if not state_bounds:
            state_bounds = union_bounds(
                [
                    item["bounds"]
                    for item in area_map.values()
                    if item.get("country_id") == "us" and item.get("state_id") == state_id and item.get("bounds")
                ]
            )
        if not state_bounds:
            state_fips = next((fips for fips, meta_item in US_STATE_META_BY_FIPS.items() if meta_item["code"] == state_id), None)
            if state_fips:
                try:
                    state_bounds = fetch_us_state_extent(state_fips)
                except requests.RequestException:
                    state_bounds = None
        if not state_bounds:
            continue
        states.append(
            {
                "id": state_id,
                "country_id": "us",
                "code": state_id.upper(),
                "label": state_meta["label"],
                "bounds": state_bounds,
                "region_hint": COVERED_REGION_BY_STATE_CODE.get(state_id),
            }
        )

    for state_id, province_meta in CANADA_PROVINCE_META.items():
        state_bounds = province_meta["bounds"]
        if state_id in region_meta_by_id and region_meta_by_id[state_id].get("bounds"):
            state_bounds = region_meta_by_id[state_id]["bounds"]
        states.append(
            {
                "id": state_id,
                "country_id": "ca",
                "code": state_id.upper(),
                "label": province_meta["label"],
                "bounds": state_bounds,
                "region_hint": COVERED_REGION_BY_STATE_CODE.get(state_id),
            }
        )

    countries: list[dict[str, Any]] = []
    for country_id, country_meta in COUNTRY_META.items():
        country_state_bounds = [state["bounds"] for state in states if state["country_id"] == country_id]
        bounds = union_bounds(country_state_bounds)
        if not bounds:
            continue
        countries.append(
            {
                "id": country_id,
                "label": country_meta["label"],
                "emoji": country_meta["emoji"],
                "bounds": bounds,
            }
        )

    areas = sorted(
        area_map.values(),
        key=lambda item: (str(item["country_id"]), str(item["state_id"]), str(item["display_name"])),
    )
    states.sort(key=lambda item: (str(item["country_id"]), str(item["label"])))
    countries.sort(key=lambda item: str(item["label"]))

    return {
        "generated_at": meta.get("generated_at"),
        "countries": countries,
        "states": states,
        "areas": areas,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate jump-index.v1.json for country/state/area navigation.")
    parser.add_argument("--data-dir", default=str(DATA_DIR), help="Directory containing meta.v2.json and coverage.v1.geojson")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    jump_index = build_jump_index(data_dir)
    output_path = data_dir / "jump-index.v1.json"
    output_path.write_text(json.dumps(jump_index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
