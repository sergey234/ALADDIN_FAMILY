# G4 Integration Week — готовность (до телефона)

**Journal:** `/opt/aladdin-shop-vpn-api/var/integration-week-journal.json`  
**Календарь:** `VPN_INTEGRATION_WEEK_G4.md`

## Auto (должно быть PASS до телефона)

```bash
bash deploy/scripts/vpn_g4_gate.sh          # G4 AUTO PASS
python3 deploy/scripts/vpn_pre_ga_audit.py
bash deploy/scripts/vpn_dns_verify.sh       # CDN path
```

## Checklist

| # | Готово | Задача |
|---|--------|--------|
| ☐ | ✅ | DNS cdn → MAIN (ф2) или relay |
| ☐ | ✅ | Legal v1.1 в репо → юрист sign-off |
| ☐ | | Mac external smoke cron |
| ☐ | | Contabo S4 cron |
| ☐ | | D1 Wi‑Fi vpn-56 |
| ☐ | | D2–D5 4G vpn-55/79 |
| ☐ | | D6 audit sign vpn-89 |
| ☐ | | D7 ga_decision vpn-75 |

## После телефона

```json
"ga_decision": "approved",
"audit_vpn89": { "completed": true, "signed_by": "...", "signed_at": "..." }
```

`vpn_g4_gate.sh` → **G4 FULL PASS** → marketing GA.
