#!/usr/bin/env bash
# ALADDIN OPS Command Center digest → all ADMIN_IDS (same fan-out as payment cards).
# Slots: morning | lunch | evening | auto
set -euo pipefail

SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=vpn_ops_notify.sh
source "${SCRIPTS}/vpn_ops_notify.sh"

vpn_ops_load_env

SLOT="${1:-auto}"
case "$SLOT" in
  morning|lunch|evening|auto) ;;
  *)
    echo "usage: $0 [morning|lunch|evening|auto]" >&2
    exit 2
    ;;
esac

REPORT="$(
  /usr/bin/python3 "${SCRIPTS}/vpn_ops_command_center.py" --slot "$SLOT" --print-only
)"

RESOLVED="$(
  SLOT="$SLOT" /usr/bin/python3 - <<'PY'
import os
from datetime import datetime
from zoneinfo import ZoneInfo
slot = os.environ.get("SLOT", "auto")
if slot == "auto":
    hour = datetime.now(ZoneInfo("Europe/Moscow")).hour
    slot = "morning" if hour < 12 else "lunch" if hour < 18 else "evening"
print(slot)
PY
)"

DATE_MSK="$(TZ=Europe/Moscow date +%F)"
vpn_ops_digest "ops-cc-${DATE_MSK}-${RESOLVED}" "$REPORT"
