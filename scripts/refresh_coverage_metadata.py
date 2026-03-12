#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.build_data import (
    REGION_LABELS,
    country_for_region,
    load_city_boundary_geometry,
    load_coverage_status_registry,
    make_coverage_feature,
    write_json_atomic,
)

STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY = True
def load_covered_city_records(data_dir: Path) -> list[dict[str, str]]:
    covered_city_map: dict[tuple[str, str, str], dict[str, str]] = {}
    for area_index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        payload = json.loads(area_index_path.read_text(encoding="utf-8"))
        state_id = str(payload.get("region", "")).strip()
        country_id = country_for_region(state_id) if state_id else "us"
        for item in payload.get("items", []):
            city = str(item.get("jurisdiction", "")).strip()
            if city and int(item.get("tree_count", 0) or 0) > 0:
                covered_city_map[(country_id, state_id, city)] = {
                    "country_id": country_id,
                    "state_id": state_id,
                    "jurisdiction": city,
                }
    return sorted(
        covered_city_map.values(),
        key=lambda item: (item["state_id"], item["jurisdiction"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh coverage.v1.geojson and coverage-related meta fields.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing city publish files and meta.v2.json.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    covered_city_records = load_covered_city_records(data_dir)
    covered_city_keys = {
        (record["country_id"], record["state_id"], record["jurisdiction"]) for record in covered_city_records
    }
    official_unavailable_entries = sorted(
        [
            entry
            for entry in load_coverage_status_registry()
            if str(entry.get("status", "")).strip() == "official_unavailable"
            and (
                str(entry.get("country_id", "")).strip(),
                str(entry.get("state_id", "")).strip(),
                str(entry.get("jurisdiction", "")).strip(),
            )
            not in covered_city_keys
        ],
        key=lambda entry: (
            str(entry.get("state_id", "")).strip(),
            str(entry.get("jurisdiction", "")).strip(),
        ),
    )
    official_unavailable_cities = [str(entry.get("jurisdiction", "")).strip() for entry in official_unavailable_entries]

    coverage_features: list[dict[str, Any]] = []
    skipped_coverage_cities: list[str] = []
    for record in covered_city_records:
        city = record["jurisdiction"]
        geometry = load_city_boundary_geometry(
            city,
            state_id=record["state_id"],
            country_id=record["country_id"],
        )
        if not geometry:
            skipped_coverage_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")
        coverage_features.append(
            make_coverage_feature(
                city,
                geometry,
                status="covered",
                note=f"Covered by public tree inventory for {city}; geometry from official jurisdiction boundary.",
                state_id=record["state_id"],
                country_id=record["country_id"],
            )
        )

    skipped_official_unavailable_cities: list[str] = []
    for entry in official_unavailable_entries:
        city = str(entry.get("jurisdiction", "")).strip()
        geometry = load_city_boundary_geometry(
            city,
            state_id=str(entry.get("state_id", "")).strip() or None,
            country_id=str(entry.get("country_id", "")).strip() or None,
        )
        if not geometry:
            skipped_official_unavailable_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")
        coverage_features.append(
            make_coverage_feature(
                city,
                geometry,
                status="official_unavailable",
                note=str(entry.get("note", "")).strip(),
                state_id=str(entry.get("state_id", "")).strip() or None,
                country_id=str(entry.get("country_id", "")).strip() or None,
                area_type=str(entry.get("area_type", "")).strip() or None,
            )
        )

    coverage_geojson = {"type": "FeatureCollection", "features": coverage_features}
    coverage_by_region: dict[str, list[dict[str, Any]]] = {region: [] for region in REGION_LABELS}
    for feature in coverage_features:
        region_id = str(feature["properties"].get("state_id", "")).strip()
        if region_id in coverage_by_region:
            coverage_by_region[region_id].append(feature)

    meta["coverage_rule"] = "official_jurisdiction_boundary_only"
    meta["coverage_skipped_cities"] = skipped_coverage_cities
    meta["coverage_official_unavailable_cities"] = official_unavailable_cities
    meta["coverage_official_unavailable_skipped_cities"] = skipped_official_unavailable_cities
    for region in meta.get("regions", []):
        region_id = str(region.get("id", "")).strip()
        region_features = coverage_by_region.get(region_id, [])
        coverage_file_name = f"coverage.{region_id}.v1.geojson"
        coverage_file_path = data_dir / coverage_file_name
        if region_features:
            write_json_atomic(
                coverage_file_path,
                {"type": "FeatureCollection", "features": region_features},
            )
            region["coverage_path"] = f"/data/{coverage_file_name}"
        else:
            region["coverage_path"] = None
            if coverage_file_path.exists():
                coverage_file_path.unlink()

    write_json_atomic(data_dir / "coverage.v1.geojson", coverage_geojson)
    write_json_atomic(meta_path, meta, pretty=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
