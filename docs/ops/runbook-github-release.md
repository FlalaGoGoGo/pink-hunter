# Runbook: GitHub Release

## Purpose
- Push the current validated workspace into the GitHub export repo and trigger GitHub Pages deployment.

## Preferred Commands
```bash
./scripts/ops_runner.sh sync-release "Describe the release"
./scripts/ops_runner.sh deploy-pages "Describe the release"
```

## Rules
- The root workspace is the only development workspace.
- `GitHub/pink-hunter` is the only export mirror.
- Do not create local directory backups under `GitHub/`.
- Keep only one long-term compressed archive at `/Users/zhangziling/Documents/Project-Pink-Hunter-Archive/releases/pink-hunter-baseline-2026-03-cleanup.tar.gz`.

## Flow
1. Pass the size gate and local build.
2. Run `sync-release` or `deploy-pages`.
3. Confirm the export mirror is clean.
4. Confirm the production domain serves the newest asset build.
5. Refresh the single compressed archive if this release is the new rollback baseline.

## Policy
- Detailed export rules live in [GitHub Sync Policy](github-sync-policy.md).
