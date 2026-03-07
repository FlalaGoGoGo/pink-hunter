# GitHub Sync Policy

Last updated: 2026-03-06 (America/Los_Angeles)

## Hard Rule
- Every accepted change to product code, ETL logic, public data, docs, or assets must be reflected in both:
  - the local working project at `/Users/zhangziling/Documents/Project-Pink-Hunter`
  - the GitHub export repo at `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`
- After the GitHub export repo is updated, the change must be committed and pushed to `https://github.com/FlalaGoGoGo/pink-hunter`.

## Required Workflow
1. Make and verify the local change first.
2. Rebuild or refresh any published data artifacts that changed.
3. Run the region size check and ensure no published region file reaches the hard-fail threshold.
4. Sync the project into the GitHub export repo.
5. Commit the GitHub export repo.
6. Push the GitHub export repo to GitHub.

## Canonical Helper
- Preferred sync helper: `scripts/sync_github_export.sh`
- Example:
  - `./scripts/sync_github_export.sh "Sync latest product changes"`

## Notes
- The GitHub export repo intentionally excludes local-only build caches such as `node_modules/`, `dist/`, `.DS_Store`, and `*.tsbuildinfo`.
- Public tree data is published as regional files such as `public/data/trees.wa.v2.geojson`, not as one global `trees.v1.geojson`.
- Every publish flow must pass `scripts/check_region_data_sizes.py`.
- Size thresholds are hard rules for published region files:
  - `warning`: `>= 35 MiB raw`
  - `high_warning`: `>= 45 MiB raw`
  - `hard_fail`: `>= 50 MiB raw`
- Any region that reaches warning level must be reviewed for the next split step before additional expansion work continues.
- Keep `public/CNAME` synchronized because the production custom domain is `pinkhunter.flalaz.com`.
