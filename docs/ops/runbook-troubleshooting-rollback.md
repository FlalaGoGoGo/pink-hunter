# Runbook: Troubleshooting And Rollback

## First Checks
- Read the latest release checklist.
- Confirm whether the issue is local-only, export-only, GitHub Pages, or AWS-specific.
- Confirm `GitHub/pink-hunter` is still the only export mirror.

## Common Failures
- Build failure: rerun `npm run build` and inspect the changed runtime or data file.
- Size gate failure: refresh shards and inspect the largest changed city payload.
- Export drift: rerun `./scripts/ops_runner.sh sync-release "<commit message>"`.
- Production mismatch: compare the latest deployed asset hash with the export repo build output.

## Rollback Order
1. Roll the GitHub export repo back to the last known good commit.
2. Re-push `main` to trigger GitHub Pages redeploy, or republish to AWS.
3. If local recovery is needed, restore from `/Users/zhangziling/Documents/Project-Pink-Hunter-Archive/releases/pink-hunter-baseline-2026-03-cleanup.tar.gz`.

## Archive Rule
- Do not create a new backup folder in `GitHub/`.
- Refresh the single baseline archive instead.
