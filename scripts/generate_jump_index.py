#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    slugify_token,
)

DATA_DIR = ROOT / "public" / "data"
REFERENCE_DIR = ROOT / "data" / "reference"

REGION_COUNTRY: dict[str, str] = {
    "wa": "us",
    "ca": "us",
    "or": "us",
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
    "wa": "Washington",
    "ca": "California",
    "or": "Oregon",
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

COUNTRY_META = {
    "us": {"label": "United States", "emoji": "🇺🇸"},
    "ca": {"label": "Canada", "emoji": "🇨🇦"},
}

STATE_FIPS_TO_REGION = {
    "53": "wa",
    "06": "ca",
    "41": "or",
    "11": "dc",
    "51": "va",
    "24": "md",
    "34": "nj",
    "36": "ny",
    "42": "pa",
    "25": "ma",
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


def load_boundary_bounds(path: Path) -> list[list[float]] | None:
    payload = load_json(path)
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features", [])
        if not features:
            return None
        return normalize_bounds(bounds_for_geometry(features[0].get("geometry")))
    if payload.get("type") == "Feature":
        return normalize_bounds(bounds_for_geometry(payload.get("geometry")))
    return None


def build_jump_index(data_dir: Path) -> dict[str, Any]:
    meta = load_json(data_dir / "meta.v2.json")
    coverage = load_json(data_dir / "coverage.v1.geojson")

    area_map: dict[tuple[str, str], dict[str, Any]] = {}
    coverage_status_map: dict[str, str] = {
        str(feature.get("properties", {}).get("jurisdiction", "")).strip(): str(
            feature.get("properties", {}).get("status", "untracked")
        )
        for feature in coverage.get("features", [])
    }

    for area_index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        area_index = load_json(area_index_path)
        region = str(area_index.get("region", "")).strip()
        for item in area_index.get("items", []):
            jurisdiction = str(item.get("jurisdiction", "")).strip()
            if not jurisdiction:
                continue
            key = (region, jurisdiction)
            area_map[key] = {
                "id": f"{region}:{slugify_token(jurisdiction)}",
                "country_id": REGION_COUNTRY[region],
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
        region = infer_region_for_jurisdiction(jurisdiction)
        if not region:
            continue
        key = (region, jurisdiction)
        if key in area_map:
            continue
        area_map[key] = {
            "id": f"{region}:{slugify_token(jurisdiction)}",
            "country_id": REGION_COUNTRY[region],
            "state_id": region,
            "jurisdiction": jurisdiction,
            "display_name": normalize_display_name(jurisdiction),
            "area_type": infer_jurisdiction_type(jurisdiction),
            "bounds": normalize_bounds(bounds_for_geometry(feature.get("geometry"))),
            "region_hint": region,
            "coverage_status": "official_unavailable",
        }

    for boundary_path in sorted(REFERENCE_DIR.glob("boundary_*.geojson")):
        slug = boundary_path.stem.removeprefix("boundary_")
        jurisdiction = titleize_slug(slug)
        region = infer_region_for_jurisdiction(jurisdiction)
        if not region:
            continue
        key = (region, jurisdiction)
        if key in area_map:
            continue
        bounds = load_boundary_bounds(boundary_path)
        if not bounds:
            continue
        area_map[key] = {
            "id": f"{region}:{slugify_token(jurisdiction)}",
            "country_id": REGION_COUNTRY[region],
            "state_id": region,
            "jurisdiction": jurisdiction,
            "display_name": normalize_display_name(jurisdiction),
            "area_type": infer_jurisdiction_type(jurisdiction),
            "bounds": bounds,
            "region_hint": region,
            "coverage_status": coverage_status_map.get(jurisdiction, "untracked"),
        }

    states: list[dict[str, Any]] = []
    for region in REGION_LABELS:
        state_bounds = union_bounds([item["bounds"] for (item_region, _), item in area_map.items() if item_region == region and item.get("bounds")])
        if not state_bounds:
            region_meta = next((entry for entry in meta.get("regions", []) if entry.get("id") == region), None)
            state_bounds = region_meta.get("bounds") if region_meta else None
        if not state_bounds:
            continue
        states.append(
            {
                "id": region,
                "country_id": REGION_COUNTRY[region],
                "code": region.upper(),
                "label": REGION_FULL_NAMES[region],
                "bounds": state_bounds,
                "region_hint": region,
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
