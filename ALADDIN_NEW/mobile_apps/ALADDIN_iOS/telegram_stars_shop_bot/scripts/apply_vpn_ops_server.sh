#!/usr/bin/env bash
# VPN ops: connIdle в xray, ночной restart моста на MAIN, auto-fulfill worker только на Contabo.
set -euo pipefail

KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
SSH_OPTS=(-o IdentitiesOnly=yes -i "$KEY")
MAIN="${MAIN_HOST:-root@149.154.65.180}"
CONTABO="${BOT_HOST:-root@185.225.233.150}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"

apply_xray_policy() {
  local host="$1" cfg="$2" unit="$3"
  ssh "${SSH_OPTS[@]}" "$host" bash -s <<EOF
set -e
python3 <<'PY'
import json, shutil, subprocess
from datetime import datetime
path = "${cfg}"
unit = "${unit}"
bak = f"{path}.bak-connidle-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(path, bak)
with open(path, encoding="utf-8") as f:
    d = json.load(f)
d["policy"] = {
    "levels": {
        "0": {
            "connIdle": 300,
            "handshake": 4,
            "uplinkOnly": 0,
            "downlinkOnly": 0,
        }
    }
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)
    f.write("\n")
subprocess.run(["systemctl", "restart", unit], check=True)
print("updated", path, "backup", bak)
PY
EOF
}

echo "==> xray connIdle policy"
apply_xray_policy "$MAIN" "/opt/xray-bridge/config.json" "xray-bridge.service"
apply_xray_policy "$CONTABO" "/opt/xray/config.json" "xray.service"

echo "==> MAIN: nightly xray-bridge restart timer"
ssh "${SSH_OPTS[@]}" "$MAIN" bash -s <<'EOF'
set -e
cat > /etc/systemd/system/xray-bridge-nightly-restart.service <<'UNIT'
[Unit]
Description=Restart Xray RU bridge (zombie xhttp sessions)

[Service]
Type=oneshot
ExecStart=/bin/systemctl restart xray-bridge.service
UNIT
cat > /etc/systemd/system/xray-bridge-nightly-restart.timer <<'UNIT'
[Unit]
Description=Nightly restart Xray RU bridge

[Timer]
OnCalendar=*-*-* 04:30:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl enable --now xray-bridge-nightly-restart.timer
systemctl list-timers xray-bridge-nightly-restart.timer --no-pager | head -3
EOF

echo "==> auto-fulfill worker: Contabo ON, MAIN OFF"
scp "${SSH_OPTS[@]}" "${SRC}/docs/auto-fulfill-worker.service" "${CONTABO}:/etc/systemd/system/auto-fulfill-worker.service"
ssh "${SSH_OPTS[@]}" "$CONTABO" 'systemctl daemon-reload && systemctl enable --now auto-fulfill-worker.service && systemctl is-active auto-fulfill-worker.service'
ssh "${SSH_OPTS[@]}" "$MAIN" 'systemctl stop auto-fulfill-worker.service 2>/dev/null || true; systemctl disable auto-fulfill-worker.service 2>/dev/null || true; systemctl is-active auto-fulfill-worker.service 2>&1 || echo MAIN_AUTO_FF_OFF'

echo "==> OK vpn-ops server apply"
