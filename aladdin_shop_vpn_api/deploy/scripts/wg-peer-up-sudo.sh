#!/usr/bin/env bash
# vpn-13: вызов wg-peer-up.sh от имени root через узкий sudoers (воркер под aladdin-shop-vpn).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/wg-peer-up.sh"
TID="${1:?usage: wg-peer-up-sudo.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
    echo "wg-peer-up-sudo: invalid telegram_user_id" >&2
    exit 1
}
exec /usr/bin/sudo -n "$TARGET" "$TID"
