#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$ROOT_DIR/GitHub/pink-hunter"
ARCHIVE_DIR="/Users/zhangziling/Documents/Project-Pink-Hunter-Archive/releases"
ARCHIVE_PATH="$ARCHIVE_DIR/pink-hunter-baseline-2026-03-cleanup.tar.gz"
TMP_ARCHIVE="$(mktemp "${TMPDIR:-/tmp}/pink-hunter-baseline.XXXXXX.tar.gz")"

cleanup() {
  rm -f "$TMP_ARCHIVE"
}

trap cleanup EXIT

if [ ! -d "$EXPORT_DIR" ]; then
  echo "Missing export repo at $EXPORT_DIR" >&2
  exit 1
fi

mkdir -p "$ARCHIVE_DIR"
find "$ARCHIVE_DIR" -mindepth 1 -maxdepth 1 -type f ! -name "$(basename "$ARCHIVE_PATH")" -delete

tar -C "$(dirname "$EXPORT_DIR")" \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='data/normalized' \
  --exclude='data/tmp' \
  --exclude='.DS_Store' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  -czf "$TMP_ARCHIVE" \
  "$(basename "$EXPORT_DIR")"

mv "$TMP_ARCHIVE" "$ARCHIVE_PATH"
echo "Updated baseline archive: $ARCHIVE_PATH"
