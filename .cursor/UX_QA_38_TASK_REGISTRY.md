# UX QA 38 screens — Task Registry (SSOT Cursor TODO)

**Дата:** 2026-11-14/15  
**Порядок:** Wave **A→B→C→D→E** (pilot GO) · потом P1 · Device QA = **владелец** в конце  
**Handoff:** `docs/ML_SYSTEM_HANDOFF_UX_QA_38_SCREENS_2026-11-14.md`  
**Чеклист:** `docs/PLAN_UX_QA_SCREEN_CHECKLIST_2026-11-14.md`  
**Скрины:** `docs/qa_ux_38_screens_2026-11-14/MANIFEST.tsv`

**LOCKED:** Strip **A★** · Trips **H1 Hybrid★** · CapCut/Nativo/Pet/Tile/Gold-clone = **НЕТ**  
**Сборка:** только владелец / явное GO · агент **не** `xcodebuild`  
**Loc:** `ru`+`en`.lproj **сначала** → LocManager только `StrReplace` → `./scripts/verify_localization_manager_integrity.sh`  
**Cursor TODO:** ids `uxqa-*` · закрывать `merge: true` · **не** схлопывать список

---

## Meta

| id | Status | Note |
|----|--------|------|
| uxqa-meta | ✅ code | P0+P1 code done (audit 2026-11-15) · Device QA = owner |
| uxqa-skip | ❌ SKIP | CapCut / Nativo S22 / Pet S26 / Tile / Gold 1:1 |
| uxqa-P2-help | ❌ optional later | Help S27–33 · own paywall S34 |

---

## Wave A — trust/geo FIRST

| id | Task | Screens | Status |
|----|------|---------|--------|
| uxqa-hdr-A | HDR Wave A | — | ✅ |
| uxqa-A-05a | P0.5a RCA LocationManager ±4200 / coarse vs precise | S13 | ✅ |
| uxqa-A-05b | P0.5b Honest accuracy UI + CTA precise/Settings | S13 | ✅ |
| uxqa-A-05c | P0.5c Refresh = icon/FAB (not huge card) | S13 | ✅ |
| uxqa-B-06a | P0.6a Map tap must not dismiss | S14 | ✅ |
| uxqa-B-06b | P0.6b Tap = pin/journal; chrome regression | S14 | ✅ |

**Files:** `LocationManager.swift`, `WhereIsPhoneScreen.swift`

---

## Wave C — trips H1 (RCA → product)

| id | Task | Screens | Status |
|----|------|---------|--------|
| uxqa-hdr-C | HDR Wave C | — | ✅ |
| uxqa-C-04a | P0.4a RCA empty track + Always/Motion logs | S07–12, S38 | ✅ |
| uxqa-C-04b | P0.4b Data path ≥2 points OR honest empty | S13, S38 | ✅ |
| uxqa-C-04c | P0.4c UNNotification name·km·vmax RU/EN | S07 | ✅ |
| uxqa-C-04d | P0.4d Deep link trips+tripId → map+polyline | S08–12 | ✅ |
| uxqa-C-04e | P0.4e Brand polyline + short BG tip RU/EN | S08–12 | ✅ |
| uxqa-C-04f | P0.4f/J38 Default «Вы» / You (memberId) | S38 | ✅ |

**Files:** `FamilyMapAutoTripTracker`, `FamilyDrivingTripLedger`, `DrivingTripTrackStore`, `FamilyPushDeepLink`, `WhereIsPhoneScreen`, Push services

---

## Wave D — SimpleHome ONE diff

| id | Task | Screens | Status |
|----|------|---------|--------|
| uxqa-hdr-D | HDR Wave D | — | ✅ |
| uxqa-D-02a | P0.2 Unify hero container; kill 5811 chrome | S05 | ✅ |
| uxqa-D-01a | P0.1 Circle ~254; center; gap≥10 | S01–06 | ✅ |
| uxqa-D-01b | P0.1 Door icon 0.86–0.92; orbit 318 untouched | S01–06 | ✅ |
| uxqa-D-03a | P0.3 Loc A★ slots_fmt + «мест»/seats | S01–06 | ✅ |
| uxqa-D-03b | P0.3 UI always «Добавить в семью»; no iOS15 «1 из 1» | S01–06 | ✅ |
| uxqa-D-03c | P0.3 a11y + SSOT + loc verify | S01–06 | ✅ |

**Files:** `SimpleHomeScreen.swift` + Loc strings only for strip

---

## Wave E — Trial (NOT slots)

| id | Task | Screens | Status |
|----|------|---------|--------|
| uxqa-hdr-E | HDR Wave E | — | ✅ |
| uxqa-E-07a | P0.7a Audit CTA vs recoverableTrialEndDate | Main | ✅ |
| uxqa-E-07b | P0.7b Honest «до {date}»; no strip confuse | Main | ✅ |

**Files:** `01_MainScreen.swift`, `SubscriptionManager.swift` (minimal), existing key `main_family_restore_trial_cta`

---

## P1

| id | Task | Screens | Status |
|----|------|---------|--------|
| uxqa-hdr-P1 | HDR P1 | — | ✅ |
| uxqa-P1-14a | Date «С понедельника, …» RU+EN | S14 | ✅ |
| uxqa-P1-14b | Period picker today/week/custom | S14 | ✅ |
| uxqa-P1-15a | Kill «Ничего не выдумываем» → one CTA | S15 | ✅ |
| uxqa-P1-15b | Accordion members | S15 | ✅ |
| uxqa-P1-15c | Готово/Done apply+dismiss | S15 | ✅ |
| uxqa-P1-16a | Crash tip Always/Motion/Push | S16 | ✅ |
| uxqa-P1-17a | Inbox filters Tips/Offers/Notifs/All | S17 | ✅ |
| uxqa-P1-18a | Envelope→inbox; gear→settings | S18 | ✅ |
| uxqa-P1-37a | Journal photo PHPicker «В» | S37 | ✅ |
| uxqa-P1-19a | C19 settings hub AUDIT first | S19–21,23–25,35 | ✅ |
| uxqa-P1-19b | C19 gap-only LAST; no Profile clone | same | ✅ |

