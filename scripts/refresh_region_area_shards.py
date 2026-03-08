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

from etl.build_data import (  # noqa: E402
    REGION_LABELS,
    bounds_from_features,
    classify_aggregate_advisory_level,
    classify_publish_warning_level,
    encode_feature_collection,
    slugify_token,
    split_features_for_publish,
    summarize_ownership_groups,
    summarize_species_counts,
    summarize_zip_codes,
)


def load_area_feature_map(data_dir: Path, region_id: str) -> dict[str, list[dict]]:
    area_features: dict[str, list[dict]] = defaultdict(list)
    jurisdictions_from_city_files: set[str] = set()

    for path in sorted(data_dir.glob(f"trees.{region_id}.city.*.v1.geojson")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        if not features:
            continue
        jurisdiction = str(features[0].get("properties", {}).get("city", "")).strip()
        if jurisdiction:
            jurisdictions_from_city_files.add(jurisdiction)
            area_features[jurisdiction].extend(features)

    for path in sorted(data_dir.glob(f"trees.{region_id}.area.*.v2.geojson")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        if not features:
            continue
        jurisdiction = str(features[0].get("properties", {}).get("city", "")).strip()
        if not jurisdiction or jurisdiction in jurisdictions_from_city_files:
            continue
        area_features[jurisdiction].extend(features)

    return dict(area_features)


def write_region_area_shards(data_dir: Path, region_entry: dict[str, object], generated_at: str) -> None:
    region_id = str(region_entry["id"])
    area_feature_map = load_area_feature_map(data_dir, region_id)

    for stale_path in data_dir.glob(f"trees.{region_id}.area.*.v2.geojson"):
        stale_path.unlink()
    for stale_path in data_dir.glob(f"trees.{region_id}.city.*.v1.geojson"):
        stale_path.unlink()
    legacy_city_index_path = data_dir / f"trees.{region_id}.city-index.v1.json"
    if legacy_city_index_path.exists():
        legacy_city_index_path.unlink()

    aggregate_raw_bytes = 0
    aggregate_gzip_bytes = 0
    largest_shard_raw_bytes = 0
    largest_shard_gzip_bytes = 0
    largest_shard_area: str | None = None
    area_entries: list[dict[str, object]] = []
    shard_count = 0

    for jurisdiction in sorted(area_feature_map):
        features = area_feature_map[jurisdiction]
        area_slug = slugify_token(jurisdiction)
        shard_feature_sets = split_features_for_publish(features)
        shard_entries: list[dict[str, object]] = []
        for shard_index, shard_features in enumerate(shard_feature_sets, start=1):
            if len(shard_feature_sets) == 1:
                file_name = f"trees.{region_id}.area.{area_slug}.v2.geojson"
            else:
                file_name = f"trees.{region_id}.area.{area_slug}.shard-{shard_index:03d}.v2.geojson"
            payload_bytes = encode_feature_collection(shard_features)
            raw_bytes = len(payload_bytes)
            gzip_bytes = len(gzip.compress(payload_bytes))
            (data_dir / file_name).write_bytes(payload_bytes)
            shard_entries.append(
                {
                    "id": f"{area_slug}-{shard_index:03d}",
                    "bounds": bounds_from_features(shard_features),
                    "data_path": f"/data/{file_name}",
                    "tree_count": len(shard_features),
                    "raw_bytes": raw_bytes,
                    "gzip_bytes": gzip_bytes,
                }
            )
            aggregate_raw_bytes += raw_bytes
            aggregate_gzip_bytes += gzip_bytes
            shard_count += 1
            if raw_bytes > largest_shard_raw_bytes:
                largest_shard_raw_bytes = raw_bytes
                largest_shard_gzip_bytes = gzip_bytes
                largest_shard_area = jurisdiction

        area_entries.append(
            {
                "jurisdiction": jurisdiction,
                "slug": area_slug,
                "display_name": "Arlington County" if jurisdiction == "Arlington" else ("Richmond" if jurisdiction == "Richmond BC" else ("Vancouver" if jurisdiction == "Vancouver WA" else jurisdiction)),
                "jurisdiction_type": "county" if jurisdiction == "Arlington" or jurisdiction.endswith(" County") else "city",
                "state_province": region_id.upper(),
                "country": "Canada" if region_id in {"bc", "on", "qc"} else "United States",
                "bounds": bounds_from_features(features),
                "tree_count": len(features),
                "zip_codes": summarize_zip_codes(features),
                "species_counts": summarize_species_counts(features),
                "ownership_groups": summarize_ownership_groups(features),
                "shards": shard_entries,
            }
        )

    area_index_name = f"trees.{region_id}.area-index.v2.json"
    (data_dir / area_index_name).write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "region": region_id,
                "strategy": "area_shard",
                "items": area_entries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    region_entry["label"] = REGION_LABELS.get(region_id, region_id.upper())
    region_entry["available"] = bool(area_entries)
    region_entry["data_path"] = None
    region_entry["tree_count"] = sum(int(item["tree_count"]) for item in area_entries)
    region_entry["city_count"] = len(area_entries)
    region_entry["cities"] = [str(item["jurisdiction"]) for item in area_entries]
    all_region_features = [feature for features in area_feature_map.values() for feature in features]
    region_entry["bounds"] = bounds_from_features(all_region_features) if all_region_features else region_entry.get("bounds")
    region_entry["species_counts"] = summarize_species_counts(
        all_region_features
    )
    region_entry["ownership_groups"] = summarize_ownership_groups(
        all_region_features
    )
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
    region_entry["area_split"] = {
        "strategy": "area_shard",
        "index_path": f"/data/{area_index_name}",
        "area_count": len(area_entries),
        "shard_count": shard_count,
        "ready": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate area-index and shard publish artifacts.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json and published tree files.")
    parser.add_argument("--region", default="all", help="Region id to refresh, e.g. wa, or 'all'.")
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
        write_region_area_shards(data_dir, region_entry, str(meta.get("generated_at", "")))

    for stale_path in data_dir.glob("trees.*.city-index.v1.json"):
        stale_path.unlink()

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
