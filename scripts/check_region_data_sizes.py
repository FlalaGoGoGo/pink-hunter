#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any

TARGET_SPLIT_BYTES = 20 * 1024 * 1024
MUST_SPLIT_BYTES = 25 * 1024 * 1024
HARD_FAIL_BYTES = 30 * 1024 * 1024
AGGREGATE_WARNING_BYTES = 35 * 1024 * 1024
AGGREGATE_HIGH_WARNING_BYTES = 45 * 1024 * 1024
AGGREGATE_HARD_FAIL_BYTES = 50 * 1024 * 1024


def classify_shard_level(raw_bytes: int) -> str:
    if raw_bytes >= HARD_FAIL_BYTES:
        return "hard_fail"
    if raw_bytes >= MUST_SPLIT_BYTES:
        return "high_warning"
    if raw_bytes >= TARGET_SPLIT_BYTES:
        return "warning"
    return "none"


def classify_aggregate_level(raw_bytes: int) -> str:
    if raw_bytes >= AGGREGATE_HARD_FAIL_BYTES:
        return "hard_fail"
    if raw_bytes >= AGGREGATE_HIGH_WARNING_BYTES:
        return "high_warning"
    if raw_bytes >= AGGREGATE_WARNING_BYTES:
        return "warning"
    return "none"


def format_bytes(raw_bytes: int) -> str:
    return f"{raw_bytes / 1024 / 1024:.2f} MiB"


def build_report(data_dir: Path) -> dict[str, Any]:
    meta_path = data_dir / "meta.v2.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    regions = []
    hard_fail = False

    for region in meta.get("regions", []):
        area_split = region.get("area_split")
        if not area_split:
          raise RuntimeError(f"Region {region['id']} is missing area_split metadata.")

        area_index_path = data_dir / Path(str(area_split["index_path"])).name
        if not area_index_path.exists():
            raise FileNotFoundError(f"Missing area index file: {area_index_path}")

        area_index = json.loads(area_index_path.read_text(encoding="utf-8"))
        aggregate_raw_bytes = 0
        aggregate_gzip_bytes = 0
        largest_shard = None
        shard_count = 0

        for item in area_index.get("items", []):
            for shard in item.get("shards", []):
                shard_path = data_dir / Path(str(shard["data_path"])).name
                if not shard_path.exists():
                    raise FileNotFoundError(f"Missing shard file: {shard_path}")
                shard_raw = shard_path.stat().st_size
                shard_gzip = len(gzip.compress(shard_path.read_bytes()))
                shard_level = classify_shard_level(shard_raw)
                if int(shard.get("raw_bytes", -1)) != shard_raw or int(shard.get("gzip_bytes", -1)) != shard_gzip:
                    raise RuntimeError(
                        f"Shard size metadata mismatch for {item['jurisdiction']} / {shard['id']}: "
                        f"meta=({shard.get('raw_bytes')},{shard.get('gzip_bytes')}) actual=({shard_raw},{shard_gzip})"
                    )
                aggregate_raw_bytes += shard_raw
                aggregate_gzip_bytes += shard_gzip
                shard_count += 1
                if largest_shard is None or shard_raw > largest_shard["raw_bytes"]:
                    largest_shard = {
                        "area": item["jurisdiction"],
                        "id": shard["id"],
                        "raw_bytes": shard_raw,
                        "gzip_bytes": shard_gzip,
                        "warning_level": shard_level,
                    }
                hard_fail = hard_fail or shard_level == "hard_fail"

        aggregate_level = classify_aggregate_level(aggregate_raw_bytes)

        if int(region.get("aggregate_raw_bytes", region.get("raw_bytes", -1))) != aggregate_raw_bytes:
            raise RuntimeError(f"Aggregate raw size mismatch for region {region['id']}.")
        if int(region.get("aggregate_gzip_bytes", region.get("gzip_bytes", -1))) != aggregate_gzip_bytes:
            raise RuntimeError(f"Aggregate gzip size mismatch for region {region['id']}.")
        if str(region.get("aggregate_warning_level", region.get("warning_level", ""))) != aggregate_level:
            raise RuntimeError(f"Aggregate warning level mismatch for region {region['id']}.")
        if int(region.get("largest_shard_raw_bytes", -1)) != int((largest_shard or {}).get("raw_bytes", 0)):
            raise RuntimeError(f"Largest shard raw size mismatch for region {region['id']}.")

        regions.append(
            {
                "id": region["id"],
                "label": region["label"],
                "tree_count": int(region["tree_count"]),
                "aggregate_raw_bytes": aggregate_raw_bytes,
                "aggregate_gzip_bytes": aggregate_gzip_bytes,
                "aggregate_warning_level": aggregate_level,
                "largest_shard": largest_shard,
                "area_split": {
                    "strategy": area_split.get("strategy"),
                    "ready": bool(area_split.get("ready")),
                    "area_count": int(area_split.get("area_count", 0)),
                    "shard_count": shard_count,
                    "index_path": area_split.get("index_path"),
                },
            }
        )

    return {
        "thresholds": {
            "target_split": TARGET_SPLIT_BYTES,
            "must_split": MUST_SPLIT_BYTES,
            "hard_fail": HARD_FAIL_BYTES,
            "aggregate_warning": AGGREGATE_WARNING_BYTES,
            "aggregate_high_warning": AGGREGATE_HIGH_WARNING_BYTES,
            "aggregate_hard_fail": AGGREGATE_HARD_FAIL_BYTES,
        },
        "regions": regions,
        "hard_fail": hard_fail,
    }


