#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$ROOT_DIR/GitHub/pink-hunter"
COMMIT_MESSAGE="${1:-Sync latest local changes}"
REMOTE_URL="https://github.com/FlalaGoGoGo/pink-hunter.git"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pink-hunter-sync.XXXXXX")"
TMP_REPO="$TMP_DIR/repo"

cleanup() {
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT

if [ -d "$EXPORT_DIR/.git" ]; then
  EXISTING_REMOTE="$(git -C "$EXPORT_DIR" remote get-url origin 2>/dev/null || true)"
  if [ -n "$EXISTING_REMOTE" ]; then
    REMOTE_URL="$EXISTING_REMOTE"
  fi
fi

git clone --depth 1 "$REMOTE_URL" "$TMP_REPO" >&2

rm -rf "$TMP_REPO/data/tmp" "$TMP_REPO/data/normalized"

find "$TMP_REPO" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

tar -C "$ROOT_DIR" \
  --exclude='.git' \
  --exclude='GitHub' \
  --exclude='node_modules' \
  --exclude='dist' \
  --exclude='data/tmp' \
  --exclude='data/normalized' \
  --exclude='.DS_Store' \
  --exclude='~$*' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.tsbuildinfo' \
  -cf - . | tar -C "$TMP_REPO" -xf -

python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$TMP_REPO/public/data"

git -C "$TMP_REPO" add -A

if git -C "$TMP_REPO" diff --cached --quiet; then
  echo "No GitHub export changes to commit."
  rm -rf "$EXPORT_DIR"
  mkdir -p "$(dirname "$EXPORT_DIR")"
  mv "$TMP_REPO" "$EXPORT_DIR"
  exit 0
fi

git -C "$TMP_REPO" commit -m "$COMMIT_MESSAGE"
git -C "$TMP_REPO" -c pack.windowMemory=100m -c pack.packSizeLimit=100m -c pack.threads=1 push origin main

rm -rf "$EXPORT_DIR"
mkdir -p "$(dirname "$EXPORT_DIR")"
mv "$TMP_REPO" "$EXPORT_DIR"
