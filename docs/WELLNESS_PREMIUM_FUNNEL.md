# Wellness Premium-воронка (r100-1-16)

> **Одной фразой:** хочу больше wellness → вижу что платно → тарифы → оплата → доступ.

## Цепочка

| Шаг | Где |
|-----|-----|
| 1 | Hub: **Timeline** или **Опросники** (не PHQ-lite с главного потока) |
| 2 | `GET /api/wellness/premium/eligibility` |
| 3 | Нет подписки → `WellnessPremiumPaywallSheet` |
| 4 | **Посмотреть тарифы** → `10_TariffsScreen` |
| 5 | StoreKit / оплата семьи → снова eligibility → экран открывается |

## Код

- `Core/Services/WellnessPremiumFunnel.swift` — gate
- `Screens/WellnessPremiumPaywallSheet.swift` — paywall + навигация на тарифы
- `Screens/WellnessHubScreen.swift` — timeline + assessments hub
- `Screens/WellnessTimelineScreen.swift` — gate при загрузке timeline

## DoD

- [ ] TestFlight: без подписки → paywall; с подпиской → timeline OK
- [ ] Restore purchases на staging
- [ ] После L3 кризиса premium заблокирован (ethics) — smoke на prod

*Build 223 · 2026-06-03*
