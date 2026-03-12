# Runbook: Full ETL

## Purpose
- Rebuild the canonical published dataset and the supporting metadata.

## Command
```bash
./scripts/ops_runner.sh full-etl
```

## Use This When
- Taxonomy rules changed
- Shared parsing logic changed
- Multiple regions changed at once
- Published metadata drifted beyond a safe targeted refresh

## Required Verification
- `python3 scripts/check_region_data_sizes.py --data-dir public/data`
- `npm run build`
- Spot-check `public/data/meta.v2.json`, `public/data/jump-index.v1.json`, and the changed shard files
