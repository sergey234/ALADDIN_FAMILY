#!/bin/bash
# Rebuild the static handbook. Curated files win over exported UI strings.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/tools/export_kb_v1.py"
python3 "$ROOT/tools/ingest_kb_v1_chunks.py"
python3 "$ROOT/tools/verify_kb_v1.py"
