# Methodology And Pitfalls

## What To Review Before Repeating A Workflow
- The relevant ops runbook
- `city-coverage-tracker.md` first, using the `A1 / A2 / B / C` buckets to decide whether the task is publish, unblock, or research work
- `city-etl-methods.md`
- `factory-expansion-roadmap.md` when planning a new state, province, or prediction pilot
- This file

## Repeated Lessons
- The main source of local chaos was not missing logic; it was duplicated workspaces, duplicated backups, and duplicated intermediate files.
- Official boundary reuse is a force multiplier. Prebuild the boundary layer first, then activate cities on top of it.
- Size gates protect GitHub risk, but product performance also depends on shard granularity. Hotspot cities need tighter shard targets.
- Lazy loading alone is not enough once the browser keeps merging and re-uploading large GeoJSON sources. The stronger path is PMTiles or vector-tile rendering with GeoJSON reserved for detail fallback.
- When PMTiles is active, counts and filter availability should come from shard-level summary fields in the area index, not from loading viewport shards just to count them.
- When PMTiles is active, click-to-detail should carry the exact shard `data_path` whenever possible, so detail fallback can load one shard first instead of sweeping a whole city.
- Methods are only reusable if they are written down in docs immediately after they work.

## Historical Thread Additions
- Region lazy loading for large states or provinces needs two safeguards:
  - overview bounds must match the user-facing state or province footprint, not only the current covered-city geometry
  - the frontend should keep the active region loadable even if the viewport drifts outside that computed footprint
- PDF campus maps and similar guides are validation assets, not canonical row-level datasets. Use them to QA boundaries, hotspot placement, and cultivar labels.
- Launch-facing experiments should ship the smallest public value first: stronger detail fields, clear `start / peak / end` markers, and a lightweight weather tie-in before broader ML claims.
- Visitor counting must degrade gracefully and respect `Do Not Track` / `Global Privacy Control`; counter failure is acceptable, map failure is not.

## Discovery Rules
- Expansion priority is fixed:
  - `A2` first
  - then `B`
  - then `C`
- After one official source works in a new geography, search sideways before searching broadly:
  - same ArcGIS org or contractor org
  - same TreeKeeper or TreePlotter tenancy
  - shared county or metro layers with a `City` or `Jurisdiction` field
- Batch expansion usually comes from schema reuse, not from discovering ten unrelated cities one by one.

## Publish Integrity Rules
- Treat `area-index`, coverage files, `meta.v2.json`, and the matching area or shard GeoJSON files as one publish contract. If one moves without the others, Pages failures or silent city loss follow.
- Treat `trees.render.v1.pmtiles` and `trees.render.v1.json` as part of the same publish contract whenever tree shards change.
- Finder copy artifacts such as `* 2*` are not harmless clutter. Refresh scripts ignore those names and can shrink a region index without an obvious code error.
- If total tree counts suddenly drop, inspect published artifacts first before rewriting fetchers:
  - compare `meta.v2.json`
  - compare the relevant `trees.<region>.area-index.v2.json`
  - look for missing or stale shard files

## Capture Rules
- New source family or parser rule: update `city-etl-methods.md`
- New inclusion or exclusion decision: update `city-coverage-tracker.md`
- New workflow or failure mode: update this file or the relevant runbook

## Known Pitfalls
- `GitHub/` backup folders silently consume most local disk space.
- `data/normalized/`, `data/tmp/`, and copied `* 2*` files create false clutter and accidental sync drift.
- GitHub Pages can still feel slow if the runtime falls back to eager coverage loading or large single-city shards.
