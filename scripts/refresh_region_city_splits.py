#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

WARNING_BYTES = 35 * 1024 * 1024
HIGH_WARNING_BYTES = 45 * 1024 * 1024
HARD_FAIL_BYTES = 50 * 1024 * 1024


def slugify_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def classify_warning_level(raw_bytes: int) -> str:
    if raw_bytes >= HARD_FAIL_BYTES:
        return "hard_fail"
    if raw_bytes >= HIGH_WARNING_BYTES:
        return "high_warning"
    if raw_bytes >= WARNING_BYTES:
        return "warning"
    return "none"


def load_city_feature_map_from_region_file(region_data_path: Path) -> dict[str, list[dict[str, Any]]]:
    region_geojson = json.loads(region_data_path.read_text(encoding="utf-8"))
    city_features: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in region_geojson.get("features", []):
        city = str(feature.get("properties", {}).get("city", "")).strip()
        if city:
            city_features[city].append(feature)
    return city_features


def load_city_feature_map_from_existing_city_files(data_dir: Path, region_id: str) -> dict[str, list[dict[str, Any]]]:
    city_features: dict[str, list[dict[str, Any]]] = {}
    for city_file_path in sorted(data_dir.glob(f"trees.{region_id}.city.*.v1.geojson")):
        payload = json.loads(city_file_path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        if not features:
            continue
        city = str(features[0].get("properties", {}).get("city", "")).strip()
        if city:
            city_features[city] = features
    return city_features


def write_region_city_split(data_dir: Path, region_entry: dict[str, Any], generated_at: str) -> None:
    region_id = str(region_entry["id"])
    region_data_path = None
    if region_entry.get("data_path"):
        region_data_path = data_dir / Path(str(region_entry["data_path"])).name

    if region_data_path and region_data_path.exists():
        city_features = load_city_feature_map_from_region_file(region_data_path)
    else:
        city_features = load_city_feature_map_from_existing_city_files(data_dir, region_id)
        if not city_features:
            raise FileNotFoundError(
                f"No region source file or existing city files available for region '{region_id}'."
            )

    for stale_path in data_dir.glob(f"trees.{region_id}.city.*.v1.geojson"):
        stale_path.unlink()

    city_entries = []
    combined_features: list[dict[str, Any]] = []
    for city in sorted(city_features):
        features = city_features[city]
        combined_features.extend(features)
        file_name = f"trees.{region_id}.city.{slugify_token(city)}.v1.geojson"
        payload = {"type": "FeatureCollection", "features": features}
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        file_path = data_dir / file_name
        file_path.write_bytes(payload_bytes)
        city_entries.append(
            {
                "city": city,
                "data_path": f"/data/{file_name}",
                "tree_count": len(features),
                "raw_bytes": len(payload_bytes),
                "gzip_bytes": len(gzip.compress(payload_bytes)),
            }
        )

    city_index_name = f"trees.{region_id}.city-index.v1.json"
    city_index_path = data_dir / city_index_name
    city_index_payload = {
        "generated_at": generated_at,
        "region": region_id,
        "strategy": "city",
        "items": city_entries,
    }
    city_index_path.write_text(json.dumps(city_index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    combined_payload_bytes = json.dumps(
        {"type": "FeatureCollection", "features": combined_features},
        ensure_ascii=False,
    ).encode("utf-8")
    region_entry["data_path"] = None
    region_entry["tree_count"] = len(combined_features)
    region_entry["city_count"] = len(city_entries)
    region_entry["cities"] = sorted(city_features)
    region_entry["raw_bytes"] = len(combined_payload_bytes)
    region_entry["gzip_bytes"] = len(gzip.compress(combined_payload_bytes))
    region_entry["warning_level"] = classify_warning_level(region_entry["raw_bytes"])
    region_entry["city_split"] = {
        "strategy": "city",
        "index_path": f"/data/{city_index_name}",
        "file_count": len(city_entries),
        "ready": True,
    }

    if region_data_path and region_data_path.exists():
        region_data_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate city-split publish artifacts for one or more regions.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json.")
    parser.add_argument("--region", default="all", help="Region id to split, e.g. wa, or 'all'.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    target_region = None if args.region == "all" else args.region
    for region_entry in meta.get("regions", []):
        if target_region and region_entry.get("id") != target_region:
            continue
        write_region_city_split(data_dir, region_entry, meta.get("generated_at"))

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
