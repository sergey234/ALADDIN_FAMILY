#!/usr/bin/env bash
# Prod smoke (run on VPS as root). Does not print secrets.
set -euo pipefail
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.py
