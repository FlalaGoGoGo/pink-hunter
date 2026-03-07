#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$ROOT_DIR/GitHub/pink-hunter"
COMMIT_MESSAGE="${1:-Sync latest local changes}"

if [ ! -d "$EXPORT_DIR/.git" ]; then
  echo "GitHub export repo not found at $EXPORT_DIR" >&2
  exit 1
fi

rm -rf "$EXPORT_DIR/data/tmp" "$EXPORT_DIR/data/normalized"

rsync -av --delete \
  --exclude '.git' \
  --exclude 'GitHub' \
  --exclude 'node_modules' \
  --exclude 'dist' \
  --exclude 'data/tmp' \
  --exclude 'data/normalized' \
  --exclude '.DS_Store' \
  --exclude '~$*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.tsbuildinfo' \
  "$ROOT_DIR"/ "$EXPORT_DIR"/

python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$EXPORT_DIR/public/data"

git -C "$EXPORT_DIR" add -A

if git -C "$EXPORT_DIR" diff --cached --quiet; then
  echo "No GitHub export changes to commit."
  exit 0
fi

git -C "$EXPORT_DIR" commit -m "$COMMIT_MESSAGE"
git -C "$EXPORT_DIR" push
