#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def slugify_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def refresh_region_city_split(data_dir: Path, region_id: str) -> None:
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    region_entry = next((item for item in meta.get("regions", []) if item.get("id") == region_id), None)
    if not region_entry:
        raise KeyError(f"Region '{region_id}' not found in {meta_path}")

    region_file_name = Path(region_entry["data_path"]).name
    region_data_path = data_dir / region_file_name
    if not region_data_path.exists():
        raise FileNotFoundError(f"Missing region data file: {region_data_path}")

    region_geojson = json.loads(region_data_path.read_text(encoding="utf-8"))
    city_features: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in region_geojson.get("features", []):
        city = str(feature.get("properties", {}).get("city", "")).strip()
        if not city:
            continue
        city_features[city].append(feature)

    stale_pattern = f"trees.{region_id}.city.*.v1.geojson"
    for stale_path in data_dir.glob(stale_pattern):
        stale_path.unlink()

    city_entries = []
    for city in sorted(city_features):
        file_name = f"trees.{region_id}.city.{slugify_token(city)}.v1.geojson"
        payload = {
            "type": "FeatureCollection",
            "features": city_features[city],
        }
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        file_path = data_dir / file_name
        file_path.write_bytes(payload_bytes)
        city_entries.append(
            {
                "city": city,
                "data_path": f"/data/{file_name}",
                "tree_count": len(city_features[city]),
                "raw_bytes": len(payload_bytes),
                "gzip_bytes": len(gzip.compress(payload_bytes)),
            }
        )

    city_index_name = f"trees.{region_id}.city-index.v1.json"
    city_index_path = data_dir / city_index_name
    city_index_payload = {
        "generated_at": meta.get("generated_at"),
        "region": region_id,
        "strategy": "city",
        "items": city_entries,
    }
    city_index_path.write_text(json.dumps(city_index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    region_entry["city_split"] = {
        "strategy": "city",
        "index_path": f"/data/{city_index_name}",
        "file_count": len(city_entries),
        "ready": True,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate city-split publish artifacts for a region.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json and region files.")
    parser.add_argument("--region", default="wa", help="Region id to split by city, e.g. wa.")
    args = parser.parse_args()

    refresh_region_city_split(Path(args.data_dir), args.region)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
