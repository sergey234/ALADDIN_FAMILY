#!/bin/bash
# SFM health check: posts a small execute ping and on failure restarts gateway
set -e
OUT=$(curl -sS -X POST http://127.0.0.1:8003/api/execute -H 'Content-Type: application/json' -d '{"function":"ping","params":{}}' || true)
if echo "$OUT" | grep -qi 'success'; then
    echo "SFM OK"
    exit 0
else
    echo "SFM unhealthy: $OUT" >&2
    systemctl restart aladdin-main-api-gateway || true
    exit 2
fi
