# GitHub Sync Policy

Last updated: 2026-03-06 (America/Los_Angeles)

## Hard Rule
- Every accepted change to product code, ETL logic, public data, docs, or assets must be reflected in both:
  - the local working project at `/Users/zhangziling/Documents/Project-Pink-Hunter`
  - the GitHub export repo at `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`
- After the GitHub export repo is updated, the change must be committed and pushed to `https://github.com/FlalaGoGoGo/pink-hunter`.
- For UI work specifically, the task is not complete until `https://pinkhunter.flalaz.com/` is checked and confirmed to be serving the latest version.

## Required Workflow
1. Make and verify the local change first.
2. Rebuild or refresh any published data artifacts that changed.
3. Run the shard consistency gate and ensure every published shard file referenced by metadata actually exists.
4. Run a clean dependency install in the export repo and pass the TypeScript + production build gates.
5. Sync the project into the GitHub export repo.
6. Commit the GitHub export repo.
7. Push the GitHub export repo to GitHub.
8. Confirm the production domain `https://pinkhunter.flalaz.com/` reflects the new build.

## Canonical Helper
- Preferred sync helper: `scripts/sync_github_export.sh`
- Example:
  - `./scripts/sync_github_export.sh "Sync latest product changes"`
- The helper must sync through a fresh temporary clone on every run, then replace the local export repo only after a successful push.
- The helper now blocks `push main` unless all of the following pass inside the fresh temp clone:
  - `python3 scripts/check_region_data_sizes.py --data-dir public/data`
  - `npm ci`
  - `tsc -b`
  - `vite build`
- On this machine, the helper forces the TypeScript and Vite build gates through `Node 20` when the default local `node` version is not `20`, because the current Vite toolchain is not stable under `Node 25`.
- Do not rely on a long-lived `.git/index` inside `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`; that was the source of repeated hangs and index corruption.

## Notes
- The GitHub export repo intentionally excludes local-only build caches such as `node_modules/`, `dist/`, `.DS_Store`, and `*.tsbuildinfo`.
- The GitHub export repo also excludes local-only ETL audit/intermediate outputs such as `data/normalized/` and `data/tmp/`.
- Public tree data is published by area + shard for every region:
  - `public/data/trees.<region>.area-index.v2.json`
  - `public/data/trees.<region>.area.<slug>.v2.geojson`
  - `public/data/trees.<region>.area.<slug>.shard-###.v2.geojson`
- Every publish flow must pass `scripts/check_region_data_sizes.py`, `tsc -b`, and `vite build`.
- If a full ETL rebuild is blocked but local region files are still current, refresh area-shard artifacts with `scripts/refresh_region_area_shards.py --data-dir public/data --region all` before sync/push.
- If coverage status lists or official-boundary hints changed without a full ETL rebuild, run `scripts/refresh_coverage_metadata.py --data-dir public/data` before sync/push.
- Size thresholds are hard rules for published shard files:
  - `target_split`: `>= 20 MiB raw`
  - `must_split`: `>= 25 MiB raw`
  - `hard_fail`: `>= 30 MiB raw`
- Aggregate region size is tracked as advisory only and does not count as a GitHub single-file risk.
- Keep `public/CNAME` synchronized because the production custom domain is `pinkhunter.flalaz.com`.
- If the local export repo ever becomes unhealthy, delete it and let the sync helper recreate it from a fresh clone rather than trying to recover the old git metadata.
