# Release Checklist

Review this checklist before any formal operation. `scripts/ops_runner.sh` prints this path on every run.

## Always
- Confirm the task scope and target environment.
- Review `docs/research/city-coverage-tracker.md` and confirm whether the target city is currently in `A1`, `A2`, `B`, or `C`.
- Confirm the working tree does not contain accidental `.DS_Store`, `__pycache__`, `*.tmp`, or copied `* 2*` files.
- Confirm only `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter` exists under `GitHub/`.
- Review the relevant runbook before running ETL, publishing, or deployment commands.

## Data And Build Gates
- Run `python3 scripts/check_region_data_sizes.py --data-dir public/data`.
- Run `npm run build` locally after product or runtime changes.
- If shard logic changed, rerun `python3 scripts/refresh_region_area_shards.py --data-dir public/data --region all`.
- If coverage metadata changed, rerun `python3 scripts/refresh_coverage_metadata.py --data-dir public/data`.

## Release Gates
- Use `./scripts/ops_runner.sh sync-release "<commit message>"` for GitHub Pages release sync.
- Use `./scripts/ops_runner.sh deploy-pages "<commit message>"` when you also want an immediate production smoke check.
- Use `./scripts/ops_runner.sh deploy-aws` only after the same size and build gates pass.
- Refresh the single baseline archive with `./scripts/ops_runner.sh archive-baseline` after a release you want to keep locally.

## Post Release
- Smoke-check `https://pinkhunter.flalaz.com`.
- For AWS work, smoke-check the target staging or production domain plus the visitor API if it changed.
- Confirm `GitHub/pink-hunter` is clean and does not contain `node_modules`, `dist`, `data/normalized`, or `data/tmp`.