---

## Closeout

| id | Task | Status |
|----|------|--------|
| uxqa-hdr-P2 | HDR P2 / Device QA | ⬜ owner |
| uxqa-gates | GATES evidence table | ⬜ owner after tap-through |
| uxqa-loc-verify | All new keys RU+EN + verify script | ✅ strings+verify OK; Device QA confirms no raw keys |
| uxqa-device-qa | Owner Xcode build + tap-through `docs/DEVICE_QA_UX_38_TAP_THROUGH_2026-11-15.md` | ⬜ |

---

## Localization matrix (чтобы не переделывать)

Правило: UI **никогда** не показывает сырой ключ. Сначала `Resources/Localization/{ru,en}.lproj/Localizable.strings`, потом точечный dict в `LocalizationManager` если нужен fallback.

### Уже есть (править value / не дублировать ключ)

| Key | RU сейчас | Действие |
|-----|-----------|----------|
| `pay_pains_family_strip_slots_fmt` | `Семья · %d из %d` | → `Семья · %d из %d мест` |
| `pay_pains_family_strip_slots_fmt` EN | `Family · %d of %d` | → `Family · %d of %d seats` |
| `pay_pains_family_strip_add_to_family` | `Добавить в семью` | UI всегда показывать (не только a11y) |
| `pay_pains_family_strip_add` | `Добавить` | Только extreme fallback / не единственный visible |
| `main_family_header_member_slots` | `%d из %d` | Не использовать как единственный visible на iOS 15 |
| `main_family_restore_trial_cta` | `Вернуть пробный до %@` | Audit date arg; EN `Restore trial until %@` OK |
| `map_accuracy_meters_format` | `Точность ±%d м` | Keep; не врать coarse |
| `map_perm_precise_hint` | (exists) | Wire CTA when accuracy bad |
| `where_phone_you` | `Вы` | Default member S38 |
| `driving_reports_empty_lead` | …Ничего не выдумываем. | **Replace** (P1) |
| `driving_reports_current_user` | `Я` | Align with «Вы» / product copy |
| `bg_refresh_title/body/hint` | exists | Reuse short tip; не клон Life360 |
| `family_day_journal_*` | exists | Date grammar fix P1 |

### Новые ключи (создать RU+EN до UI)

| Key | RU (канон) | EN (канон) | Wave |
|-----|------------|------------|------|
| `where_phone_refresh_location_a11y` | Обновить моё место | Refresh my location | A |
| `where_phone_accuracy_coarse_cta` | Включить точную геолокацию | Turn on Precise Location | A |
| `where_phone_accuracy_stale_hint` | Место могло устареть. Обновите точку. | Location may be outdated. Refresh. | A |
| `family_trip_ended_push_title` | Поездка завершена | Trip completed | C |
| `family_trip_ended_push_body` | %@ · %.1f км · до %d км/ч | %@ · %.1f km · up to %d km/h | C |
| `family_trip_map_track_a11y` | Маршрут поездки | Trip route | C |
| `family_trip_empty_honest` | Трек не записался. Проверьте «Всегда» и Движение. | Track wasn’t saved. Check Always + Motion. | C |
| `driving_reports_empty_lead` (replace) | Отчёт появится после реальной поездки. | A report appears after a real trip. | P1 |
| `driving_reports_report_cta` | Отчёт о реальной поездке | Real trip report | P1 |
| `driving_reports_done` | Готово | Done | P1 |
| `family_day_journal_from_date_fmt` | С %@ | From %@ | P1 |
| `family_day_journal_period_today` | Сегодня | Today | P1 |
| `family_day_journal_period_week` | Неделя | This week | P1 |
| `family_day_journal_period_custom` | Свой период | Custom range | P1 |
| `family_crash_tip_title` | Обнаружение аварий | Crash detection | P1 |
| `family_crash_tip_body` | Нужны: геолокация «Всегда», Движение и фитнес, уведомления. | Needs: Always location, Motion & Fitness, notifications. | P1 |
| `inbox_filter_tips` | Советы | Tips | P1 |
| `inbox_filter_offers` | Предложения | Offers | P1 |
| `inbox_filter_notifications` | Уведомления | Notifications | P1 |
| `inbox_filter_all` | Все | All | P1 |

Перед закрытием `uxqa-loc-verify`: grep UI на `Text("snake_case` / raw keys; оба lproj; verify script OK.

---

## GATES (evidence)

1. S01–S06: один слой hero, ~80% орбиты, gap ≥10  
2. Strip A★ читается; кнопка «Добавить в семью»  
3. Поездка → push + polyline **или** честный error  
4. Accuracy честный; refresh = icon  
5. Trial = реальный `recoverableTrialEndDate`  
6. S15: нет «Ничего не выдумываем»; Готово работает  
7. S37: фото выбирается  
8. Device QA — владелец  

---

## Закрытие задачи

1. REGISTRY ✅  
2. PLAN checklist ✅  
3. Cursor TodoWrite `merge: true` на `uxqa-*`  
4. Отчёт: сделано / proofs / риски / нужен GO  
