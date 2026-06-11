#!/usr/bin/env bash
# Baseline p50/p95 latency из companion_llm.log (подготовка к 5.x Gateway).
set -euo pipefail

LOG="${COMPANION_LLM_METRICS_LOG:-/var/log/aladdin-backend/companion_llm.log}"
DAYS="${1:-7}"

python3 - "$LOG" "$DAYS" <<'PY'
import json, sys, time, statistics
from collections import Counter
from pathlib import Path

path, days = Path(sys.argv[1]), int(sys.argv[2])
cutoff = int(time.time()) - days * 86400
lat: list[int] = []
paths: Counter[str] = Counter()
ctx: Counter[str] = Counter()

if not path.is_file():
    print(f"No log: {path}")
    sys.exit(0)

for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        continue
    if int(row.get("ts", 0)) < cutoff:
        continue
    p = row.get("llm_path") or "unknown"
    paths[p] += 1
    ctx[row.get("ui_context") or "?"] += 1
    ms = row.get("latency_ms")
    if isinstance(ms, (int, float)) and ms > 0:
        lat.append(int(ms))

print(f"=== Latency baseline ({days}d) ===")
print(f"entries: {sum(paths.values())}")
for k, v in paths.most_common():
    print(f"  {k}: {v}")

if lat:
    lat.sort()
    p50 = lat[len(lat) // 2]
    p95 = lat[int(len(lat) * 0.95)] if len(lat) > 1 else lat[-1]
    print(f"latency_ms: n={len(lat)} p50={p50} p95={p95} max={lat[-1]}")
    if p95 > 15000:
        print("WARN: p95 > 15s — consider Gateway API spike (5.x)")
else:
    print("latency_ms: no data yet (need traffic / 1.4 iOS checks)")
PY
