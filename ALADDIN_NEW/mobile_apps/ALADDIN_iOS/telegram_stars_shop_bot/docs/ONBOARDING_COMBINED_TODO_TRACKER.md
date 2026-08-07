# Трекер: объединённый онбординг (канал + согласие)

**План:** [`PLAN_ONBOARDING_COMBINED_CHANNEL_TERMS_2026-07-30.md`](./PLAN_ONBOARDING_COMBINED_CHANNEL_TERMS_2026-07-30.md)

| ID | Задача | Статус |
|----|--------|--------|
| ob-00-docs | PLAN + трекер + BOT_ARCHITECTURE §9 | ✅ |
| ob-01-copy-kb | caption + `onboarding_combined_kb` | ✅ |
| ob-02-pipeline | `onboarding_gate` combined вместо terms→channel | ✅ |
| ob-03-handler | `onb:ch:check` → `accept_terms` + legacy terms | ✅ |
| ob-04-vpn-skip | VPN legal skip при `terms_accepted` | ✅ |
| ob-05-tests | pytest (19 passed) | ✅ |
| ob-06-deploy | Contabo poller `20260731-000338` + MAIN code sync; bot/API active | ✅ |

**Ручной smoke:** `/start` новым юзером → один экран (канал + документы) → «Проверить подписку» → капча/хаб.