def print_table(report: dict[str, Any]) -> None:
    header = (
        f"{'Region':<8} {'Trees':>10} {'Agg Raw':>12} {'Agg Gzip':>12} "
        f"{'Agg Level':>12} {'Largest':>12} {'Shard Level':>12} {'Shards':>8}  Index"
    )
    print(header)
    print("-" * len(header))
    for region in report["regions"]:
        largest_shard = region["largest_shard"] or {"raw_bytes": 0, "warning_level": "none"}
        print(
            f"{region['label']:<8} "
            f"{region['tree_count']:>10,} "
            f"{format_bytes(region['aggregate_raw_bytes']):>12} "
            f"{format_bytes(region['aggregate_gzip_bytes']):>12} "
            f"{region['aggregate_warning_level']:>12} "
            f"{format_bytes(int(largest_shard['raw_bytes'])):>12} "
            f"{largest_shard['warning_level']:>12} "
            f"{region['area_split']['shard_count']:>8}  "
            f"{region['area_split']['index_path']}"
        )


def append_summary(report: dict[str, Any], summary_path: Path) -> None:
    lines = [
        "## Area Shard Size Check",
        "",
        "| Region | Trees | Aggregate Raw | Aggregate Gzip | Aggregate Level | Largest Shard | Largest Shard Level | Shards | Index |",
        "| --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |",
    ]
    for region in report["regions"]:
        largest_shard = region["largest_shard"] or {"raw_bytes": 0, "warning_level": "none"}
        lines.append(
            f"| {region['label']} | {region['tree_count']:,} | {format_bytes(region['aggregate_raw_bytes'])} | "
            f"{format_bytes(region['aggregate_gzip_bytes'])} | {region['aggregate_warning_level']} | "
            f"{format_bytes(int(largest_shard['raw_bytes']))} | {largest_shard['warning_level']} | "
            f"{region['area_split']['shard_count']} | `{region['area_split']['index_path']}` |"
        )
    lines.append("")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check published area-shard data file sizes.")
    parser.add_argument("--data-dir", default="public/data", help="Directory containing meta.v2.json and trees.<region>.area-index.v2.json.")
    parser.add_argument("--json-out", help="Optional path to write machine-readable JSON report.")
    parser.add_argument("--summary-file", help="Optional markdown summary path, e.g. $GITHUB_STEP_SUMMARY.")
    args = parser.parse_args()

    report = build_report(Path(args.data_dir))
    print_table(report)

    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.summary_file:
        append_summary(report, Path(args.summary_file))

    if report["hard_fail"]:
        print("ERROR: One or more published shard files reached the hard-fail threshold of 30 MiB raw.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
