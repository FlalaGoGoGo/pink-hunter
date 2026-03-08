#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import io
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import (
    ARLINGTON_DATASET_PAGE,
    ARLINGTON_TREES_LAYER,
    BALTIMORE_DATASET_PAGE,
    BALTIMORE_TREES_LAYER,
    BOSTON_DATASET_PAGE,
    BOSTON_TREES_GEOJSON,
    CAMBRIDGE_DATASET_PAGE,
    CAMBRIDGE_STREET_TREES_ZIP,
    CONCORD_BOUNDARY_LAYER,
    CONCORD_DATASET_PAGE,
    CONCORD_TREEPLOTTER_URL,
    FREMONT_BOUNDARY_LAYER,
    FREMONT_DATASET_PAGE,
    FREMONT_TREEPLOTTER_URL,
    NYC_DATASET,
    NYC_DATASET_PAGE,
    NYC_METADATA,
    PHILADELPHIA_DATASET_PAGE,
    PHILADELPHIA_LAYER,
    JERSEY_CITY_DATASET_PAGE,
    JERSEY_CITY_TREES_LAYER,
    MONTREAL_DATASET_PAGE,
    MONTREAL_TREES_CSV,
    MILPITAS_LAYER,
    OTTAWA_DATASET_PAGE,
    OTTAWA_TREES_LAYER,
    PUBLIC_DATA_DIR,
    REGION_LABELS,
    MAPPING_PATH,
    NORMALIZED_DIR,
    SAN_MATEO_DATASET_PAGE,
    SAN_MATEO_LAYER,
    SAN_RAFAEL_DATASET_PAGE,
    SAN_RAFAEL_TREES_LAYER,
    SOUTH_SF_BOUNDARY_LAYER,
    SOUTH_SF_DATASET_PAGE,
    SOUTH_SF_GRIDS_ENDPOINT,
    SOUTH_SF_SEARCH_ENDPOINT,
    SUBTYPE_MAPPING_PATH,
    TORONTO_DATASET_PAGE,
    assign_zip_code,
    canonical_ownership,
    classify_tree_record,
    decode_wkb_point_hex,
    expand_abbreviated_botanical_name,
    fetch_all_features,
    fetch_binary,
    fetch_json,
    fetch_ods_export_rows,
    fetch_soda_count,
    fetch_soda_rows,
    fetch_us_city_zip_index,
    generic_scientific_name_for_common_hint,
    iso_from_epoch,
    load_mapping,
    load_zipped_point_shapefile_rows,
    load_zipped_shapefile,
    load_subtype_mapping,
    normalize_scientific_name,
    post_form_with_curl,
    slugify_token,
    title_case_if_upper,
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
PITTSBURGH_BASE = "https://pittsburghpa.treekeepersoftware.com"
PITTSBURGH_SEARCH_ENDPOINT = f"{PITTSBURGH_BASE}/cffiles/search.cfc"
PITTSBURGH_GRIDS_ENDPOINT = f"{PITTSBURGH_BASE}/cffiles/grids.cfc"
TORONTO_STREET_TREE_ALT_CSV = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6ac4569e-fd37-4cbc-ac63-db3624c5f6a2/resource/5930412c-408e-4ee3-b473-56a790c9dfb7/download/street-tree-data_csv.csv"
NEW_WESTMINSTER_TREES_LAYER = "https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer/0"
NEW_WESTMINSTER_DATASET_PAGE = "https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer"
OTTAWA_BLOSSOM_WHERE = (
    "STATUS = 'Active' AND ("
    "UPPER(SPECIES) LIKE '%CHERRY%' OR "
    "UPPER(SPECIES) LIKE '%PLUM%' OR "
    "UPPER(SPECIES) LIKE '%PEACH%' OR "
    "UPPER(SPECIES) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPECIES) LIKE '%APPLE%'"
    ")"
)
SPECIES_TEXT_PATTERN = re.compile(r"^\s*(?P<common>.+?)\s*\((?P<scientific>[^()]+)\)\s*$")
DISPLAY_NAME_REPLACEMENTS = {
    "Chery": "Cherry",
    "Crab Apple": "Crabapple",
}

SUPPORTED_CITIES = (
    "Arlington",
    "Baltimore",
    "Boston",
    "Jersey City",
    "Milpitas",
    "San Mateo",
    "San Rafael",
    "Fremont",
    "Salinas",
    "Concord",
    "South San Francisco",
    "New York City",
    "Philadelphia",
    "Cambridge",
    "Pittsburgh",
    "Ottawa",
    "Toronto",
    "Montreal",
    "New Westminster",
)


def clean_display_name(raw_value: str | None) -> str | None:
    text = (raw_value or "").strip()
    if not text or text in {"<Null>", "N/A"}:
        return None
    text = re.sub(r"\s+", " ", text)
    for source, replacement in DISPLAY_NAME_REPLACEMENTS.items():
        text = text.replace(source, replacement)
    titled = title_case_if_upper(text)
    text = titled or text
    if text.count(",") == 1:
        left, right = [part.strip() for part in text.split(",", 1)]
        if left and right:
            text = f"{right} {left}"
    return text.strip()


def parse_species_text(raw_value: str | None) -> tuple[str, str | None]:
    text = clean_display_name(raw_value)
    if not text:
        return "", None
    match = SPECIES_TEXT_PATTERN.match(text)
    if match:
        common_name = clean_display_name(match.group("common"))
        scientific_raw = expand_abbreviated_botanical_name(match.group("scientific"), common_name)
        return scientific_raw, common_name
    return generic_scientific_name_for_common_hint(text), text


def clean_common_name(raw_value: str | None) -> str | None:
    text = clean_display_name(raw_value)
    if not text:
        return None
    letters = [character for character in text if character.isalpha()]
    if letters and all(character.islower() for character in letters):
        return text.title()
    return text


def format_scientific_display_name(raw_value: str | None, common_name: str | None = None) -> str:
    text = expand_abbreviated_botanical_name(raw_value, common_name).strip()
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text.replace("×", "x"))
    tokens = text.split(" ")
    formatted: list[str] = []
    lower_tokens = {"x", "sp", "sp.", "spp", "spp.", "species", "var", "var.", "subsp", "subsp.", "ssp", "ssp."}
    for index, token in enumerate(tokens):
        if not token:
            continue
        if index == 0 and re.search(r"[A-Za-z]", token):
            formatted.append(token.capitalize())
            continue
        if token.lower() in lower_tokens:
            formatted.append(token.lower())
            continue
        if token.startswith("'") and token.endswith("'"):
            formatted.append(token)
            continue
        if re.fullmatch(r"[A-Z][a-z]+", token):
            formatted.append(token)
            continue
        if re.search(r"[A-Za-z]", token):
            formatted.append(token.lower())
            continue
        formatted.append(token)
    return " ".join(formatted)


