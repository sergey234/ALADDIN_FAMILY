# vpn-75 — GA release gate (marketing)

**Разрешение на публичный marketing** только после **G4 FULL PASS**.

## Checklist

| # | Критерий | Статус |
|---|----------|--------|
| 1 | G1–G3 auto gates PASS | ☐ |
| 2 | Integration Week journal — 4 оператора PASS | ☐ |
| 3 | Wi‑Fi A/B (vpn-56) PASS | ☐ |
| 4 | vpn-89 audit signed | ☐ |
| 5 | Legal bridge (vpn-54) — минимум черновик согласован | ☐ |
| 6 | Legal полный (vpn-77) — в работе или ✅ | ☐ |
| 7 | Статус-канал готов к инцидентам (vpn-83) | ☐ |

## Команды

```bash
bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_g4_gate.sh
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_pre_ga_audit.py
python3 /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_integration_week_journal.py
```

## Решение

В `integration-week-journal.json`:

```json
"ga_decision": "approved",
"ga_decision_date": "2026-07-04",
"signed_by": "ops / product owner"
```

**После approved:** можно включать marketing (Stars, канал, лендинг CTA).

**Post-GA (не блокер):** vpn-78 «один Connect», vpn-95 landing `/i/{code}`, vpn-76 reserve EU.
