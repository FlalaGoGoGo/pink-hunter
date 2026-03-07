#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import (
    FREMONT_BOUNDARY_LAYER,
    FREMONT_DATASET_PAGE,
    FREMONT_TREEPLOTTER_URL,
    MILPITAS_LAYER,
    PUBLIC_DATA_DIR,
    MAPPING_PATH,
    NORMALIZED_DIR,
    SAN_MATEO_DATASET_PAGE,
    SAN_MATEO_LAYER,
    SAN_RAFAEL_DATASET_PAGE,
    SAN_RAFAEL_TREES_LAYER,
    SUBTYPE_MAPPING_PATH,
    assign_zip_code,
    canonical_ownership,
    classify_tree_record,
    decode_wkb_point_hex,
    expand_abbreviated_botanical_name,
    fetch_all_features,
    fetch_json,
    fetch_ods_export_rows,
    fetch_us_city_zip_index,
    generic_scientific_name_for_common_hint,
    iso_from_epoch,
    load_mapping,
    load_subtype_mapping,
    normalize_scientific_name,
    post_form_with_curl,
    slugify_token,
    title_case_if_upper,
    web_mercator_to_lon_lat,
)

NORMALIZED_HEADER = [
    "id",
    "city",
    "source_dataset",
    "scientific_raw",
    "scientific_normalized",
    "common_name",
    "subtype_name",
    "zip_code",
    "species_group",
    "ownership",
    "ownership_raw",
    "lat",
    "lon",
    "included",
]

MILPITAS_DATASET_PAGE = "https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/Trees_RO/FeatureServer/0"
SAN_RAFAEL_BOUNDARY_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=4c64d7f5f8384283ae83be8fd861afb4"
TREEPLOTTER_CLIENT_VERSION = "v3.9.65"
FREMONT_DB_ENDPOINT = "https://pg-cloud.com/main/server/db.php"
SALINAS_DATASET = "https://cityofsalinas.opendatasoft.com/api/explore/v2.1/catalog/datasets/tree-inventory"

SUPPORTED_CITIES = ("Milpitas", "San Mateo", "San Rafael", "Fremont", "Salinas")


def domain_lookup(layer_info: dict[str, Any], field_name: str) -> dict[Any, str]:
    for field in layer_info.get("fields") or []:
        if field.get("name") != field_name:
            continue
        coded_values = ((field.get("domain") or {}).get("codedValues")) or []
        return {item.get("code"): str(item.get("name") or "") for item in coded_values}
    return {}


def write_city_geojson(region: str, city: str, features: list[dict[str, Any]]) -> Path:
    path = PUBLIC_DATA_DIR / f"trees.{region}.city.{slugify_token(city)}.v1.geojson"
    payload = {"type": "FeatureCollection", "features": sorted(features, key=lambda item: item["properties"]["id"])}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def load_normalized_rows() -> list[dict[str, str]]:
    path = NORMALIZED_DIR / "trees_normalized.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_normalized_rows(rows: list[dict[str, Any]]) -> None:
    path = NORMALIZED_DIR / "trees_normalized.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_rows = []
    for row in rows:
        normalized_rows.append({column: str(row.get(column, "")) for column in NORMALIZED_HEADER})
    normalized_rows.sort(key=lambda item: item["id"])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_HEADER)
        writer.writeheader()
        writer.writerows(normalized_rows)


