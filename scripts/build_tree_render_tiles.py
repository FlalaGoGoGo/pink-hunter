#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PMTILES_FILENAME = "trees.render.v1.pmtiles"
MANIFEST_FILENAME = "trees.render.v1.json"
VECTOR_LAYER = "trees"
MIN_ZOOM = 8
MAX_ZOOM = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build PMTiles render artifacts for tree points.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing published tree shards.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_shard_lookup(data_dir: Path) -> tuple[dict[str, dict[str, str]], list[str], list[list[float]]]:
    shard_lookup: dict[str, dict[str, str]] = {}
    regions: list[str] = []
    min_lon = float("inf")
    min_lat = float("inf")
    max_lon = float("-inf")
    max_lat = float("-inf")

    for index_path in sorted(data_dir.glob("trees.*.area-index.v2.json")):
        area_index = load_json(index_path)
        region = str(area_index["region"])
        regions.append(region)
        for item in area_index["items"]:
            area_slug = str(item["slug"])
            city = str(item["jurisdiction"])
            bounds = item.get("bounds") or []
            if len(bounds) == 2:
                [item_min_lon, item_min_lat], [item_max_lon, item_max_lat] = bounds
                min_lon = min(min_lon, item_min_lon)
                min_lat = min(min_lat, item_min_lat)
                max_lon = max(max_lon, item_max_lon)
                max_lat = max(max_lat, item_max_lat)
            for shard in item["shards"]:
                shard_lookup[str(shard["data_path"])] = {
                    "region": region,
                    "area_slug": area_slug,
                    "city": city,
                    "data_path": str(shard["data_path"]),
                }

    return shard_lookup, sorted(set(regions)), [[min_lon, min_lat], [max_lon, max_lat]]


def build_render_feature(
    coordinates: list[float],
    properties: dict[str, Any],
    shard_meta: dict[str, str],
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coordinates,
        },
        "properties": {
            "id": properties["id"],
            "species_group": properties["species_group"],
            "ownership": properties["ownership"],
            "city": shard_meta["city"],
            "region": shard_meta["region"],
            "area_slug": shard_meta["area_slug"],
            "data_path": shard_meta["data_path"],
        },
    }


def resolve_data_path(project_root: Path, data_path: str) -> Path:
    normalized = data_path.lstrip("/")
    return project_root / "public" / normalized


def write_render_ndjson(
    project_root: Path,
    shard_lookup: dict[str, dict[str, str]],
    output_path: Path,
) -> dict[str, Any]:
    tree_count = 0
    region_counts: Counter[str] = Counter()

    with output_path.open("w", encoding="utf-8") as handle:
        for data_path in sorted(shard_lookup):
            shard_meta = shard_lookup[data_path]
            geojson_path = resolve_data_path(project_root, data_path)
            collection = load_json(geojson_path)
            for feature in collection["features"]:
                coordinates = feature["geometry"]["coordinates"]
                render_feature = build_render_feature(coordinates, feature["properties"], shard_meta)
                handle.write(json.dumps(render_feature, separators=(",", ":")) + "\n")
                tree_count += 1
                region_counts[shard_meta["region"]] += 1

    if tree_count == 0:
        raise SystemExit("No tree features found while building render tiles.")

    return {
        "tree_count": tree_count,
        "region_counts": dict(region_counts),
    }


def run_tippecanoe(ndjson_path: Path, output_path: Path) -> None:
    if shutil.which("tippecanoe") is None:
        raise SystemExit("tippecanoe is required to build PMTiles render artifacts.")

    subprocess.run(
        [
            "tippecanoe",
            "-f",
            "-o",
            str(output_path),
            "-l",
            VECTOR_LAYER,
            "-Z",
            str(MIN_ZOOM),
            "-z",
            str(MAX_ZOOM),
            "-P",
            "--drop-densest-as-needed",
            "--extend-zooms-if-still-dropping",
            str(ndjson_path),
        ],
        check=True,
    )


def write_manifest(output_path: Path, stats: dict[str, Any], regions: list[str]) -> None:
    manifest = {
        "generated_at": now_iso(),
        "path": f"/data/{PMTILES_FILENAME}",
        "vector_layer": VECTOR_LAYER,
        "minzoom": MIN_ZOOM,
        "maxzoom": MAX_ZOOM,
        "tree_count": stats["tree_count"],
        "bounds": stats["bounds"],
        "regions": regions,
    }
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    project_root = repo_root()
    shard_lookup, regions, bounds = build_shard_lookup(data_dir)

    output_pmtiles = data_dir / PMTILES_FILENAME
    output_manifest = data_dir / MANIFEST_FILENAME

    with tempfile.TemporaryDirectory(prefix="pink-hunter-render-tiles.") as temp_dir:
        ndjson_path = Path(temp_dir) / "trees.render.ndjson"
        stats = write_render_ndjson(project_root, shard_lookup, ndjson_path)
        stats["bounds"] = bounds
        run_tippecanoe(ndjson_path, output_pmtiles)
        write_manifest(output_manifest, stats, regions)

    print(
        f"Built {output_pmtiles} and {output_manifest} "
        f"for {stats['tree_count']} trees across {len(regions)} regions."
    )


if __name__ == "__main__":
    main()