def parse_dash_species(raw_value: str | None) -> tuple[str, str | None]:
    text = (raw_value or "").strip()
    if not text:
        return "", None
    if " - " not in text:
        common_name = clean_common_name(text)
        return format_scientific_display_name(text, common_name), common_name
    scientific_part, common_part = text.split(" - ", 1)
    common_name = clean_common_name(common_part)
    scientific_raw = format_scientific_display_name(scientific_part, common_name)
    return scientific_raw, common_name


def domain_lookup(layer_info: dict[str, Any], field_name: str) -> dict[Any, str]:
    for field in layer_info.get("fields") or []:
        if field.get("name") != field_name:
            continue
        coded_values = ((field.get("domain") or {}).get("codedValues")) or []
        return {item.get("code"): str(item.get("name") or "") for item in coded_values}
    return {}


def load_remote_geojson(url: str) -> dict[str, Any]:
    response = subprocess.run(["curl", "-sL", url], capture_output=True, text=True, check=False)
    if response.returncode != 0:
        raise RuntimeError(f"Failed to download GeoJSON from {url}: {response.stderr.strip()}")
    return json.loads(response.stdout.lstrip("\ufeff"))


def iter_remote_csv_rows(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
            yield from csv.DictReader(text_stream)
            return
    except Exception:
        pass

    insecure_context = ssl.create_default_context()
    insecure_context.check_hostname = False
    insecure_context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(request, timeout=180, context=insecure_context) as response:
            text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
            yield from csv.DictReader(text_stream)
            return
    except Exception:
        pass

    with tempfile.NamedTemporaryFile("wb", suffix=".csv") as handle:
        result = subprocess.run(
            ["curl", "-sL", "-k", "--max-time", "600", "-o", handle.name, url],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to download CSV from {url}: {result.stderr.strip()}")
        with open(handle.name, "r", encoding="utf-8-sig", newline="") as csv_handle:
            yield from csv.DictReader(csv_handle)


def parse_point_geometry_text(raw_value: str | None) -> tuple[float | None, float | None]:
    text = (raw_value or "").strip()
    if not text:
        return None, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            payload = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None, None
    coordinates = payload.get("coordinates") or []
    if payload.get("type") == "MultiPoint" and coordinates and coordinates[0]:
        lon, lat = coordinates[0][:2]
        return float(lon), float(lat)
    if payload.get("type") == "Point" and len(coordinates) >= 2:
        lon, lat = coordinates[:2]
        return float(lon), float(lat)
    return None, None


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


def ensure_region_entries(meta: dict[str, Any], regions: set[str]) -> None:
    existing = {region_entry.get("id") for region_entry in meta.get("regions", [])}
    for region_id in sorted(regions):
        if region_id in existing:
            continue
        meta.setdefault("regions", []).append(
            {
                "id": region_id,
                "label": REGION_LABELS[region_id],
                "available": True,
                "bounds": [[-123.08, 47.02], [-121.55, 48.08]],
                "data_path": None,
                "tree_count": 0,
                "city_count": 0,
                "cities": [],
                "raw_bytes": 0,
                "gzip_bytes": 0,
                "warning_level": "none",
                "city_split": {
                    "strategy": "city",
                    "index_path": f"/data/trees.{region_id}.city-index.v1.json",
                    "file_count": 0,
                    "ready": False,
                },
            }
        )
    meta["regions"].sort(key=lambda item: item.get("id", ""))


def refresh_publish_indexes(target_regions: set[str]) -> None:
    for region in sorted(target_regions):
        subprocess.run(
            ["python3", "scripts/refresh_region_city_splits.py", "--data-dir", "public/data", "--region", region],
            check=True,
        )
    subprocess.run(
        ["python3", "scripts/refresh_coverage_metadata.py", "--data-dir", "public/data"],
        check=True,
    )
    subprocess.run(
        ["python3", "scripts/refresh_meta_species_summary.py", "--data-dir", "public/data"],
        check=True,
    )


def fetch_arlington() -> dict[str, Any]:
    layer_info = fetch_json(ARLINGTON_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{ARLINGTON_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        ARLINGTON_TREES_LAYER,
        "1=1",
        ["OBJECTID", "ID", "CommonName", "CultivarVariety", "Ownership", "Jurisdiction"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Arlington")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CultivarVariety"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = (
            clean_display_name(attrs.get("Jurisdiction"))
            or clean_display_name(attrs.get("Ownership"))
            or "Arlington County"
        )
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"arlington-{attrs.get('ID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Arlington",
                "source_dataset": "DPR Trees",
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
                    "city": "Arlington",
                    "source_dataset": "DPR Trees",
                    "source_department": "Arlington County",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Arlington",
        "region": "va",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "DPR Trees",
            "city": "Arlington",
            "endpoint": ARLINGTON_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from Arlington County's official public DPR Trees layer using the official county jurisdiction boundary.",
        },
    }


def fetch_boston() -> dict[str, Any]:
    payload = load_remote_geojson(BOSTON_TREES_GEOJSON)
    features = payload.get("features", [])
    zip_index = fetch_us_city_zip_index("Boston")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates") or []
        if len(coordinates) != 2:
            continue
        lon, lat = coordinates

        common_name = clean_common_name(attrs.get("spp_com"))
        scientific_raw = format_scientific_display_name(attrs.get("spp_bot"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Boston"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"boston-{attrs.get('id') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Boston",
                "source_dataset": "BPRD Trees",
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
                    "city": "Boston",
                    "source_dataset": "BPRD Trees",
                    "source_department": "Boston Parks and Recreation Department",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Boston",
        "region": "ma",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "BPRD Trees",
            "city": "Boston",
            "endpoint": BOSTON_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": len(features),
            "records_included": len(output_features),
            "note": "Integrated from the official Analyze Boston BPRD Trees download, which includes both street and park trees.",
        },
    }


def fetch_baltimore() -> dict[str, Any]:
    layer_info = fetch_json(BALTIMORE_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{BALTIMORE_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        BALTIMORE_TREES_LAYER,
        "SPP LIKE 'Prunus%' OR SPP LIKE 'Malus%' OR SPP LIKE 'Magnolia%'",
        ["OBJECTID", "ID", "UniqueID", "Address", "Street", "SPP", "CULTIVAR", "CONDITION", "DBH"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Baltimore")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        common_name = None
        scientific_raw = format_scientific_display_name(attrs.get("SPP"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CULTIVAR"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = "City of Baltimore"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"baltimore-{attrs.get('UniqueID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Baltimore",
                "source_dataset": "Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
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
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Baltimore",
                    "source_dataset": "Trees",
                    "source_department": "Baltimore City Forestry",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Baltimore",
        "region": "md",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees",
            "city": "Baltimore",
            "endpoint": BALTIMORE_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official Baltimore city forestry ArcGIS tree layer on gis.baltimorecity.gov.",
        },
    }


def fetch_jersey_city() -> dict[str, Any]:
    layer_info = fetch_json(JERSEY_CITY_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{JERSEY_CITY_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        JERSEY_CITY_TREES_LAYER,
        "1=1",
        ["FID", "site_id", "species", "species_1", "species_1_", "site_comme", "condition", "address"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index("Jersey City")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        species_text = attrs.get("species") or attrs.get("species_1")
        scientific_raw, common_name = parse_species_text(species_text)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("species_1_"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = "City of Jersey City"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"jersey-city-{attrs.get('site_id') or attrs.get('FID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Jersey City",
                "source_dataset": "City of Jersey City Tree Inventory",
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
                    "city": "Jersey City",
                    "source_dataset": "City of Jersey City Tree Inventory",
                    "source_department": "City of Jersey City",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Jersey City",
        "region": "nj",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "City of Jersey City Tree Inventory",
            "city": "Jersey City",
            "endpoint": JERSEY_CITY_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the public Jersey City Tree Inventory service referenced by the city's Urban Forests materials.",
        },
    }


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


def fetch_treeplotter_inventory(
    *,
    city: str,
    folder: str,
    landing_url: str,
    boundary_layer: str,
    dataset_page: str,
    source_note: str,
) -> dict[str, Any]:
    boundary_info = fetch_json(boundary_layer, {"f": "pjson"})
    zip_index = fetch_us_city_zip_index(city)
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    cookie_path = init_treeplotter_session(folder, landing_url)
    try:
        lookup_rows = retrieve_treeplotter_rows(
            folder,
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
        species_lookup: dict[Any, dict[str, str]] = {}
        for row in lookup_rows:
            pid = row["pid"]["val"]
            species_lookup[pid] = {
                "latin_name": row["latin_name"]["alias"] or row["latin_name"]["val"] or "",
                "common_name": row["common_name"]["alias"] or row["common_name"]["val"] or "",
                "cultivar": row["cultivar"]["alias"] or row["cultivar"]["val"] or "",
            }

        tree_rows = retrieve_treeplotter_rows(
            folder,
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

    source_last_edit_at = iso_from_epoch(boundary_info.get("editingInfo", {}).get("lastEditDate"))
    city_slug = slugify_token(city)
    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in tree_rows:
        geom_hex = row.get("geom", {}).get("val") or row.get("geom", {}).get("alias")
        point = decode_wkb_point_hex(geom_hex)
        if not point:
            continue
        lon, lat = web_mercator_to_lon_lat(*point)
        species_id = (
            row.get("species_latin", {}).get("val")
            or row.get("species_common", {}).get("val")
            or row.get("species_code", {}).get("val")
        )
        species_info = species_lookup.get(species_id, {})
        common_name = clean_display_name(species_info.get("common_name"))
        latin_name = species_info.get("latin_name") or ""
        scientific_raw = expand_abbreviated_botanical_name(latin_name, common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar_name = clean_display_name(species_info.get("cultivar"))
        if cultivar_name and not subtype_name:
            subtype_name = cultivar_name
        ownership_raw = "Not published in public inventory"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{city_slug}-{row.get('pid', {}).get('val')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
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
                    "city": city,
                    "source_dataset": "Tree Inventory",
                    "source_department": f"City of {city}",
                    "source_last_edit_at": source_last_edit_at,
                },
            }
        )

    return {
        "city": city,
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": city,
            "endpoint": dataset_page,
            "last_edit_at": source_last_edit_at,
            "records_fetched": len(tree_rows),
            "records_included": len(output_features),
            "note": source_note,
        },
    }


def fetch_treekeeper_rows(search_endpoint: str, grids_endpoint: str, uid: str, fac_id: int = 1) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary_payload = fetch_json(
        search_endpoint,
        {
            "method": "submitMapSearch",
            "uid": uid,
            "facID": fac_id,
            "searchCurrentSelection": "false",
            "returnFormat": "json",
        },
        method="POST",
        body={},
    )

    rows: list[dict[str, Any]] = []
    limit = 5000
    offset = 0
    total_rows = int(summary_payload.get("siteCount") or 0)
    while True:
        rows_payload = fetch_json(
            grids_endpoint,
            {
                "method": "getTreeKeeperGridOptionsData",
                "session_id": uid,
                "layer_id": fac_id,
                "gridType": "sites",
                "calls_search": "true",
                "limit": limit,
                "offset": offset,
                "stopCache": int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1000),
            },
            method="POST",
            body={"filters": "[]", "sorts": "[]"},
        )
        batch = rows_payload.get("data") or []
        if isinstance(batch, str):
            batch = json.loads(batch)
        if not batch:
            break
        rows.extend(batch)
        if total_rows and len(rows) >= total_rows:
            break
        if len(batch) < limit:
            break
        offset += limit

    return summary_payload if isinstance(summary_payload, dict) else {}, rows


def fetch_fremont() -> dict[str, Any]:
    return fetch_treeplotter_inventory(
        city="Fremont",
        folder="FremontCA",
        landing_url=FREMONT_TREEPLOTTER_URL,
        boundary_layer=FREMONT_BOUNDARY_LAYER,
        dataset_page=FREMONT_DATASET_PAGE,
        source_note="Integrated via public TreePlotter session + official species lookup table.",
    )


def fetch_concord() -> dict[str, Any]:
    return fetch_treeplotter_inventory(
        city="Concord",
        folder="ConcordCA",
        landing_url=CONCORD_TREEPLOTTER_URL,
        boundary_layer=CONCORD_BOUNDARY_LAYER,
        dataset_page=CONCORD_DATASET_PAGE,
        source_note="Integrated via the official Concord TreePlotter page and city GIS boundary.",
    )


def fetch_south_san_francisco() -> dict[str, Any]:
    _boundary_info = fetch_json(SOUTH_SF_BOUNDARY_LAYER, {"f": "pjson"})
    summary_payload, rows = fetch_treekeeper_rows(
        SOUTH_SF_SEARCH_ENDPOINT,
        SOUTH_SF_GRIDS_ENDPOINT,
        uid="pinkhunter-south-san-francisco",
        fac_id=1,
    )
    zip_index = fetch_us_city_zip_index("South San Francisco")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon, lat = coordinates[0], coordinates[1]
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR1"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = clean_display_name(row.get("SITE_ATTR23")) or "City of South San Francisco"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"south-san-francisco-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "South San Francisco",
                "source_dataset": "TreeKeeper Inventory",
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
                    "city": "South San Francisco",
                    "source_dataset": "TreeKeeper Inventory",
                    "source_department": "City of South San Francisco",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "South San Francisco",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "TreeKeeper Inventory",
            "city": "South San Francisco",
            "endpoint": SOUTH_SF_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": len(rows),
            "records_included": len(output_features),
            "note": "Integrated from the official public TreeKeeper inventory linked from the city's Trees page.",
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


def fetch_pittsburgh() -> dict[str, Any]:
    summary_payload, rows = fetch_treekeeper_rows(
        PITTSBURGH_SEARCH_ENDPOINT,
        PITTSBURGH_GRIDS_ENDPOINT,
        uid="pinkhunter-pittsburgh",
        fac_id=1,
    )
    zip_index = fetch_us_city_zip_index("Pittsburgh")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon, lat = coordinates[0], coordinates[1]
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR6"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Pittsburgh"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"pittsburgh-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Pittsburgh",
                "source_dataset": "TreeKeeper Inventory",
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
                    "city": "Pittsburgh",
                    "source_dataset": "TreeKeeper Inventory",
                    "source_department": "City of Pittsburgh",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Pittsburgh",
        "region": "pa",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "TreeKeeper Inventory",
            "city": "Pittsburgh",
            "endpoint": PITTSBURGH_BASE,
            "last_edit_at": "",
            "records_fetched": int(summary_payload.get("siteCount") or len(rows)),
            "records_included": len(output_features),
            "note": "Integrated from the official public Pittsburgh TreeKeeper inventory domain.",
        },
    }


def fetch_new_york_city() -> dict[str, Any]:
    metadata = fetch_json(NYC_METADATA)
    rows = fetch_soda_rows(
        NYC_DATASET,
        where="status='Alive' AND (lower(spc_latin) like 'prunus%' OR lower(spc_latin) like 'malus%' OR lower(spc_latin) like 'magnolia%')",
        order="tree_id",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch(metadata.get("rowsUpdatedAt") or metadata.get("viewLastModified"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        try:
            lon = float(row.get("longitude"))
            lat = float(row.get("latitude"))
        except (TypeError, ValueError):
            continue

        common_name = clean_common_name(row.get("spc_common"))
        scientific_raw = format_scientific_display_name(row.get("spc_latin"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "New York City Department of Parks & Recreation"
        zip_code = (row.get("zipcode") or "").strip() or None
        row_id = f"new-york-city-{row.get('tree_id')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "New York City",
                "source_dataset": "2015 Street Tree Census - Tree Data",
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
                    "city": "New York City",
                    "source_dataset": "2015 Street Tree Census - Tree Data",
                    "source_department": "Department of Parks & Recreation (DPR)",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "New York City",
        "region": "ny",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "2015 Street Tree Census - Tree Data",
            "city": "New York City",
            "endpoint": NYC_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": fetch_soda_count(NYC_DATASET, where="status='Alive'"),
            "records_included": len(output_features),
            "note": "Integrated from the official NYC Open Data street tree census dataset published by NYC Parks.",
        },
    }


def fetch_philadelphia() -> dict[str, Any]:
    layer_info = fetch_json(PHILADELPHIA_LAYER, {"f": "pjson"})
    rows = fetch_all_features(
        PHILADELPHIA_LAYER,
        "tree_name LIKE 'PRUNUS%' OR tree_name LIKE 'MALUS%' OR tree_name LIKE 'MAGNOLIA%'",
        ["objectid", "tree_name", "year"],
        "objectid",
    )
    total_payload = fetch_json(
        f"{PHILADELPHIA_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    zip_index = fetch_us_city_zip_index("Philadelphia")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in rows:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue
        scientific_raw, common_name = parse_dash_species(attrs.get("tree_name"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Philadelphia Parks & Recreation"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"philadelphia-{attrs.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Philadelphia",
                "source_dataset": "PPR Tree Inventory 2025",
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
                    "city": "Philadelphia",
                    "source_dataset": "PPR Tree Inventory 2025",
                    "source_department": "Philadelphia Parks & Recreation",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Philadelphia",
        "region": "pa",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "PPR Tree Inventory 2025",
            "city": "Philadelphia",
            "endpoint": PHILADELPHIA_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(rows)),
            "records_included": len(output_features),
            "note": "Integrated from the official Philadelphia Parks & Recreation tree inventory layer.",
        },
    }


def fetch_cambridge() -> dict[str, Any]:
    reader, _prj_text = load_zipped_shapefile(CAMBRIDGE_STREET_TREES_ZIP)
    total_records = len(reader)
    point_rows = load_zipped_point_shapefile_rows(CAMBRIDGE_STREET_TREES_ZIP)
    zip_index = fetch_us_city_zip_index("Cambridge")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in point_rows:
        attrs = row.get("attributes", {})
        geom = row.get("geometry", {})
        if (attrs.get("SiteType") or "").strip() != "Tree":
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = format_scientific_display_name(attrs.get("Scientific"), common_name)
        if not scientific_raw:
            scientific_raw = format_scientific_display_name(attrs.get("Genus"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("Cultivar"))
        if not subtype_name and cultivar:
            subtype_name = cultivar
        ownership_raw = clean_display_name(attrs.get("Ownership")) or "City of Cambridge"
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"cambridge-{attrs.get('TreeID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Cambridge",
                "source_dataset": "Street Trees",
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
                    "city": "Cambridge",
                    "source_dataset": "Street Trees",
                    "source_department": "City of Cambridge GIS",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Cambridge",
        "region": "ma",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Trees",
            "city": "Cambridge",
            "endpoint": CAMBRIDGE_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of Cambridge street-tree shapefile download.",
        },
    }


def fetch_ottawa() -> dict[str, Any]:
    layer_info = fetch_json(OTTAWA_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{OTTAWA_TREES_LAYER}/query",
        {"where": OTTAWA_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        OTTAWA_TREES_LAYER,
        OTTAWA_BLOSSOM_WHERE,
        ["OBJECTID", "TREEID", "SPECIES", "OWNERSHIP", "STATUS", "PROGRAM", "TREATMENT"],
        "OBJECTID",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue
        common_name = clean_common_name(attrs.get("SPECIES"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = clean_display_name(attrs.get("OWNERSHIP")) or "City of Ottawa"
        row_id = f"ottawa-{attrs.get('TREEID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Ottawa",
                "source_dataset": "Tree Inventory / Inventaire des arbres",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
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
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Ottawa",
                    "source_dataset": "Tree Inventory / Inventaire des arbres",
                    "source_department": "City of Ottawa",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Ottawa",
        "region": "on",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory / Inventaire des arbres",
            "city": "Ottawa",
            "endpoint": OTTAWA_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Ottawa Tree Inventory ArcGIS layer and official city boundary.",
        },
    }


def fetch_toronto() -> dict[str, Any]:
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    total_records = 0
    for row in iter_remote_csv_rows(TORONTO_STREET_TREE_ALT_CSV):
        total_records += 1
        lon, lat = parse_point_geometry_text(row.get("geometry"))
        if lon is None or lat is None:
            continue
        common_name = clean_common_name(row.get("COMMON_NAME"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Toronto"
        row_id = f"toronto-{row.get('_id') or row.get('OBJECTID') or total_records}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Toronto",
                "source_dataset": "Street Tree Data",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
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
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Toronto",
                    "source_dataset": "Street Tree Data",
                    "source_department": "City of Toronto Urban Forestry",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Toronto",
        "region": "on",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Tree Data",
            "city": "Toronto",
            "endpoint": TORONTO_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of Toronto Street Tree Data CSV and official municipal boundary.",
        },
    }


def fetch_montreal() -> dict[str, Any]:
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    total_records = 0
    for row in iter_remote_csv_rows(MONTREAL_TREES_CSV):
        total_records += 1
        lon_raw = row.get("Longitude")
        lat_raw = row.get("Latitude")
        if lon_raw in (None, "") or lat_raw in (None, ""):
            continue
        lon = float(lon_raw)
        lat = float(lat_raw)
        common_name = clean_common_name(row.get("Essence_ang") or row.get("Essence_fr"))
        scientific_raw = format_scientific_display_name(row.get("Essence_latin"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Ville de Montréal"
        row_id = f"montreal-{total_records}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Montreal",
                "source_dataset": "Arbres publics sur le territoire de la Ville",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
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
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Montreal",
                    "source_dataset": "Arbres publics sur le territoire de la Ville",
                    "source_department": "Ville de Montréal",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Montreal",
        "region": "qc",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Arbres publics sur le territoire de la Ville",
            "city": "Montreal",
            "endpoint": MONTREAL_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official Ville de Montréal public-trees consolidated CSV and arrondissement-derived city boundary.",
        },
    }


def fetch_new_westminster() -> dict[str, Any]:
    layer_info = fetch_json(NEW_WESTMINSTER_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{NEW_WESTMINSTER_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        NEW_WESTMINSTER_TREES_LAYER,
        "1=1",
        ["objectid", "ADDRESS", "MAINTBY", "OWNEDBY", "SPECIES", "CULTIVAR", "GENUS", "FULL_NAME"],
        "objectid",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        scientific_raw = format_scientific_display_name(attrs.get("FULL_NAME"))
        if not scientific_raw:
            genus = clean_display_name(attrs.get("GENUS")) or ""
            species = clean_display_name(attrs.get("SPECIES")) or ""
            scientific_raw = format_scientific_display_name(" ".join(part for part in [genus, species] if part))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, None, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CULTIVAR"))
        if not subtype_name and cultivar:
            subtype_name = cultivar
        ownership_raw = clean_display_name(attrs.get("OWNEDBY")) or clean_display_name(attrs.get("MAINTBY")) or "City of New Westminster"
        row_id = f"new-westminster-{attrs.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "New Westminster",
                "source_dataset": "Tree Inventory (Active Trees)",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
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
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "New Westminster",
                    "source_dataset": "Tree Inventory (Active Trees)",
                    "source_department": "City of New Westminster",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "New Westminster",
        "region": "bc",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory (Active Trees)",
            "city": "New Westminster",
            "endpoint": NEW_WESTMINSTER_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of New Westminster Tree Inventory ArcGIS layer and official Metro Vancouver administrative boundary.",
        },
    }


CITY_FETCHERS = {
    "Arlington": fetch_arlington,
    "Baltimore": fetch_baltimore,
    "Boston": fetch_boston,
    "Jersey City": fetch_jersey_city,
    "Milpitas": fetch_milpitas,
    "San Mateo": fetch_san_mateo,
    "San Rafael": fetch_san_rafael,
    "Fremont": fetch_fremont,
    "Salinas": fetch_salinas,
    "Concord": fetch_concord,
    "South San Francisco": fetch_south_san_francisco,
    "Pittsburgh": fetch_pittsburgh,
    "New York City": fetch_new_york_city,
    "Philadelphia": fetch_philadelphia,
    "Cambridge": fetch_cambridge,
    "Ottawa": fetch_ottawa,
    "Toronto": fetch_toronto,
    "Montreal": fetch_montreal,
    "New Westminster": fetch_new_westminster,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish targeted city updates into existing city-split public data.")
    parser.add_argument("--city", action="append", choices=SUPPORTED_CITIES, help="City to refresh. Repeat for multiple cities.")
    args = parser.parse_args()

    target_cities = args.city or list(SUPPORTED_CITIES)
    results = [CITY_FETCHERS[city]() for city in target_cities]
    target_regions = {result["region"] for result in results}

    current_rows = load_normalized_rows()
    remaining_rows = [row for row in current_rows if row.get("city") not in target_cities]
    next_rows = remaining_rows[:]

    for result in results:
        write_city_geojson(result["region"], result["city"], result["features"])
        next_rows.extend(result["normalized_rows"])

    write_normalized_rows(next_rows)
    meta = load_meta()
    meta["generated_at"] = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    ensure_region_entries(meta, target_regions)
    save_meta(meta)
    refresh_publish_indexes(target_regions)

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
    meta["included_records"] = sum(int(region.get("tree_count", 0)) for region in meta.get("regions", []))
    meta["unknown_records"] = sum(item["count"] for item in unknown_items)
    save_meta(meta)
    subprocess.run(["python3", "scripts/check_region_data_sizes.py", "--data-dir", "public/data"], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
