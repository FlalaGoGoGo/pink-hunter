# Deployment Topology

## Canonical Workspace Model
- Development happens only in `/Users/zhangziling/Documents/Project-Pink-Hunter`.
- `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter` is a generated export mirror.
- Local backup retention is reduced to one compressed archive outside the repo.

## Release Paths
- GitHub Pages
  - Source of truth: `main` in `FlalaGoGoGo/pink-hunter`
  - Delivery path: GitHub export sync -> push -> Pages workflow -> `https://pinkhunter.flalaz.com`
- AWS
  - Source of truth: same workspace and same `public/data` artifacts
  - Delivery path: local gate checks -> S3 sync -> CloudFront invalidation -> smoke check

## Launch Sensitivity
- Under traffic spikes, the first likely bottlenecks are third-party counter or basemap providers, not the static site host itself.
- Counter failure should be non-blocking, and map-provider assumptions should be reviewed before publicity pushes.

## Data Model
- Tree data: `public/data/trees.<region>.area-index.v2.json` and area shard GeoJSON files
- Tree render tiles: `public/data/trees.render.v1.pmtiles` plus `public/data/trees.render.v1.json`
- Coverage data: `public/data/coverage.<region>.v1.geojson`
- Compatibility fallback: `public/data/coverage.v1.geojson`
- Predictions namespace: `public/data/predictions/*.v1.json`

## Storage Boundary
- `public/data` is the public distribution layer that can be pushed to GitHub Pages or an S3 data bucket.
- `data/`, ETL intermediates, and normalization outputs remain internal workspace material; moving the site to AWS does not remove the need to manage those local files deliberately.

## Runtime Loading
- Coverage loading is now configurable independently from runtime environment.
- GitHub Pages and AWS can both use `lazy_by_region`.
- Tree rendering can run in `pmtiles` mode, which moves point drawing to vector tiles while keeping shard GeoJSON as the detail fallback path.
- Large hotspot cities should target roughly `12 MiB raw` per shard for better perceived performance.
