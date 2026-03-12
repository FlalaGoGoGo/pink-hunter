#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.build_data import (  # noqa: E402
    ALLOWED_CENSUS_PLACE_LSADC,
    CITY_BOUNDARY_HINTS,
    US_CENSUS_CITIES_LAYER,
    city_boundary_cache_path,
    country_for_region,
    fetch_json,
    load_boundary_catalog,
    load_city_boundary_feature,
    load_json_file,
    region_for_city,
    standardize_boundary_feature,
    write_boundary_catalog,
    write_boundary_feature_cache,
)

SUPPORTED_US_STATE_FIPS = {
    "az": "04",
    "ca": "06",
    "co": "08",
    "dc": "11",
    "ga": "13",
    "il": "17",
    "ma": "25",
    "md": "24",
    "mi": "26",
    "nj": "34",
    "nv": "32",
    "ny": "36",
    "or": "41",
    "pa": "42",
    "tx": "48",
    "ut": "49",
    "va": "51",
    "wa": "53",
}


def strip_us_place_suffix(raw_name: str) -> str:
    lowered = raw_name.lower().strip()
    for suffix in (" city", " town", " village", " borough"):
        if lowered.endswith(suffix):
            return raw_name[: -len(suffix)].strip()
    return raw_name.strip()


def build_state_alias_map(state_fips: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for city, hint in CITY_BOUNDARY_HINTS.items():
        if str(hint.get("state", "")).strip() != state_fips:
            continue
        basename = str(hint.get("basename", city)).strip()
        aliases[basename] = city
        aliases[strip_us_place_suffix(basename)] = city
    return aliases


def canonicalize_city_name(raw_name: str, state_fips: str) -> str:
    aliases = build_state_alias_map(state_fips)
    stripped = strip_us_place_suffix(raw_name)
    return aliases.get(raw_name, aliases.get(stripped, raw_name))


def clear_state_boundaries(country_id: str, state_id: str) -> None:
    boundary_dir = PROJECT_ROOT / "data" / "reference" / "boundaries" / country_id / state_id
    if boundary_dir.exists():
        for path in boundary_dir.glob("*.geojson"):
            path.unlink()
    kept_entries = [
        item
        for item in load_boundary_catalog()
        if not (
            str(item.get("country_id", "")).strip() == country_id
            and str(item.get("state_id", "")).strip() == state_id
        )
    ]
    write_boundary_catalog(kept_entries)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prebuild official city/place boundaries for a supported US state.")
    parser.add_argument("--country", default="us", help="Country identifier. v1 supports only 'us'.")
    parser.add_argument("--state", required=True, help="State/region id such as 'ca' or 'wa'.")
    parser.add_argument(
        "--refresh-existing",
        action="store_true",
        help="Refetch and overwrite existing canonical boundary files.",
    )
    args = parser.parse_args()

    country_id = args.country.strip().lower()
    state_id = args.state.strip().lower()
    if country_id != "us":
        raise SystemExit("Only --country us is supported in this version.")
    state_fips = SUPPORTED_US_STATE_FIPS.get(state_id)
    if not state_fips:
        raise SystemExit(f"Unsupported state for boundary prebuild: {state_id}")
    allowed_lsadc = ",".join(f"'{value}'" for value in sorted(ALLOWED_CENSUS_PLACE_LSADC))

    if args.refresh_existing:
        clear_state_boundaries(country_id, state_id)

    payload = fetch_json(
        f"{US_CENSUS_CITIES_LAYER}/query",
        {
            "where": f"STATE = '{state_fips}' AND LSADC IN ({allowed_lsadc})",
            "outFields": "BASENAME,NAME,STATE,GEOID,LSADC",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    features = payload.get("features", [])
    if not features:
        raise SystemExit(f"No place boundaries returned for state {state_id}.")

    created = 0
    reused = 0
    special_overrides = 0
    for feature in features:
        properties = feature.get("properties", {})
        raw_basename = str(properties.get("BASENAME") or "").strip()
        raw_name = raw_basename or strip_us_place_suffix(str(properties.get("NAME") or "").strip())
        if not raw_name:
            continue
        city = canonicalize_city_name(raw_name, state_fips)
        boundary_path = city_boundary_cache_path(city, state_id=state_id, country_id=country_id)
        if boundary_path.exists() and not args.refresh_existing:
            cached_feature = load_city_boundary_feature(city, state_id=state_id, country_id=country_id)
            if cached_feature:
                reused += 1
                continue
        standardized = standardize_boundary_feature(
            city,
            feature,
            state_id=state_id,
            country_id=country_id,
        )
        write_boundary_feature_cache(standardized, boundary_path)
        created += 1

    for city, hint in sorted(CITY_BOUNDARY_HINTS.items()):
        if str(hint.get("state", "")).strip() != state_fips:
            continue
        if not str(hint.get("boundary_source", "")).strip():
            continue
        if country_for_region(region_for_city(city)) != country_id:
            continue
        feature = load_city_boundary_feature(
            city,
            state_id=state_id,
            country_id=country_id,
            refresh=True,
        )
        if feature:
            special_overrides += 1

    catalog_path = PROJECT_ROOT / "data" / "reference" / "boundary_catalog.v1.json"
    item_count = 0
    if catalog_path.exists():
        payload = load_json_file(catalog_path)
        items = payload.get("items")
        if isinstance(items, list):
            item_count = len(items)

    print(
        f"Prebuilt boundaries for {state_id}: created_or_updated={created}, reused={reused}, "
        f"special_overrides={special_overrides}, catalog_items={item_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
