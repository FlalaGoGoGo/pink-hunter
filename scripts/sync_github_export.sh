#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPORT_DIR="$ROOT_DIR/GitHub/pink-hunter"
COMMIT_MESSAGE="${1:-Sync latest local changes}"
REMOTE_URL="https://github.com/FlalaGoGoGo/pink-hunter.git"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pink-hunter-sync.XXXXXX")"
TMP_REPO="$TMP_DIR/repo"
NPM_INSTALL_FLAGS=("--no-fund" "--no-audit")

cleanup() {
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "$command_name is required." >&2
    exit 1
  fi
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

cleanup_export_repo() {
  local repo_dir="$1"
  rm -rf \
    "$repo_dir/node_modules" \
    "$repo_dir/dist" \
    "$repo_dir/data/normalized" \
    "$repo_dir/data/tmp"
  find "$repo_dir" \
    \( -name '.DS_Store' -o -name '__pycache__' -o -name '*.pyc' -o -name '*.tmp' -o -name '* 2*' \) \
    -print0 | xargs -0 rm -rf --
}

prune_export_siblings() {
  local github_dir="$ROOT_DIR/GitHub"
  local entry_name
  shopt -s nullglob
  for path in "$github_dir"/pink-hunter*; do
    entry_name="$(basename "$path")"
    if [ "$entry_name" = "pink-hunter" ]; then
      continue
    fi
    rm -rf "$path"
  done
  shopt -u nullglob
}

run_preflight_checks() {
  echo "Rebuilding PMTiles render artifacts..." >&2
  python3 "$ROOT_DIR/scripts/build_tree_render_tiles.py" --data-dir "$TMP_REPO/public/data"

  echo "Running shard consistency check..." >&2
  python3 "$ROOT_DIR/scripts/check_region_data_sizes.py" --data-dir "$TMP_REPO/public/data"

  echo "Installing dependencies in temp export repo..." >&2
  npm --prefix "$TMP_REPO" ci "${NPM_INSTALL_FLAGS[@]}"

  echo "Running TypeScript build gate with Node 20..." >&2
  (
    cd "$TMP_REPO"
    "${NODE20_RUNNER[@]}" node_modules/typescript/bin/tsc -b
  )

  echo "Running Vite production build gate with Node 20..." >&2
  (
    cd "$TMP_REPO"
    "${NODE20_RUNNER[@]}" node_modules/vite/bin/vite.js build
  )
}

require_command git
require_command npm
require_command python3
resolve_node20_runner

if [ -d "$EXPORT_DIR/.git" ]; then
  EXISTING_REMOTE="$(git -C "$EXPORT_DIR" remote get-url origin 2>/dev/null || true)"
  if [ -n "$EXISTING_REMOTE" ]; then
    REMOTE_URL="$EXISTING_REMOTE"
  fi
fi

git clone --depth 1 "$REMOTE_URL" "$TMP_REPO" >&2

cleanup_export_repo "$TMP_REPO"

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

git -C "$TMP_REPO" add -A

if git -C "$TMP_REPO" diff --cached --quiet; then
  echo "No GitHub export changes to commit."
  cleanup_export_repo "$TMP_REPO"
  rm -rf "$EXPORT_DIR"
  mkdir -p "$(dirname "$EXPORT_DIR")"
  prune_export_siblings
  mv "$TMP_REPO" "$EXPORT_DIR"
  exit 0
fi

run_preflight_checks

git -C "$TMP_REPO" commit -m "$COMMIT_MESSAGE"
git -C "$TMP_REPO" -c pack.windowMemory=100m -c pack.packSizeLimit=100m -c pack.threads=1 push origin main

cleanup_export_repo "$TMP_REPO"
rm -rf "$EXPORT_DIR"
mkdir -p "$(dirname "$EXPORT_DIR")"
prune_export_siblings
mv "$TMP_REPO" "$EXPORT_DIR"
