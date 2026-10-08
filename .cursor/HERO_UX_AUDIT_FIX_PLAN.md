# Итог: план → факт (код)

**Решения:** B · L3 закрыть · микрофон как Сири (фазы) · wellness в «Ещё» → вкладка AI поддержка  
**Сборка:** ждёт отдельного **GO на сборку** (потом — итоговый чеклист «после сборки №5»)

## План → факт

| id | План | Факт в коде |
|----|------|-------------|
| A1–A4 | L3 dismiss + тёмный фон | ✅ `WellnessReferralSheet` l3Shell + Companion `allowDismiss: true` |
| B1–B4 | Premium ≠ сеть | ✅ `PrivacyPremiumErrorMapper` + gate + upsell card |
| C1–C6 | anti-overlap, 2 чипа + Ещё | ✅ `essentialOnly` → «Как день?» + «Ещё» → tab wellness |
| D1–D4 | banner, 409, timeout | ✅ shelf · 409 copy · **load hang fix**: no TaskGroup race; `isLoadingState=false` сразу после `fetchState` (iOS 15.2 sim) |
| E1–E3 | фазы микрофона | ✅ preparing/listening/thinking/speaking в полке |
| E4 | SiriKit | ⏳ позже |
| F1 | static | ✅ |
| F2 | sim | ⏳ после GO на сборку |

## Локализация RU/EN

- `companion_banner_more_chip`, `companion_error_conflict`, `companion_error_load_timeout`
- `companion_mic_phase_*`
- `privacy_premium_required_*`
