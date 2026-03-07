#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import REGION_LABELS, SPECIES_GROUPS, summarize_species_counts


CITY_FILE_PATTERN = re.compile(r"^trees\.(?P<region>[a-z]{2})\.city\..+\.v1\.geojson$")


def empty_species_counts() -> dict[str, int]:
    return {species: 0 for species in SPECIES_GROUPS}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh meta.v2.json species summary fields from published city files.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json and city publish files.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
      raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    region_features: dict[str, list[dict]] = defaultdict(list)
    region_cities: dict[str, set[str]] = defaultdict(set)

    for path in sorted(data_dir.glob("trees.*.city.*.v1.geojson")):
        match = CITY_FILE_PATTERN.match(path.name)
        if not match:
            continue
        region = match.group("region")
        payload = json.loads(path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        region_features[region].extend(features)
        for feature in features:
            city = str(feature.get("properties", {}).get("city", "")).strip()
            if city:
                region_cities[region].add(city)

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
        all_features.extend(features)

        if not features and region_id in REGION_LABELS:
            region_entry["species_counts"] = empty_species_counts()

    meta["included_records"] = len(all_features)
    meta["species_counts"] = summarize_species_counts(all_features) if all_features else empty_species_counts()

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