def recompute_unknown_items(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        if row.get("included") == "1":
            continue
        scientific = (row.get("scientific_normalized") or "").strip()
        if scientific:
            counter[scientific] += 1
    return [
        {"scientific_name_normalized": name, "count": count}
        for name, count in counter.most_common()
    ]


def load_meta() -> dict[str, Any]:
    return json.loads((PUBLIC_DATA_DIR / "meta.v2.json").read_text(encoding="utf-8"))


def save_meta(meta: dict[str, Any]) -> None:
    (PUBLIC_DATA_DIR / "meta.v2.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def refresh_publish_indexes() -> None:
    subprocess.run(
        ["python3", "scripts/refresh_region_city_splits.py", "--data-dir", "public/data", "--region", "ca"],
        check=True,
    )
    subprocess.run(
        ["python3", "scripts/refresh_coverage_metadata.py", "--data-dir", "public/data"],
        check=True,
    )


def fetch_milpitas() -> dict[str, Any]:
    info = fetch_json(MILPITAS_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        MILPITAS_LAYER,
        "1=1",
        ["OBJECTID", "Name", "Genus", "Species", "OwnedBy", "MaintBy"],
        "OBJECTID",
    )
    owner_domain = domain_lookup(info, "OwnedBy")
    zip_index = fetch_us_city_zip_index("Milpitas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("Species") or "").strip()
        common_name = title_case_if_upper(attrs.get("Name")) or None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        owned_by = owner_domain.get(attrs.get("OwnedBy")) or ""
        if owned_by == "<null>":
            owned_by = ""
        maintained_by = title_case_if_upper(attrs.get("MaintBy")) or ""
        ownership_raw = owned_by or maintained_by or "Unknown"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"milpitas-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Milpitas",
                "source_dataset": "Trees RO",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Milpitas",
                    "source_dataset": "Trees RO",
                    "source_department": "City of Milpitas",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "Milpitas",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees RO",
            "city": "Milpitas",
            "endpoint": MILPITAS_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def fetch_san_mateo() -> dict[str, Any]:
    info = fetch_json(SAN_MATEO_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        SAN_MATEO_LAYER,
        "ACTIVE=1",
        ["OBJECTID", "ACTIVE", "SPP", "ID", "UNIQUEID"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("San Mateo")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SPP") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of San Mateo"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"san-mateo-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "San Mateo",
                "source_dataset": "Street Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Mateo",
                    "source_dataset": "Street Trees",
                    "source_department": "City of San Mateo Public Works",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "San Mateo",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Trees",
            "city": "San Mateo",
            "endpoint": SAN_MATEO_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def fetch_san_rafael() -> dict[str, Any]:
    info = fetch_json(SAN_RAFAEL_TREES_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        SAN_RAFAEL_TREES_LAYER,
        "1=1",
        ["ObjectId", "UniqueID", "Species_Name", "Condition", "Species_Type"],
        "ObjectId",
    )
    zip_index = fetch_us_city_zip_index("San Rafael")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        common_name = title_case_if_upper(attrs.get("Species_Name")) or None
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of San Rafael"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"san-rafael-{attrs.get('UniqueID') or attrs.get('ObjectId')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "San Rafael",
                "source_dataset": "Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw or "",
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Rafael",
                    "source_dataset": "Trees",
                    "source_department": "City of San Rafael",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "San Rafael",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees",
            "city": "San Rafael",
            "endpoint": SAN_RAFAEL_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def init_treeplotter_session(folder: str, landing_url: str) -> str:
    fd, cookie_path = tempfile.mkstemp(prefix=f"{slugify_token(folder)}_", suffix=".cookies")
    os.close(fd)
    landing = subprocess.run(["curl", "-sL", "-c", cookie_path, landing_url], capture_output=True, text=True, check=False)
    if landing.returncode != 0:
        raise RuntimeError(f"Failed to open TreePlotter landing page for {folder}: {landing.stderr.strip()}")
    payload = post_form_with_curl(
        FREMONT_DB_ENDPOINT,
        [("action", "sessionCheck"), ("params[folder]", folder)],
        headers={"X-Client-Version": TREEPLOTTER_CLIENT_VERSION},
        cookie_path=cookie_path,
    )
    if payload.get("status") != "OK":
        raise RuntimeError(f"TreePlotter sessionCheck failed for {folder}: {payload}")
    return cookie_path


def retrieve_treeplotter_rows(
    folder: str,
    table: str,
    fields: dict[str, dict[str, str]],
    *,
    cookie_path: str,
    limit: int = 2000,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        form = [
            ("action", "retrieveDataAlias"),
            ("params[folder]", folder),
            ("params[table]", table),
            ("params[firstIndex]", offset),
            ("params[limit]", limit),
            ("params[sortBy]", "pid"),
            ("params[sortOrder]", "asc"),
            ("params[timezoneOffset]", 0),
        ]
        for field_name, details in fields.items():
            form.extend(
                [
                    (f"params[fields][{field_name}][data_type]", details["data_type"]),
                    (f"params[fields][{field_name}][input_type]", details["input_type"]),
                    (f"params[fields][{field_name}][name]", field_name),
                    (f"params[fields][{field_name}][referencer]", table),
                ]
            )
        payload = post_form_with_curl(
            FREMONT_DB_ENDPOINT,
            form,
            headers={"X-Client-Version": TREEPLOTTER_CLIENT_VERSION},
            cookie_path=cookie_path,
        )
        if payload.get("status") != "OK":
            raise RuntimeError(f"TreePlotter retrieveDataAlias failed for {folder}/{table} at offset {offset}: {payload}")
        batch = payload.get("resultsArray") or []
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += len(batch)
    return rows


def fetch_fremont() -> dict[str, Any]:
    boundary_info = fetch_json(FREMONT_BOUNDARY_LAYER, {"f": "pjson"})
    zip_index = fetch_us_city_zip_index("Fremont")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    cookie_path = init_treeplotter_session("FremontCA", FREMONT_TREEPLOTTER_URL)
    try:
        lookup_rows = retrieve_treeplotter_rows(
            "FremontCA",
            "species",
            {
                "pid": {"data_type": "integer", "input_type": "number"},
                "sp_code": {"data_type": "character varying", "input_type": "text"},
                "genus": {"data_type": "character varying", "input_type": "text"},
                "latin_name": {"data_type": "character varying", "input_type": "text"},
                "common_name": {"data_type": "character varying", "input_type": "text"},
                "cultivar": {"data_type": "character varying", "input_type": "text"},
            },
            cookie_path=cookie_path,
        )
        species_lookup = {}
        for row in lookup_rows:
            pid = row["pid"]["val"]
            species_lookup[pid] = {
                "latin_name": row["latin_name"]["alias"] or row["latin_name"]["val"] or "",
                "common_name": row["common_name"]["alias"] or row["common_name"]["val"] or "",
                "cultivar": row["cultivar"]["alias"] or row["cultivar"]["val"] or "",
            }

        tree_rows = retrieve_treeplotter_rows(
            "FremontCA",
            "trees",
            {
                "pid": {"data_type": "integer", "input_type": "number"},
                "geom": {"data_type": "geometry", "input_type": "hidden"},
                "species_common": {"data_type": "integer", "input_type": "select"},
                "species_latin": {"data_type": "integer", "input_type": "select"},
                "species_code": {"data_type": "integer", "input_type": "select"},
                "species_cultivar": {"data_type": "integer", "input_type": "select"},
                "organization": {"data_type": "character varying", "input_type": "text"},
                "park_name": {"data_type": "character varying", "input_type": "text"},
                "status": {"data_type": "integer", "input_type": "select"},
            },
            cookie_path=cookie_path,
            limit=5000,
        )
    finally:
        Path(cookie_path).unlink(missing_ok=True)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in tree_rows:
        geom_hex = row.get("geom", {}).get("val") or row.get("geom", {}).get("alias")
        point = decode_wkb_point_hex(geom_hex)
        if not point:
            continue
        lon, lat = web_mercator_to_lon_lat(*point)
        species_id = row.get("species_latin", {}).get("val") or row.get("species_common", {}).get("val") or row.get("species_code", {}).get("val")
        species_info = species_lookup.get(species_id, {})
        common_name = title_case_if_upper(row.get("species_common", {}).get("alias")) or title_case_if_upper(species_info.get("common_name")) or None
        latin_name = row.get("species_latin", {}).get("alias") or species_info.get("latin_name") or ""
        scientific_raw = expand_abbreviated_botanical_name(latin_name, common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar_name = (
            title_case_if_upper(row.get("species_cultivar", {}).get("alias"))
            or title_case_if_upper(species_info.get("cultivar"))
            or None
        )
        if cultivar_name and not subtype_name:
            subtype_name = cultivar_name
        ownership_raw = "Not published in public inventory"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"fremont-{row.get('pid', {}).get('val')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Fremont",
                "source_dataset": "Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Fremont",
                    "source_dataset": "Tree Inventory",
                    "source_department": "City of Fremont",
                    "source_last_edit_at": iso_from_epoch(boundary_info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "Fremont",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": "Fremont",
            "endpoint": FREMONT_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(boundary_info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(tree_rows),
            "records_included": len(output_features),
            "note": "Integrated via public TreePlotter session + official species lookup table.",
        },
    }


def fetch_salinas() -> dict[str, Any]:
    dataset_info = fetch_json(SALINAS_DATASET)
    rows = fetch_ods_export_rows(SALINAS_DATASET, where="active=1")
    zip_index = fetch_us_city_zip_index("Salinas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = (
        dataset_info.get("metas", {}).get("default", {}).get("modified")
        or dataset_info.get("metas", {}).get("data_processed")
        or ""
    )

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        point = (row.get("geo_point_2d") or {}) if isinstance(row.get("geo_point_2d"), dict) else {}
        lon = point.get("lon")
        lat = point.get("lat")
        if lon is None or lat is None:
            continue

        scientific_raw = (row.get("spp") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Salinas"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"salinas-{row.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Salinas",
                "source_dataset": "Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Salinas",
                    "source_dataset": "Tree Inventory",
                    "source_department": "City of Salinas",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Salinas",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": "Salinas",
            "endpoint": "https://cityofsalinas.opendatasoft.com/explore/dataset/tree-inventory/",
            "last_edit_at": last_edit_at,
            "records_fetched": len(rows),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Salinas OpenDataSoft tree inventory dataset.",
        },
    }


CITY_FETCHERS = {
    "Milpitas": fetch_milpitas,
    "San Mateo": fetch_san_mateo,
    "San Rafael": fetch_san_rafael,
    "Fremont": fetch_fremont,
    "Salinas": fetch_salinas,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish targeted city updates into existing city-split public data.")
    parser.add_argument("--city", action="append", choices=SUPPORTED_CITIES, help="City to refresh. Repeat for multiple cities.")
    args = parser.parse_args()

    target_cities = args.city or list(SUPPORTED_CITIES)
    results = [CITY_FETCHERS[city]() for city in target_cities]

    current_rows = load_normalized_rows()
    remaining_rows = [row for row in current_rows if row.get("city") not in target_cities]
    next_rows = remaining_rows[:]

    for result in results:
        write_city_geojson(result["region"], result["city"], result["features"])
        next_rows.extend(result["normalized_rows"])

    write_normalized_rows(next_rows)
    refresh_publish_indexes()

    unknown_items = recompute_unknown_items(load_normalized_rows())
    (PUBLIC_DATA_DIR / "unknown_scientific_names.v1.json").write_text(
        json.dumps(unknown_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    meta = load_meta()
    meta["generated_at"] = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    existing_sources = [source for source in meta.get("sources", []) if source.get("city") not in target_cities]
    existing_sources.extend(result["source"] for result in results)
    existing_sources.sort(key=lambda source: (source.get("city", ""), source.get("name", "")))
    meta["sources"] = existing_sources
    meta["source_count"] = len(existing_sources)

    latest_rows = load_normalized_rows()
    meta["total_records"] = len(latest_rows)
    meta["included_records"] = sum(1 for row in latest_rows if row.get("included") == "1")
    meta["unknown_records"] = sum(item["count"] for item in unknown_items)
    save_meta(meta)
    subprocess.run(["python3", "scripts/check_region_data_sizes.py", "--data-dir", "public/data"], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
