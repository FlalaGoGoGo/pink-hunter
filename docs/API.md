# Public Data Interfaces

## `GET /data/trees.v1.geojson`
GeoJSON `FeatureCollection` of tree points.

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

## `GET /data/meta.v1.json`
Dataset metadata and source refresh details.

## `GET /assets/ui/manifest.v1.json`
Asset manifest with expected dimensions and target formats.
