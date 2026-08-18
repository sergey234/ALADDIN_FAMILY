#!/usr/bin/env bash
#
# Cloud Agent install script for the ALADDIN iOS app.
#
# ALADDIN is a native iOS/SwiftUI application. Building, running the simulator,
# and the xcodebuild-based unit/UI tests all require macOS + Xcode and therefore
# cannot run inside a Linux Cloud Agent VM. What *can* run here is the static
# analysis / linting and the grep-based security scan that the GitHub Actions
# workflows perform. This script provisions SwiftLint (the tool used by the
# `code-quality` CI job) so an agent can lint Swift sources on Linux.
#
# The script is idempotent: it is safe to run repeatedly and will only download
# SwiftLint when the pinned version is not already installed.
set -euo pipefail

SWIFTLINT_VERSION="0.65.0"
INSTALL_PATH="/usr/local/bin/swiftlint"
ARCH="$(uname -m)"

if [ "$ARCH" != "x86_64" ]; then
  echo "WARNING: this install script targets x86_64; detected '$ARCH'." >&2
fi

install_swiftlint() {
  local url tmp
  url="https://github.com/realm/SwiftLint/releases/download/${SWIFTLINT_VERSION}/swiftlint_linux_amd64.zip"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  echo "Downloading SwiftLint ${SWIFTLINT_VERSION}..."
  curl -fsSL -o "$tmp/swiftlint.zip" "$url"

  if ! command -v unzip >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y --no-install-recommends unzip
  fi

  unzip -o -q "$tmp/swiftlint.zip" -d "$tmp/extracted"

  # The `-static` variant bundles SourceKit and runs without a full Swift
  # toolchain on Linux, so we install it as the canonical `swiftlint` binary.
  sudo install -m 0755 "$tmp/extracted/swiftlint-static" "$INSTALL_PATH"
}

current_version="$(swiftlint version 2>/dev/null || true)"
if [ "$current_version" = "$SWIFTLINT_VERSION" ]; then
  echo "SwiftLint ${SWIFTLINT_VERSION} already installed at $(command -v swiftlint)."
else
  install_swiftlint
fi

echo "SwiftLint version: $(swiftlint version)"
echo "Install complete."
