# GitHub Sync Policy

Last updated: 2026-03-06 (America/Los_Angeles)

## Hard Rule
- Every accepted change to product code, ETL logic, public data, docs, or assets must be reflected in both:
  - the local working project at `/Users/zhangziling/Documents/Project-Pink-Hunter`
  - the GitHub export repo at `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`
- After the GitHub export repo is updated, the change must be committed and pushed to `https://github.com/FlalaGoGoGo/pink-hunter`.

## Required Workflow
1. Make and verify the local change first.
2. Sync the project into the GitHub export repo.
3. Commit the GitHub export repo.
4. Push the GitHub export repo to GitHub.

## Canonical Helper
- Preferred sync helper: `scripts/sync_github_export.sh`
- Example:
  - `./scripts/sync_github_export.sh "Sync latest product changes"`

## Notes
- The GitHub export repo intentionally excludes local-only build caches such as `node_modules/`, `dist/`, `.DS_Store`, and `*.tsbuildinfo`.
- Keep `public/CNAME` synchronized because the production custom domain is `pinkhunter.flalaz.com`.
