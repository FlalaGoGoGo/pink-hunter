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
3. Run the region size check and ensure published city files stay below the hard-fail threshold and aggregate region payloads stay within warning policy.
4. Sync the project into the GitHub export repo.
5. Commit the GitHub export repo.
6. Push the GitHub export repo to GitHub.

## Canonical Helper
- Preferred sync helper: `scripts/sync_github_export.sh`
- Example:
  - `./scripts/sync_github_export.sh "Sync latest product changes"`

## Notes
- The GitHub export repo intentionally excludes local-only build caches such as `node_modules/`, `dist/`, `.DS_Store`, and `*.tsbuildinfo`.
- The GitHub export repo also excludes local-only ETL audit/intermediate outputs such as `data/normalized/` and `data/tmp/`.
- Public tree data is published by city for every region:
  - `public/data/trees.<region>.city-index.v1.json`
  - `public/data/trees.<region>.city.<slug>.v1.geojson`
- Every publish flow must pass `scripts/check_region_data_sizes.py`.
- If a full ETL rebuild is blocked but local region files are still current, refresh city-split artifacts with `scripts/refresh_region_city_splits.py --data-dir public/data --region all` before sync/push.
- If coverage status lists or official-boundary hints changed without a full ETL rebuild, run `scripts/refresh_coverage_metadata.py --data-dir public/data` before sync/push.
- Size thresholds are hard rules for published city files and planning thresholds for aggregate region payloads:
  - `warning`: `>= 35 MiB raw`
  - `high_warning`: `>= 45 MiB raw`
  - `hard_fail`: `>= 50 MiB raw`
- Any region that reaches warning level must be reviewed for the next split step before additional expansion work continues.
- Keep `public/CNAME` synchronized because the production custom domain is `pinkhunter.flalaz.com`.
