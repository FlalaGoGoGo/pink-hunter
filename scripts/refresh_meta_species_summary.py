#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import (
    REGION_LABELS,
    SPECIES_GROUPS,
    classify_aggregate_advisory_level,
    classify_publish_warning_level,
    summarize_ownership_groups,
    summarize_species_counts,
)


def empty_species_counts() -> dict[str, int]:
    return {species: 0 for species in SPECIES_GROUPS}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh meta.v2.json summary fields from published area shard files.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json and area publish files.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    region_features: dict[str, list[dict]] = defaultdict(list)
    region_cities: dict[str, set[str]] = defaultdict(set)
    area_summaries: list[dict[str, object]] = []

    for area_index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        area_index = json.loads(area_index_path.read_text(encoding="utf-8"))
        region = str(area_index.get("region", "")).strip()
        for item in area_index.get("items", []):
            combined_features: list[dict] = []
            for shard in item.get("shards", []):
                shard_path = data_dir / Path(str(shard["data_path"])).name
                payload = json.loads(shard_path.read_text(encoding="utf-8"))
                combined_features.extend(payload.get("features", []))
            region_features[region].extend(combined_features)
            jurisdiction = str(item.get("jurisdiction", "")).strip()
            if jurisdiction:
                region_cities[region].add(jurisdiction)
                area_summaries.append(
                    {
                        "jurisdiction": jurisdiction,
                        "region": region,
                        "tree_count": len(combined_features),
                        "species_counts": summarize_species_counts(combined_features) if combined_features else empty_species_counts(),
                        "jurisdiction_type": item.get("jurisdiction_type", "city"),
                        "state_province": item.get("state_province", region.upper()),
                    }
                )

    all_features: list[dict] = []
    for region_entry in meta.get("regions", []):
        region_id = str(region_entry.get("id", "")).strip()
        features = region_features.get(region_id, [])
        cities = sorted(region_cities.get(region_id, set()))
        region_entry["available"] = bool(features)
        region_entry["tree_count"] = len(features)
        region_entry["city_count"] = len(cities)
        region_entry["cities"] = cities
        region_entry["species_counts"] = summarize_species_counts(features) if features else empty_species_counts()
        region_entry["ownership_groups"] = summarize_ownership_groups(features) if features else []
        all_features.extend(features)

        if not features and region_id in REGION_LABELS:
            region_entry["species_counts"] = empty_species_counts()
            region_entry["ownership_groups"] = []

        aggregate_raw_bytes = 0
        aggregate_gzip_bytes = 0
        largest_shard_raw_bytes = 0
        largest_shard_gzip_bytes = 0
        largest_shard_area = None
        area_split = region_entry.get("area_split") or {}
        index_path = area_split.get("index_path")
        if index_path:
            area_index_path = data_dir / Path(str(index_path)).name
            if area_index_path.exists():
                area_index = json.loads(area_index_path.read_text(encoding="utf-8"))
                shard_count = 0
                for item in area_index.get("items", []):
                    for shard in item.get("shards", []):
                        shard_path = data_dir / Path(str(shard["data_path"])).name
                        raw_bytes = shard_path.stat().st_size
                        gzip_bytes = len(gzip.compress(shard_path.read_bytes()))
                        aggregate_raw_bytes += raw_bytes
                        aggregate_gzip_bytes += gzip_bytes
                        shard_count += 1
                        if raw_bytes > largest_shard_raw_bytes:
                            largest_shard_raw_bytes = raw_bytes
                            largest_shard_gzip_bytes = gzip_bytes
                            largest_shard_area = item.get("jurisdiction")
                area_split["area_count"] = len(area_index.get("items", []))
                area_split["shard_count"] = shard_count
                region_entry["area_split"] = area_split
        region_entry["raw_bytes"] = aggregate_raw_bytes
        region_entry["gzip_bytes"] = aggregate_gzip_bytes
        region_entry["warning_level"] = classify_publish_warning_level(largest_shard_raw_bytes)
        region_entry["aggregate_raw_bytes"] = aggregate_raw_bytes
        region_entry["aggregate_gzip_bytes"] = aggregate_gzip_bytes
        region_entry["aggregate_warning_level"] = classify_aggregate_advisory_level(aggregate_raw_bytes)
        region_entry["largest_shard_raw_bytes"] = largest_shard_raw_bytes
        region_entry["largest_shard_gzip_bytes"] = largest_shard_gzip_bytes
        region_entry["largest_shard_area"] = largest_shard_area
        region_entry["largest_shard_warning_level"] = classify_publish_warning_level(largest_shard_raw_bytes)

    meta["included_records"] = len(all_features)
    meta["species_counts"] = summarize_species_counts(all_features) if all_features else empty_species_counts()
    meta["areas"] = sorted(area_summaries, key=lambda item: (str(item["region"]), str(item["jurisdiction"])))

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
