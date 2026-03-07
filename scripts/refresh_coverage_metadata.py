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

from etl.build_data import (
    OFFICIAL_DATA_UNAVAILABLE_CITIES,
    STRICT_CITY_BOUNDARY_ONLY,
    WA_METRO_OVERVIEW_BOUNDS,
    build_region_bounds,
    load_city_boundary_geometry,
)


def make_coverage_feature(city: str, geometry: dict[str, Any], status: str, note: str) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": f"{status.replace('_', '-')}-{city.lower().replace(' ', '-')}",
            "status": status,
            "jurisdiction": city,
            "note": note,
        },
    }


def load_covered_cities(data_dir: Path) -> list[str]:
    covered_cities: set[str] = set()
    for city_file_path in sorted(data_dir.glob("trees.*.city.*.v1.geojson")):
        payload = json.loads(city_file_path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        if not features:
            continue
        city = str(features[0].get("properties", {}).get("city", "")).strip()
        if city:
            covered_cities.add(city)
    return sorted(covered_cities)


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh coverage.v1.geojson and coverage-related meta fields.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing city publish files and meta.v2.json.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    covered_cities = load_covered_cities(data_dir)
    covered_city_set = set(covered_cities)
    official_unavailable_cities = sorted(
        city for city in OFFICIAL_DATA_UNAVAILABLE_CITIES if city not in covered_city_set
    )

    coverage_features: list[dict[str, Any]] = []
    skipped_coverage_cities: list[str] = []
    for city in covered_cities:
        geometry = load_city_boundary_geometry(city)
        if not geometry:
            skipped_coverage_cities.append(city)
            if STRICT_CITY_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official city boundary geometry for: {city}")
        coverage_features.append(
            make_coverage_feature(
                city,
                geometry,
                "covered",
                f"Covered by public tree inventory for {city}; geometry from official city boundary."
            )
        )

    skipped_official_unavailable_cities: list[str] = []
    for city in official_unavailable_cities:
        geometry = load_city_boundary_geometry(city)
        if not geometry:
            skipped_official_unavailable_cities.append(city)
            if STRICT_CITY_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official city boundary geometry for: {city}")
        coverage_features.append(
            make_coverage_feature(city, geometry, "official_unavailable", OFFICIAL_DATA_UNAVAILABLE_CITIES[city])
        )

    coverage_geojson = {"type": "FeatureCollection", "features": coverage_features}
    region_bounds = build_region_bounds(coverage_features)

    meta["coverage_rule"] = "official_city_boundary_only"
    meta["coverage_skipped_cities"] = skipped_coverage_cities
    meta["coverage_official_unavailable_cities"] = official_unavailable_cities
    meta["coverage_official_unavailable_skipped_cities"] = skipped_official_unavailable_cities

    for region_entry in meta.get("regions", []):
        region_id = region_entry.get("id")
        region_entry["bounds"] = region_bounds.get(region_id, WA_METRO_OVERVIEW_BOUNDS)

    (data_dir / "coverage.v1.geojson").write_text(
        json.dumps(coverage_geojson, ensure_ascii=False),
        encoding="utf-8",
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
