# BATCH UX FIX — TODO tracker

> Обновляй статусы по мере работы. Полный план: `docs/FIX_BATCH_UX_P0_PLAN.md`

## Batch A — Family Tournament (P0)

- [x] **A1** `project.pbxproj`: file ref `FamilyTournamentView` → `Screens/FamilyTournamentView.swift`
- [x] **A2** Исключить/удалить `Screens/Views/FamilyTournamentView.swift` из target
- [x] **A3** Добавить ключи `join_tournament`, `loading_leaderboard` (RU + EN) в `LocalizationManager`
- [ ] **A4** Smoke: RU заголовок «Турнир семьи», кнопка ←, нет Mom/Dad/1247
- [ ] **A5** Smoke: API или empty state (не fake leaderboard)

## Batch B — Onboarding OB_02 (P0)

- [x] **B1** `14_OnboardingScreen.swift` case 1: `title.y` 412 → 384
- [x] **B2** При необходимости scrim y −28pt (504 → 476)
- [ ] **B3** Visual check iPhone SE + 15 Pro

## Batch C — Child Rewards CancellationError (P1)

- [x] **C1** Заменить `onAppear`+`Task` на `.task(id: effectiveChildId)`
- [x] **C2** `isIgnorableLoadError` в ViewModel + Screen
- [x] **C3** Маппинг `NetworkError.timeout` → `child_rewards_error_generic`
- [ ] **C4** Smoke: быстрый back — нет баннера
- [ ] **C5** Smoke: offline 15s — RU сообщение + Retry

## Batch D — AI copy (P2)

- [x] **D1** `ai_consent_banner_title` → «Умный помощник офлайн — включите в Настройках»
- [x] **D2** `ai_error_consent_required` + `AIOutboundTextGate` синхрон
- [x] **D3** EN-аналоги
- [x] **D4** `ai_data_sharing_title` + `05_SettingsScreen` без хардкода

## Batch E — Dark Web prod-only (P1)

- [x] **E1** Backend: `dark-web/stats` + leaks с `WHERE user_id` / family scope
- [x] **E2** Backend: breach vs scan-event — `source NOT IN (scan_*)` в stats/list
- [x] **E3** iOS: убрать stats из `applyFrom` в `DarkWebMonitoringModal`
- [x] **E4** iOS: empty state 0 + CTA scan + source label + `/leaks/list` + `user_id`
- [x] **E5** Server audit: 35 rows = scan_start 19 + scan_secure 9 + scan_fast 6 + haveibeenpwned 1 (все `new`, без `user_id` до миграции)
- [x] **E6** Smoke prod: `stats` без/с `user_id` → `0/0/0`; `leaks/list` → `[]` (деплой `reports_router.py` 2026-06-07)

---

**Текущий фокус:** follow-up — `user_id` в INSERT scan/breach + backfill HIBP  
**Последнее обновление:** 2026-06-07 — E5/E6 на prod, миграция `user_id` на `darkweb.darkweb_leaks`
