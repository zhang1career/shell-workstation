#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Script Name: space-manager.sh
#
# Purpose:
#   Manage large directories (e.g. Xcode DerivedData)
#   by migrating them to external disks or cleaning them safely.
#
# Usage:
#   migrate <SOURCE> <TARGET>
#   clean   <SOURCE>
#
# Examples:
#   ./space-manager.sh migrate \
#     ~/Library/Developer/Xcode/DerivedData \
#     /Volumes/ExternalDisk/Xcode/DerivedData
#
#   ./space-manager.sh clean \
#     ~/Library/Developer/Xcode/DerivedData
#
# Notes:
#   - Uses rsync instead of mv for safety
#   - Avoids nested symlink bugs
#   - Supports atomic cleanup
# ============================================================

ACTION="${1:-}"

usage() {
  cat <<EOF
Usage: $0 <command> [arguments]

Commands:
  migrate <SOURCE> <TARGET>    Migrate a directory to a new location and create a symlink
  clean   <SOURCE>             Clean a directory (safely handles symlinks)

Examples:
  $0 migrate \\
    ~/Library/Developer/Xcode/DerivedData \\
    /Volumes/ExternalDisk/Xcode/DerivedData

  $0 clean \\
    ~/Library/Developer/Xcode/DerivedData
EOF
  exit 1
}

[[ -z "$ACTION" ]] && usage

expand_path() {
  eval echo "$1"
}

is_symlink() {
  [[ -L "$1" ]]
}

case "$ACTION" in
  migrate)
    [[ $# -ne 3 ]] && usage

    SRC="$(expand_path "$2")"
    DST="$(expand_path "$3")"

    if [[ ! -d "$SRC" ]]; then
      echo "ERROR: Source does not exist: $SRC"
      exit 1
    fi

    mkdir -p "$(dirname "$DST")"

    echo ">>> Rsyncing data..."
    rsync -av --inplace --progress "$SRC/" "$DST/"

    echo ">>> Removing original source directory..."
    rm -rf "$SRC"

    echo ">>> Creating symlink..."
    ln -s "$DST" "$SRC"

    echo ">>> Migration completed."
    ;;

  clean)
    [[ $# -ne 2 ]] && usage

    SRC="$(expand_path "$2")"

    if [[ ! -e "$SRC" ]]; then
      echo "Nothing to clean: $SRC does not exist."
      exit 0
    fi

    if is_symlink "$SRC"; then
      TARGET="$(readlink "$SRC")"
      TARGET_DIR="$(cd "$(dirname "$SRC")" && ls -a | grep "$(basename "$TARGET")" || true)"

      echo ">>> Detected symlink:"
      echo "    $SRC -> $TARGET"

      echo ">>> Removing symlink..."
      rm "$SRC"

      if [[ -d "$TARGET" ]]; then
        BACKUP="${TARGET}.bak.$(date +%s)"
        echo ">>> Safely backing up target to:"
        echo "    $BACKUP"
        mv "$TARGET" "$BACKUP"
      fi

      echo ">>> Recreating target directory..."
      mkdir -p "$TARGET"

      echo ">>> Recreating symlink..."
      ln -s "$TARGET" "$SRC"

      echo ">>> Clean completed (old data preserved as backup)."
    else
      echo ">>> Not a symlink, removing directory directly:"
      echo "    $SRC"
      rm -rf "$SRC"
      echo ">>> Clean completed."
    fi
    ;;

  *)
    usage
    ;;
esac
