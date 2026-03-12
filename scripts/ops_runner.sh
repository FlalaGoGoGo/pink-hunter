#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKLIST_PATH="$ROOT_DIR/docs/ops/release-checklist.md"

print_usage() {
  cat <<'EOF'
Pink Hunter ops runner

Usage:
  ./scripts/ops_runner.sh <command> [args...]

Commands:
  prebuild-boundaries   Run official boundary prebuild for a state/province
  publish-city          Publish targeted city updates
  full-etl              Run the canonical ETL flow
  refresh-shards        Refresh area shard artifacts
  refresh-render-tiles  Rebuild PMTiles render artifacts
  sync-release          Sync, commit, and push the GitHub export repo
  deploy-pages          Sync release for GitHub Pages and smoke-check production
  deploy-aws            Publish the current build to AWS
  smoke-check           Smoke-check a deployed site
  archive-baseline      Refresh the single local compressed baseline archive
EOF
}

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "$command_name is required." >&2
    exit 1
  fi
}

announce_checklist() {
  echo "Review checklist before continuing: $CHECKLIST_PATH"
}

run_sync_release() {
  local commit_message="${1:-Sync latest product changes}"
  "$ROOT_DIR/scripts/sync_github_export.sh" "$commit_message"
}

run_smoke_check() {
  require_command python3
  python3 "$ROOT_DIR/scripts/smoke_check_deployment.py" "$@"
}

command_name="${1:-}"
if [ -z "$command_name" ]; then
  print_usage
  exit 1
fi
shift || true

announce_checklist

case "$command_name" in
  prebuild-boundaries)
    require_command python3
    python3 "$ROOT_DIR/scripts/prebuild_state_boundaries.py" "$@"
    ;;
  publish-city)
    require_command python3
    python3 "$ROOT_DIR/scripts/publish_targeted_city_updates.py" "$@"
    python3 "$ROOT_DIR/scripts/build_tree_render_tiles.py" --data-dir "$ROOT_DIR/public/data"
    python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$ROOT_DIR/public/data"
    ;;
  full-etl)
    require_command npm
    (
      cd "$ROOT_DIR"
      npm run etl
    )
    python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$ROOT_DIR/public/data"
    ;;
  refresh-shards)
    require_command python3
    python3 "$ROOT_DIR/scripts/refresh_region_area_shards.py" "$@"
    python3 "$ROOT_DIR/scripts/build_tree_render_tiles.py" --data-dir "$ROOT_DIR/public/data"
    python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$ROOT_DIR/public/data"
    ;;
  refresh-render-tiles)
    require_command python3
    python3 "$ROOT_DIR/scripts/build_tree_render_tiles.py" --data-dir "$ROOT_DIR/public/data"
    ;;
  sync-release)
    run_sync_release "$@"
    ;;
  deploy-pages)
    run_sync_release "${1:-Deploy latest GitHub Pages release}"
    run_smoke_check --site-url "https://pinkhunter.flalaz.com" --insecure
    ;;
  deploy-aws)
    require_command bash
    "$ROOT_DIR/scripts/publish_to_aws.sh" "$@"
    ;;
  smoke-check)
    run_smoke_check "$@"
    ;;
  archive-baseline)
    require_command bash
    "$ROOT_DIR/scripts/archive_release_baseline.sh"
    ;;
  *)
    print_usage
    exit 1
    ;;
esac
