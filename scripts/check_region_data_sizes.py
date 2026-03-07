#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any

WARNING_BYTES = 35 * 1024 * 1024
HIGH_WARNING_BYTES = 45 * 1024 * 1024
HARD_FAIL_BYTES = 50 * 1024 * 1024


def classify_warning_level(raw_bytes: int) -> str:
    if raw_bytes >= HARD_FAIL_BYTES:
        return "hard_fail"
    if raw_bytes >= HIGH_WARNING_BYTES:
        return "high_warning"
    if raw_bytes >= WARNING_BYTES:
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
        city_split = None
        largest_city = None
        raw_bytes = 0
        gzip_bytes = 0
        warning_level = "none"
        if region.get("city_split"):
            city_split_meta = region["city_split"]
            city_index_path = data_dir / Path(city_split_meta["index_path"]).name
            if not city_index_path.exists():
                raise FileNotFoundError(f"Missing city split index file: {city_index_path}")
            city_index = json.loads(city_index_path.read_text(encoding="utf-8"))
            items = city_index.get("items", [])
            if int(city_split_meta.get("file_count", -1)) != len(items):
                raise RuntimeError(
                    f"City split file_count mismatch for region {region['id']}: "
                    f"meta={city_split_meta.get('file_count')} actual={len(items)}"
                )
            city_tree_total = 0
            combined_features: list[dict[str, Any]] = []
            for item in items:
                city_data_path = data_dir / Path(item["data_path"]).name
                if not city_data_path.exists():
                    raise FileNotFoundError(f"Missing city split file: {city_data_path}")
                city_raw = city_data_path.stat().st_size
                city_gzip = len(gzip.compress(city_data_path.read_bytes()))
                city_level = classify_warning_level(city_raw)
                if int(item.get("raw_bytes", -1)) != city_raw or int(item.get("gzip_bytes", -1)) != city_gzip:
                    raise RuntimeError(
                        f"City split size metadata mismatch for {item['city']}: "
                        f"meta=({item.get('raw_bytes')},{item.get('gzip_bytes')}) actual=({city_raw},{city_gzip})"
                    )
                city_payload = json.loads(city_data_path.read_text(encoding="utf-8"))
                combined_features.extend(city_payload.get("features", []))
                city_tree_total += int(item.get("tree_count", 0))
                if largest_city is None or city_raw > largest_city["raw_bytes"]:
                    largest_city = {
                        "city": item["city"],
                        "raw_bytes": city_raw,
                        "gzip_bytes": city_gzip,
                        "warning_level": city_level,
                    }
                hard_fail = hard_fail or city_level == "hard_fail"
            if city_tree_total != int(region["tree_count"]):
                raise RuntimeError(
                    f"City split tree_count mismatch for region {region['id']}: "
                    f"region={region['tree_count']} city_sum={city_tree_total}"
                )
            combined_payload = {"type": "FeatureCollection", "features": combined_features}
            combined_payload_bytes = json.dumps(combined_payload, ensure_ascii=False).encode("utf-8")
            raw_bytes = len(combined_payload_bytes)
            gzip_bytes = len(gzip.compress(combined_payload_bytes))
            warning_level = classify_warning_level(raw_bytes)
            city_split = {
                "strategy": city_split_meta.get("strategy"),
                "ready": bool(city_split_meta.get("ready")),
                "file_count": len(items),
                "index_path": city_split_meta.get("index_path"),
                "largest_city": largest_city,
            }
        else:
            data_path_value = region.get("data_path")
            if not data_path_value:
                raise RuntimeError(f"Region {region['id']} has neither city_split nor data_path.")
            data_path = data_dir / Path(data_path_value).name
            if not data_path.exists():
                raise FileNotFoundError(f"Missing region file: {data_path}")
            raw_bytes = data_path.stat().st_size
            gzip_bytes = len(gzip.compress(data_path.read_bytes()))
            warning_level = classify_warning_level(raw_bytes)
            hard_fail = hard_fail or warning_level == "hard_fail"

        meta_raw = int(region.get("raw_bytes", -1))
        meta_gzip = int(region.get("gzip_bytes", -1))
        meta_warning = str(region.get("warning_level", ""))
        if meta_raw != raw_bytes or meta_gzip != gzip_bytes or meta_warning != warning_level:
            raise RuntimeError(
                f"meta.v2.json size metadata mismatch for region {region['id']}: "
                f"meta=({meta_raw},{meta_gzip},{meta_warning}) actual=({raw_bytes},{gzip_bytes},{warning_level})"
            )

        regions.append(
            {
                "id": region["id"],
                "label": region["label"],
                "tree_count": int(region["tree_count"]),
                "raw_bytes": raw_bytes,
                "gzip_bytes": gzip_bytes,
                "warning_level": warning_level,
                "data_path": region.get("data_path"),
                "city_split": city_split,
            }
        )

    return {
        "thresholds": {
            "warning": WARNING_BYTES,
            "high_warning": HIGH_WARNING_BYTES,
            "hard_fail": HARD_FAIL_BYTES,
        },
        "regions": regions,
        "hard_fail": hard_fail,
    }


def print_table(report: dict[str, Any]) -> None:
    header = f"{'Region':<8} {'Trees':>10} {'Raw':>12} {'Gzip':>12} {'Level':>14} {'Split':>8}  Path"
    print(header)
    print("-" * len(header))
    for region in report["regions"]:
        split_label = "city" if region["city_split"] else "-"
        path_label = region["city_split"]["index_path"] if region["city_split"] else region["data_path"]
        print(
            f"{region['label']:<8} "
            f"{region['tree_count']:>10,} "
            f"{format_bytes(region['raw_bytes']):>12} "
            f"{format_bytes(region['gzip_bytes']):>12} "
            f"{region['warning_level']:>14} "
            f"{split_label:>8}  "
            f"{path_label}"
        )


def append_summary(report: dict[str, Any], summary_path: Path) -> None:
    lines = [
        "## Region Data Size Check",
        "",
        "| Region | Trees | Raw | Gzip | Level | Split | File |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for region in report["regions"]:
        split_label = region["city_split"]["strategy"] if region["city_split"] else "-"
        file_label = region["city_split"]["index_path"] if region["city_split"] else region["data_path"]
        lines.append(
            f"| {region['label']} | {region['tree_count']:,} | {format_bytes(region['raw_bytes'])} | "
            f"{format_bytes(region['gzip_bytes'])} | {region['warning_level']} | {split_label} | `{file_label}` |"
        )
    lines.append("")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check published city-split region data file sizes.")
    parser.add_argument(
        "--data-dir",
        default="public/data",
        help="Directory containing meta.v2.json, trees.<region>.city-index.v1.json, and trees.<region>.city.<slug>.v1.geojson",
    )
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
        print("ERROR: One or more published city files reached the hard-fail threshold of 50 MiB raw.", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
