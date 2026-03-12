#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_command() {
  local command_name="$1"
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "$command_name is required." >&2
    exit 1
  }
}

resolve_node20_runner() {
  require_command node

  local node_major
  node_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || true)"
  if [ "$node_major" = "20" ]; then
    NODE20_RUNNER=(node)
    return
  fi

  require_command npx
  NODE20_RUNNER=(npx -y node@20)
}

require_command aws
require_command npm
require_command python3
resolve_node20_runner

: "${APP_BUCKET_NAME:?Set APP_BUCKET_NAME.}"
: "${DATA_BUCKET_NAME:?Set DATA_BUCKET_NAME.}"
: "${DISTRIBUTION_ID:?Set DISTRIBUTION_ID.}"

APP_CACHE_CONTROL_HTML="${APP_CACHE_CONTROL_HTML:-public,max-age=300,must-revalidate}"
APP_CACHE_CONTROL_ASSETS="${APP_CACHE_CONTROL_ASSETS:-public,max-age=31536000,immutable}"
DATA_CACHE_CONTROL="${DATA_CACHE_CONTROL:-public,max-age=86400,stale-while-revalidate=604800}"

pushd "$ROOT_DIR" >/dev/null
export VITE_TREE_RENDER_MODE="${VITE_TREE_RENDER_MODE:-pmtiles}"
python3 scripts/build_tree_render_tiles.py --data-dir public/data
python3 scripts/check_region_data_sizes.py --data-dir public/data
npm ci --no-fund --no-audit
"${NODE20_RUNNER[@]}" node_modules/typescript/bin/tsc -b
"${NODE20_RUNNER[@]}" node_modules/vite/bin/vite.js build

aws s3 sync dist/assets "s3://${APP_BUCKET_NAME}/assets/" \
  --delete \
  --cache-control "$APP_CACHE_CONTROL_ASSETS"

aws s3 sync dist "s3://${APP_BUCKET_NAME}/" \
  --delete \
  --exclude "assets/*" \
  --cache-control "$APP_CACHE_CONTROL_HTML"

aws s3 sync public/data "s3://${DATA_BUCKET_NAME}/data/" \
  --delete \
  --cache-control "$DATA_CACHE_CONTROL"

aws cloudfront create-invalidation \
  --distribution-id "$DISTRIBUTION_ID" \
  --paths "/" "/index.html" "/assets/*" "/data/*"
popd >/dev/null
