#!/usr/bin/env bash
# phase-a-verify: health, optional JWT, family WS upgrade (run on VPS or via ssh)
set -euo pipefail
KEY="${HOME}/.ssh/aladdin_server"
HOST="root@149.154.65.180"
SSH=(ssh -o BatchMode=yes -o IdentitiesOnly=yes -i "$KEY" "$HOST")

echo "=== phase-a-verify ==="

"${SSH[@]}" 'curl -sf http://127.0.0.1:8002/api/health && echo backend_ok'
"${SSH[@]}" 'curl -sf http://127.0.0.1:8003/api/health && echo sfm_ok'
"${SSH[@]}" 'curl -sf https://aladdin-ai.ru/api/health && echo nginx_ok'

"${SSH[@]}" 'curl -i -N -m 5 -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  "http://127.0.0.1:8002/ws/family/chat?familyId=TEST" 2>/dev/null | head -3'

echo "=== SSE nginx (ai-sse-nginx hint) ==="
"${SSH[@]}" 'grep -R "proxy_buffering\|assistant/stream" /etc/nginx/sites-enabled/ 2>/dev/null | head -20 || true'

echo "phase-a-verify DONE"
