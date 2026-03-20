#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/olist/target"
DST_DIR="$ROOT_DIR/docs"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Source directory not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$DST_DIR"

# Keep docs as a real directory for GitHub Pages, not a symlink.
rsync -a --delete \
  --exclude 'dbt.log' \
  "$SRC_DIR/" "$DST_DIR/"

# Required for static hosting when paths contain directories that start with '_'.
touch "$DST_DIR/.nojekyll"

echo "Synced $SRC_DIR -> $DST_DIR"
