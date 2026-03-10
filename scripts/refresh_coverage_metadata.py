#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.build_data import OFFICIAL_DATA_UNAVAILABLE_CITIES, REGION_LABELS, region_for_city

STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY = True
SPECIAL_BOUNDARY_SLUGS = {
    "Richmond BC": "richmond_bc",
    "Vancouver WA": "vancouver",
}


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


def slugify_city(city: str) -> str:
    if city in SPECIAL_BOUNDARY_SLUGS:
        return SPECIAL_BOUNDARY_SLUGS[city]
    return re.sub(r"[^a-z0-9]+", "_", city.lower()).strip("_")


def load_city_boundary_geometry(reference_dir: Path, city: str) -> dict[str, Any] | None:
    boundary_path = reference_dir / f"boundary_{slugify_city(city)}.geojson"
    if not boundary_path.exists():
        return None
    payload = json.loads(boundary_path.read_text(encoding="utf-8"))
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features") or []
        if not features:
            return None
        return (features[0] or {}).get("geometry")
    if payload.get("type") == "Feature":
        return payload.get("geometry")
    return payload.get("geometry")


def load_covered_cities(data_dir: Path) -> list[str]:
    covered_cities: set[str] = set()
    for area_index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        payload = json.loads(area_index_path.read_text(encoding="utf-8"))
        for item in payload.get("items", []):
            city = str(item.get("jurisdiction", "")).strip()
            if city and int(item.get("tree_count", 0) or 0) > 0:
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
    reference_dir = PROJECT_ROOT / "data" / "reference"
    covered_cities = load_covered_cities(data_dir)
    covered_city_set = set(covered_cities)
    configured_official_unavailable = set(meta.get("coverage_official_unavailable_cities", []))
    configured_official_unavailable.update(OFFICIAL_DATA_UNAVAILABLE_CITIES.keys())
    official_unavailable_cities = sorted(
        city for city in configured_official_unavailable if city not in covered_city_set
    )

    coverage_features: list[dict[str, Any]] = []
    skipped_coverage_cities: list[str] = []
    for city in covered_cities:
        geometry = load_city_boundary_geometry(reference_dir, city)
        if not geometry:
            skipped_coverage_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")
        coverage_features.append(
            make_coverage_feature(
                city,
                geometry,
                "covered",
                f"Covered by public tree inventory for {city}; geometry from official jurisdiction boundary."
            )
        )

    skipped_official_unavailable_cities: list[str] = []
    for city in official_unavailable_cities:
        geometry = load_city_boundary_geometry(reference_dir, city)
        if not geometry:
            skipped_official_unavailable_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")
        existing_note = OFFICIAL_DATA_UNAVAILABLE_CITIES.get(city, "")
        if not existing_note:
            for feature in meta.get("coverage_notes", []):
                if feature.get("jurisdiction") == city:
                    existing_note = str(feature.get("note", ""))
                    break
        coverage_features.append(make_coverage_feature(city, geometry, "official_unavailable", existing_note))

    coverage_geojson = {"type": "FeatureCollection", "features": coverage_features}
    coverage_by_region: dict[str, list[dict[str, Any]]] = {region: [] for region in REGION_LABELS}
    for feature in coverage_features:
        region_id = region_for_city(str(feature["properties"]["jurisdiction"]))
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
            coverage_file_path.write_text(
                json.dumps({"type": "FeatureCollection", "features": region_features}, ensure_ascii=False),
                encoding="utf-8",
            )
            region["coverage_path"] = f"/data/{coverage_file_name}"
        else:
            region["coverage_path"] = None
            if coverage_file_path.exists():
                coverage_file_path.unlink()

    (data_dir / "coverage.v1.geojson").write_text(
        json.dumps(coverage_geojson, ensure_ascii=False),
        encoding="utf-8",
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
