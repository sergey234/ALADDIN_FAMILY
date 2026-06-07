#!/usr/bin/env bash
# Curated ECC install for ALADDIN iOS (batches 1–3). Does NOT overwrite existing .mdc domain rules.
# Official ECC minimal profile pulls 200+ unrelated lang rules — we copy only ALADDIN-needed assets.

set -euo pipefail

ECC="${ECC_ROOT:-/tmp/ECC}"
IOS="$(cd "$(dirname "$0")/.." && pwd)"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

if [[ ! -d "$ECC" ]]; then
  echo "ERROR: ECC not found at $ECC. Clone: git clone --depth 1 https://github.com/affaan-m/ECC.git /tmp/ECC" >&2
  exit 1
fi

copy_file() {
  local src="$1" dest="$2"
  if [[ ! -f "$src" ]]; then
    echo "SKIP missing: $src" >&2
    return 0
  fi
  if [[ -f "$dest" ]] && cmp -s "$src" "$dest" 2>/dev/null; then
    echo "UNCHANGED $dest"
    return 0
  fi
  if $DRY_RUN; then
    echo "WOULD COPY $src -> $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "COPIED $dest"
  fi
}

copy_dir() {
  local src="$1" dest="$2"
  if [[ ! -d "$src" ]]; then
    echo "SKIP missing dir: $src" >&2
    return 0
  fi
  if $DRY_RUN; then
    echo "WOULD RSYNC $src/ -> $dest/"
  else
    mkdir -p "$dest"
    rsync -a "$src/" "$dest/"
    echo "RSYNC $dest/"
  fi
}

echo "=== ALADDIN curated ECC install (dry_run=$DRY_RUN) ==="
echo "ECC: $ECC"
echo "IOS: $IOS"
echo ""

# Swift + common rules (new files only — never touch aladdin-*.mdc, prod-no-mock, figma-*)
for f in swift-coding-style swift-hooks swift-patterns swift-security swift-testing common-security common-testing; do
  if [[ -f "$ECC/.cursor/rules/${f}.mdc" ]]; then
    copy_file "$ECC/.cursor/rules/${f}.mdc" "$IOS/.cursor/rules/${f}.mdc"
  elif [[ -f "$ECC/.cursor/rules/${f}.md" ]]; then
    copy_file "$ECC/.cursor/rules/${f}.md" "$IOS/.cursor/rules/${f}.mdc"
  else
    echo "SKIP missing rule: $f" >&2
  fi
done

# Skills (batch 2–4 partial)
for skill in security-review security-scan verification-loop tdd-workflow \
  swiftui-patterns swift-actor-persistence swift-concurrency-6-2 swift-protocol-di-testing; do
  copy_dir "$ECC/skills/$skill" "$IOS/.cursor/skills/$skill"
done

# Agents (batch 2–3)
mkdir -p "$IOS/.cursor/agents" 2>/dev/null || true
for agent in swift-reviewer swift-build-resolver security-reviewer build-error-resolver e2e-runner; do
  copy_file "$ECC/agents/${agent}.md" "$IOS/.cursor/agents/${agent}.md"
done

# Install state marker
if ! $DRY_RUN; then
  cat > "$IOS/.cursor/ecc-install-state.json" << EOF
{
  "installedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "method": "aladdin-curated",
  "eccVersion": "$(cat "$ECC/VERSION" 2>/dev/null || echo unknown)",
  "components": [
    "swift-rules", "common-security", "common-testing",
    "skills:security-review,security-scan,verification-loop,tdd-workflow,swift-*",
    "agents:swift-reviewer,swift-build-resolver,security-reviewer,build-error-resolver,e2e-runner"
  ],
  "mcpJson": "unchanged — audit in batch 7"
}
EOF
  echo "WROTE .cursor/ecc-install-state.json"
fi

echo ""
echo "Done. mcp.json NOT modified (batch 7 = audit only)."
