#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-pink-hunter}"
VISIBILITY="${2:-public}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not installed. Install GitHub CLI first." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "origin already exists. Pushing current branch."
  git push -u origin main
  exit 0
fi

gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
