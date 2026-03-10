#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v aws >/dev/null 2>&1 || {
  echo "aws CLI is required." >&2
  exit 1
}

: "${APP_BUCKET_NAME:?Set APP_BUCKET_NAME.}"
: "${DATA_BUCKET_NAME:?Set DATA_BUCKET_NAME.}"
: "${DISTRIBUTION_ID:?Set DISTRIBUTION_ID.}"

APP_CACHE_CONTROL_HTML="${APP_CACHE_CONTROL_HTML:-public,max-age=300,must-revalidate}"
APP_CACHE_CONTROL_ASSETS="${APP_CACHE_CONTROL_ASSETS:-public,max-age=31536000,immutable}"
DATA_CACHE_CONTROL="${DATA_CACHE_CONTROL:-public,max-age=86400,stale-while-revalidate=604800}"

pushd "$ROOT_DIR" >/dev/null
npm run build

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
