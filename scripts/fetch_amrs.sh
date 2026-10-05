#!/usr/bin/env bash
# Download the AMRS program from its GitHub release and put it where the plugin
# copies it from (the folder every new project gets and the Run button uses):
#   src/apexmod/FOLDER_FOR_COPY/APEX-MODFLOW/amrs       (Linux, gfortran, static)
#   src/apexmod/FOLDER_FOR_COPY/APEX-MODFLOW/amrs.exe   (Windows, gfortran)
#
#   scripts/fetch_amrs.sh                    # Linux program, version in amrs-version.txt
#   scripts/fetch_amrs.sh v0.1.0             # another release
#   AMRS_PLATFORM=windows scripts/fetch_amrs.sh   # Windows program only
#   AMRS_PLATFORM=all scripts/fetch_amrs.sh       # both (what the release workflow uses)
#   AMRS_ASSET=ifx-lin_x86_64 scripts/fetch_amrs.sh   # Intel ifx build for Linux instead
#
# The programs are not committed (see src/apexmod/.gitignore).
set -euo pipefail

repo="spark-hydro/AMRS"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version="${1:-$(tr -d '[:space:]' < "$root/amrs-version.txt")}"
platform="${AMRS_PLATFORM:-linux}"
dest="$root/src/apexmod/FOLDER_FOR_COPY/APEX-MODFLOW"

case "$platform" in linux|windows|all) ;; *) echo "AMRS_PLATFORM must be linux, windows or all" >&2; exit 1 ;; esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dest"

fetch_asset() {  # fetch_asset ASSET TARGET_NAME
    local asset="$1" target="$2" zip="amrs-${version}-$1-Rel.zip"
    echo "Downloading $zip from $repo"
    if command -v gh >/dev/null 2>&1; then
        gh release download "$version" --repo "$repo" --pattern "$zip" --dir "$tmp"
    else
        curl -fsSL -o "$tmp/$zip" "https://github.com/$repo/releases/download/$version/$zip"
    fi
    rm -rf "$tmp/x"
    python3 -m zipfile -e "$tmp/$zip" "$tmp/x"
    local exe
    exe="$(find "$tmp/x" -type f -name 'amrs-*' | head -1)"
    [ -n "$exe" ] || { echo "no amrs-* program in $zip" >&2; exit 1; }
    cp "$exe" "$dest/$target"
    chmod +x "$dest/$target"
    echo "Installed $target ($version, $asset) in FOLDER_FOR_COPY/APEX-MODFLOW"
}

if [ "$platform" = linux ] || [ "$platform" = all ]; then
    fetch_asset "${AMRS_ASSET:-gnu-lin_x86_64}" amrs
    "$dest/amrs" --version | sed -n '/AMRS/,$p'
fi
if [ "$platform" = windows ] || [ "$platform" = all ]; then
    fetch_asset gnu-win_amd64 amrs.exe
fi
