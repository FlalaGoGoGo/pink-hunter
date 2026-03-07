# Public Data Interfaces

## `GET /data/trees.v1.geojson`
Deprecated monolithic tree file. Public publishing now uses regional tree files instead.

## `GET /data/trees.<region>.v2.geojson`
GeoJSON `FeatureCollection` of tree points for one region.

### Supported regions
- `wa`
- `ca`
- `or`
- `dc`
- `bc`

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

### `regions[]`
- `id`
- `label`
- `available`
- `bounds`
- `data_path`
- `tree_count`
- `city_count`
- `cities`
- `raw_bytes`
- `gzip_bytes`
- `warning_level`

## `GET /assets/ui/manifest.v1.json`
Asset manifest with expected dimensions and target formats.
