# vpn-88 — Integration Week G4 (календарь + журнал)

**Gate:** G4 PASS → **vpn-75** marketing GA  
**SSOT журнал:** `/opt/aladdin-shop-vpn-api/var/integration-week-journal.json`  
**Шаблон:** `deploy/var/integration-week-journal.template.json`

## Календарь (2026-06-28 старт)

| День | Дата | Сеть | Задача | vpn-xx |
|------|------|------|--------|--------|
| **D1** | 2026-06-28 | Wi‑Fi | «Домашний Wi‑Fi» vs OpenVPN, speed ≥1 Mbit/s ≥5 min | vpn-56 |
| **D2** | 2026-06-29 | 4G | MegaFon: «Мобильный мост» → «Мобильный CDN» | vpn-55 |
| **D3** | 2026-06-30 | 4G | MTS | vpn-55 |
| **D4** | 2026-07-01 | 4G | Beeline | vpn-55 |
| **D5** | 2026-07-02 | 4G | **Tele2** | vpn-79 |
| **D6** | 2026-07-03 | — | Pre-GA audit «6 шляп» + DoD §5.1 | vpn-89 |
| **D7** | 2026-07-04 | — | Решение GA (`ga_decision=approved`) | vpn-75 |

## Порядок профилей на 4G

1. **Мобильный мост** (RU bridge)  
2. Если FAIL → **Мобильный интернет** (direct Contabo)  
3. Если FAIL → **Мобильный CDN**

PASS = **≥1 Mbit/s** на fast.com **≥5 минут** подряд.

## Заполнение журнала

```bash
# на Contabo или локально скопировать шаблон
cp deploy/var/integration-week-journal.template.json \
   /opt/aladdin-shop-vpn-api/var/integration-week-journal.json

# после каждого дня — править JSON:
#   "speed_mbps": 3.2,
#   "result": "PASS",
#   "tested_at": "2026-06-29T14:30:00+03:00",
#   "tester": "ops"

python3 deploy/scripts/vpn_integration_week_journal.py
```

## Auto gate (без телефона)

```bash
bash deploy/scripts/vpn_g4_gate.sh
# → G4 AUTO PASS пока journal PENDING

python3 deploy/scripts/vpn_pre_ga_audit.py
```

## G4 FULL PASS (marketing GA)

1. Все 5 entries `result: PASS` + speed/duration  
2. `audit_vpn89.completed: true` + подпись  
3. `ga_decision: approved`  
4. `vpn_g4_gate.sh` exit 0  

См. также `VPN75_GA_RELEASE_GATE.md`, `VPN_QUARTERLY_DRILL_CHECKLIST.md`.
