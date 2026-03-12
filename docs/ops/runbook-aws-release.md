# Runbook: AWS Release

## Purpose
- Publish the validated build and data artifacts to the AWS staging or production path.

## Command
```bash
./scripts/ops_runner.sh deploy-aws
```

## Requirements
- Required environment variables for buckets and distribution IDs must be set.
- `python3 scripts/check_region_data_sizes.py --data-dir public/data` must pass.
- The local build must pass under Node 20.

## Afterward
- Run `./scripts/ops_runner.sh smoke-check --site-url <site-url> --api-base-url <api-base-url>`
- Confirm the data and app buckets both serve the latest release
