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

## Data Model
- Tree data: `public/data/trees.<region>.area-index.v2.json` and area shard GeoJSON files
- Coverage data: `public/data/coverage.<region>.v1.geojson`
- Compatibility fallback: `public/data/coverage.v1.geojson`
- Predictions namespace: `public/data/predictions/*.v1.json`

## Runtime Loading
- Coverage loading is now configurable independently from runtime environment.
- GitHub Pages and AWS can both use `lazy_by_region`.
- Large hotspot cities should target roughly `12 MiB raw` per shard for better perceived performance.
