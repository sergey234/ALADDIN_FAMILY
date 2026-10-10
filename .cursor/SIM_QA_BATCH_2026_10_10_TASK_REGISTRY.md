# Sim QA batch 2026-10-10 — SSOT

**Constraint:** no push without GO · SSH/prod restart only with ops GO · no xcodebuild without «GO на сборку»

---

## План–Факт (итог)

| ID | Задача | План | Факт |
|----|--------|------|------|
| sqa-01 | Invite «операция недоступна» | 3 варианта + soft-fail | ✅ Hybrid: Invite всегда + жёлтый soft-banner + Retry |
| sqa-02 | Жёлтая карточка тарифа | разобрать цвет | ✅ free=`secondaryGold` by design; StoreKit sim fail |
| sqa-03 | Invite API probe | health + 403 | ✅ health 200; stats/rewards/devices 403 без JWT |
| sqa-04 | AI не отвечает | consent | ✅ `cloud_disabled` / `consent_off` — включить в Settings |
| sqa-05 | TF2 ретро | оценка | ✅ crash/loc/coverage/KB — лучшие; 504 = ops+timeout UX |
| sqa-06 | 504 / companion hang | nginx + UX | ✅ сейчас 504 нет (unauth); hang → soft timeout 8s |
| sqa-07 | Unicorn crop | PNG | ✅ de-letterbox `unicorn_master.png` |
| sqa-08 | LOGS + geofence | gate + contrast | ✅ VisualLogger off; geofence contrast |
| sqa-09 | Fake iPhone 13 | убрать | ✅ убраны |
| sqa-10 | Registry/TODO | SSOT | ✅ этот файл |
| sqa-11 | Hybrid Invite | soft-fail + retry | ✅ `21_ReferralScreen` local code + soft warning |
| sqa-12 | Companion timeout | 8s overlay | ✅ `CompanionConversationScreen.loadState` |
| sqa-13 | Server stats matrix | probe | ✅ см. таблицу ниже |
| sqa-14 | Sessions Hybrid real | getDevices + Parent Gate | ✅ `ActiveSessionsView` real API, no GPS |
| sqa-15 | Plan–Fact final | чеклист | ✅ этот раздел |

---

## Server probe (2026-10-10, без JWT)

| Endpoint | Edge `aladdin-ai.ru` | Direct `:8002` |
|----------|----------------------|----------------|
| `/api/health` | 200 · ~0.12s · `ok` | 200 · ~0.07s · `ok` |
| `/api/referral/overview` | 200 · ~0.16s · **mock** `Unknown function: get_referral_overview` | 200 · mock |
| `/api/referral/stats` | 403 · ~0.25s · Not authenticated | — |
| `/api/referral/rewards` | 403 · ~0.13s | — |
| `/api/devices` | 403 · ~0.15s | 403 · ~0.06s |
| `/api/wellness/metrics` | 200 · ~0.12s · **mock** | 200 · mock |
| `/api/companion/session` | 200 · ~0.12s · **mock** | — |
| `/api/companion/metrics` | 200 · ~0.15s · **mock** | — |

**Вывод:** сейчас **нет 504** на unauth probe (раньше ~30s nginx timeout под auth/load).  
**Риск:** часть путей без JWT отдают `source=mock` / Unknown function — для реальных сессий нужен **auth smoke (ops GO)**.  
504 в логах приложения = медленный authenticated upstream, не перевод.

---

## Apple / закон — Active sessions Hybrid

**Разрешено:** список устройств семейной защиты (имя, тип, last activity) из `GET /api/devices` + Sign out = `removeDevice` после `ParentSessionGate` — **без точного GPS**, без MDM wipe / Find My remote lock.

Согласуется с:
- App Store: семейный контроль / управление аккаунтом; parental gate на чувствительное действие
- Privacy: не показываем точную геолокацию чужих устройств в этом экране
- Не выдаём выдуманные «iPhone 13»

---

## Код (что изменили)

| Файл | Зачем |
|------|--------|
| `Screens/21_ReferralScreen.swift` | Hybrid Invite: local/cached code; soft orange banner; Retry stats |
| `Screens/11_ProfileScreen.swift` (`ActiveSessionsView`) | Real `getDevices`; Sign out + Parent Gate; no fake rows / no GPS |
| `Screens/CompanionConversationScreen.swift` | 8s soft timeout → chat usable + human message |
| `Resources/Localization/en|ru.lproj/Localizable.strings` | новые ключи sessions/referral soft |
| `Core/Localization/LocalizationManager.swift` | EN/RU dict SSOT для тех же ключей |

---

## Чеклист исполнения

- [x] Hybrid Invite soft-fail + retry  
- [x] Server matrix + stats  
- [x] Apple-safe Hybrid sessions (real API)  
- [x] Companion loading timeout UX  
- [x] Loc keys EN/RU + LocalizationManager  
- [x] Plan–Fact  
- [ ] Device QA / симулятор — только после **GO на сборку**  
- [ ] Auth smoke referral/devices на проде — только после **ops GO**  
- [ ] Commit / push — только после явного GO  
