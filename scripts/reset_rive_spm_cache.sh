#!/usr/bin/env bash
# HERO-3-08 — fix SPM binary target cache for RiveRuntime.
# Fixes:
#   - "already exists in file system" (corrupt global SPM cache)
#   - "There is no XCFramework found at .../rive-ios/RiveRuntime/RiveRuntime.xcframework"
#     (resolve alone does not always extract; this script seeds DerivedData explicitly)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$ROOT/ALADDIN.xcodeproj"
SCHEME="${ALADDIN_SCHEME:-ALADDIN}"
RIVE_VERSION="${RIVE_IOS_VERSION:-6.20.5}"
ZIP_URL="https://github.com/rive-app/rive-ios/releases/download/${RIVE_VERSION}/RiveRuntime.xcframework.zip"
CHECKSUM="3deb9bcc402a24dc94a341612ba0996e904cdce4e4c91939e16a43fde0e18b80"

echo "→ Close Xcode before continuing (avoids locked caches)."
echo "→ Project: $PROJECT"

GLOBAL_ARTIFACT_NAME="https___github_com_rive_app_rive_ios_releases_download_${RIVE_VERSION//./_}_RiveRuntime_xcframework_zip"
GLOBAL_ARTIFACT="$HOME/Library/Caches/org.swift.swiftpm/artifacts/${GLOBAL_ARTIFACT_NAME}"
if [[ -e "$GLOBAL_ARTIFACT" ]]; then
  echo "→ Removing global SPM artifact: $GLOBAL_ARTIFACT"
  rm -rf "$GLOBAL_ARTIFACT"
fi

TMP_ZIP="$(mktemp -t RiveRuntime.xcframework.XXXXXX.zip)"
cleanup() { rm -f "$TMP_ZIP"; }
trap cleanup EXIT

echo "→ Downloading RiveRuntime ${RIVE_VERSION}…"
curl -fsSL "$ZIP_URL" -o "$TMP_ZIP"
echo "$CHECKSUM  $TMP_ZIP" | shasum -a 256 -c -

seed_derived_data_rive() {
  local dd="$1"
  local dest="$dd/SourcePackages/artifacts/rive-ios/RiveRuntime"
  local xcf="$dest/RiveRuntime.xcframework"
  if [[ -d "$xcf" ]]; then
    echo "→ Already present: $xcf"
    return 0
  fi
  echo "→ Extracting into DerivedData: $dest"
  rm -rf "$dest" "$dd/SourcePackages/artifacts/extract/rive-ios"
  mkdir -p "$dest"
  ditto -x -k "$TMP_ZIP" "$dest"
  if [[ ! -d "$xcf" ]]; then
    echo "ERROR: expected $xcf after extract" >&2
    exit 1
  fi
}

# Seed every ALADDIN DerivedData folder (Xcode may use any hash suffix)
found_dd=0
while IFS= read -r -d '' dd; do
  found_dd=1
  seed_derived_data_rive "$dd"
done < <(find "$HOME/Library/Developer/Xcode/DerivedData" -maxdepth 1 -type d -name 'ALADDIN-*' -print0 2>/dev/null || true)

if [[ "$found_dd" -eq 0 ]]; then
  echo "→ No ALADDIN DerivedData yet; resolve will create one on next build."
fi

echo "→ Resolving packages…"
xcodebuild -resolvePackageDependencies -project "$PROJECT" -scheme "$SCHEME" >/dev/null

# Re-seed after resolve (resolve can wipe incomplete extract/)
while IFS= read -r -d '' dd; do
  seed_derived_data_rive "$dd"
done < <(find "$HOME/Library/Developer/Xcode/DerivedData" -maxdepth 1 -type d -name 'ALADDIN-*' -print0 2>/dev/null || true)

echo "✓ RiveRuntime.xcframework ready. Open Xcode → Clean Build Folder → Build."
