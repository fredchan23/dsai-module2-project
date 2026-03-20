#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SRC_DIR="$ROOT_DIR/olist/target"
DST_DIR="$ROOT_DIR/docs"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Source directory not found: $SRC_DIR" >&2
  exit 1
fi

# Safety guard: never allow syncing from repo root or current directory.
if [[ "$SRC_DIR" == "$ROOT_DIR" || "$SRC_DIR" == "." || "$SRC_DIR" == "./" || "$SRC_DIR" == "/" ]]; then
  echo "Refusing to sync from unsafe source path: $SRC_DIR" >&2
  exit 1
fi

if [[ ! -f "$SRC_DIR/index.html" || ! -f "$SRC_DIR/manifest.json" ]]; then
  echo "Expected dbt docs artifacts were not found in: $SRC_DIR" >&2
  echo "Run 'dbt docs generate' in olist/ first." >&2
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
