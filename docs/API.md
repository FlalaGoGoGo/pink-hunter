# Public Data Interfaces

## `GET /data/trees.<region>.area-index.v2.json`
Published area-shard index for one region.

### Supported regions
- `wa`
- `ca`
- `or`
- `dc`
- `bc`
- `va`
- `md`
- `nj`
- `ny`
- `pa`
- `ma`
- `on`
- `qc`

### Shape
- `generated_at`
- `region`
- `strategy: "area_shard"`
- `items[]`
  - `jurisdiction`
  - `slug`
  - `display_name`
  - `jurisdiction_type`
  - `state_province`
  - `country`
  - `bounds`
  - `tree_count`
  - `zip_codes[]`
  - `species_counts`
  - `ownership_groups[]`
  - `shards[]`
    - `id`
    - `bounds`
    - `data_path`
    - `tree_count`
    - `raw_bytes`
    - `gzip_bytes`

## `GET /data/trees.<region>.area.<slug>.v2.geojson`
GeoJSON `FeatureCollection` for a single-area shard when the area fits in one published file.

## `GET /data/trees.<region>.area.<slug>.shard-###.v2.geojson`
GeoJSON `FeatureCollection` for one shard of a larger area.

### `feature.properties`
- `id: string`
- `species_group: "cherry" | "plum" | "peach" | "magnolia" | "crabapple"`
- `scientific_name: string`
- `common_name: string | null`
- `subtype_name: string | null`
- `zip_code: string | null`
- `ownership: "public" | "private" | "unknown"`
- `ownership_raw: string`
- `city: string`
- `source_dataset: string`
- `source_department: string`
- `source_last_edit_at: ISO8601 string`

## `GET /data/coverage.v1.geojson`
GeoJSON `FeatureCollection` for coverage overlays.

### `feature.properties`
- `id: string`
- `status: "covered" | "official_unavailable"`
- `jurisdiction: string`
- `note: string`

## `GET /data/species-guide.v1.json`
Bilingual species education content.

## `GET /data/meta.v2.json`
Dataset metadata and source refresh details.

### Top-level fields
- `included_records`
- `species_counts`
  - `cherry`
  - `plum`
  - `peach`
  - `magnolia`
  - `crabapple`
- `areas[]`
  - `jurisdiction`
  - `region`
  - `tree_count`
  - `species_counts`
    - `cherry`
    - `plum`
    - `peach`
    - `magnolia`
    - `crabapple`

### `regions[]`
- `id`
- `label`
- `available`
- `bounds`
- `data_path?`
- `tree_count`
- `city_count`
- `cities`
- `species_counts`
  - `cherry`
  - `plum`
  - `peach`
  - `magnolia`
  - `crabapple`
- `raw_bytes`
- `gzip_bytes`
- `warning_level` (largest shard publish risk for this region)
- `aggregate_raw_bytes`
- `aggregate_gzip_bytes`
- `aggregate_warning_level` (`none | watch | large | very_large`; advisory only)
- `largest_shard_raw_bytes`
- `largest_shard_gzip_bytes`
- `largest_shard_area`
- `largest_shard_warning_level`
- `area_split`
  - `strategy`
  - `index_path`
  - `area_count`
  - `shard_count`
  - `ready`

## `GET /assets/ui/manifest.v1.json`
Asset manifest with expected dimensions and target formats.
