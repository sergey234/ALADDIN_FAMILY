#!/usr/bin/env bash
# Подключить RiveMCP в Cursor (нужен ключ с https://rivemcp.stunning.gg)
set -euo pipefail

MCP_GLOBAL="$HOME/.cursor/mcp.json"
KEY="${RIVEMCP_LICENSE_KEY:-}"

if [[ -z "$KEY" ]]; then
  echo "Usage: RIVEMCP_LICENSE_KEY='your-key' $0"
  echo ""
  echo "Get key: https://rivemcp.stunning.gg (~\$10/mo, отдельно от Cadet)"
  echo "Free trial on this Mac: EXHAUSTED (3/3)"
  exit 1
fi

python3 - <<PY
import json, os
path = os.path.expanduser("~/.cursor/mcp.json")
data = json.load(open(path)) if os.path.isfile(path) else {"mcpServers": {}}
srv = data.setdefault("mcpServers", {}).setdefault("rivemcp", {
    "command": "/usr/local/bin/rivemcp",
    "args": [],
    "env": {}
})
srv["command"] = "/usr/local/bin/rivemcp"
srv["args"] = []
srv["env"] = {"RIVEMCP_LICENSE_KEY": os.environ["RIVEMCP_LICENSE_KEY"]}
json.dump(data, open(path, "w"), indent=2)
print("OK: wrote RIVEMCP_LICENSE_KEY to", path)
print("Next: Cursor → Cmd+Shift+P → Developer: Reload Window")
print("Then: Settings → Tools & MCP → rivemcp → Connected")
PY

rivemcp --reset-license-cache 2>/dev/null || true
echo "Probe:"
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' | rivemcp 2>&1 | head -3
