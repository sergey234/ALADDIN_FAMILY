# DOC ↔ CODE Audit Diff (Advanced/Settings) — 2026-03-23

Цель: сверить утверждения из актуального списка изменений с фактическим состоянием репозитория.

Статусы:
- `PASS` — подтверждено кодом/доками в репозитории.
- `PARTIAL` — подтверждено частично (нужна внешняя verify-цепочка или runtime-подтверждение).
- `MISSING` — подтверждение не найдено.

## Audit Matrix

| # | Пункт | Статус | Доказательство (файлы) | Комментарий |
|---|---|---|---|---|
| 1 | `COMPONENT_TOGGLES_FIX_REPORT_20260322.md` и `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` согласованы по цифрам и логике | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md`, `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` | В SSOT есть блоки про 39 + 25 = 64, Release Notes 2026-03-23 |
| 2 | Анализ логов по этапам 3/4 (Advanced), где PASS и где нужна verify-цепочка | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md` | Зафиксированы PASS-метрики и operational verify-цепочка |
| 3 | TODO-план по Advanced (Safari, parental, time-management, автопроверки, GO/STOP) сформирован и вёлся | PASS | `docs/server/ADVANCED_SETTINGS_GO_STOP_CHECKLIST_20260323.md`, `docs/server/test_advanced_settings_smoke.py`, `docs/server/test_advanced_settings_smoke.sh` | План и gate-логика оформлены как checklist + smoke |
| 4 | Найдена корневая причина Safari Apply: невалидный `content_blocker_manager` | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md` | Причина явно описана в отчёте |
| 5 | Исправлен Safari componentId на валидный `browser_security_bot` | PASS | `Components/Modals/FamilyContentBlockModal.swift`, `Screens/AdvancedProtectionSettingsScreen.swift` | В коде используется `browser_security_bot`, старого id в `*.swift` не найдено |
| 6 | Добавлен mini-log Safari apply (`start / ok / failed`) | PASS | `Components/Modals/FamilyContentBlockModal.swift` | Логи `SAFARI APPLY start/ok/failed` присутствуют |
| 7 | Усилено логирование parental-тумблеров (`parental_messages_monitoring`, `parental_screenshots_enabled`) | PASS | `Screens/AdvancedProtectionSettingsScreen.swift` | Есть UI-логи для обоих toggles |
| 8 | Добавлен server-sync для 2 parental-тумблеров: GET при входе/возврате, POST с debounce, API-логи | PASS | `Screens/AdvancedProtectionSettingsScreen.swift` | Есть `loadParentalMonitoringSettingsFromServer`, `scheduleParentalMonitoringSync`, `Task.sleep` debounce, POST start/ok/failed |
| 9 | Добавлен server-sync в time/family модалках (`schedule`, `sleep`, `appLimits`) в `parental_control_bot` через configuration | PASS | `Screens/02_FamilyScreen.swift` | Все 3 модалки делают merge+POST в `parental_control_bot` и логируют API result |
| 10 | Убран остаточный reference `content_blocker_manager` в статус-проверке Safari модалки | PASS | `Components/Modals/FamilyContentBlockModal.swift` | Фактический id = `browser_security_bot`; глобальный поиск по `*.swift` старого id не показал |
| 11 | Многократная проверка `xcodebuild`, итоговая сборка PASS | PASS | `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md`, `docs/server/STAGE_5_1_FULL_RERUN_REPORT_20260321.md` | Дополнительно выполнен контрольный `xcodebuild` на текущем коммите: `BUILD SUCCEEDED` |
| 12 | Добавлен Python smoke `docs/server/test_advanced_settings_smoke.py` | PASS | `docs/server/test_advanced_settings_smoke.py` | Скрипт есть, покрывает Safari/Parental/Time management |
| 13 | Добавлен Bash smoke (curl-only, цветной GO/STOP) `docs/server/test_advanced_settings_smoke.sh` | PASS | `docs/server/test_advanced_settings_smoke.sh` | Скрипт есть, содержит GO/STOP и проверки через `jq` |
| 14 | Добавлен release-checklist `docs/server/ADVANCED_SETTINGS_GO_STOP_CHECKLIST_20260323.md` | PASS | `docs/server/ADVANCED_SETTINGS_GO_STOP_CHECKLIST_20260323.md` | Чеклист есть, включает manual+server verify шаги |
| 15 | Даны компактные ручные curl-команды для Safari / Parental monitoring / Time management | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md`, `docs/server/test_advanced_settings_smoke.sh` | Команды и шаблоны запросов зафиксированы |
| 16 | Обновлён основной отчёт по тумблерам с «как было/как стало», метриками, новыми этапами | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md` | Есть разделы 5.4, метрики успеха, этапность |
| 17 | Исправлен подсчёт: базовые 39 + доп. 25 = 64 | PASS | `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md`, `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` | Числа синхронизированы в обоих документах |
| 18 | SSOT синхронизирован: `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` обновлён до 64/64 + release notes 2026-03-23 | PASS | `ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md` | Есть Operational Checklists + Release Notes (2026-03-23) |
| 19 | TODO-статусы по выполненным пунктам закрыты/актуализированы | PASS | `docs/server/ADVANCED_SETTINGS_GO_STOP_CHECKLIST_20260323.md`, `docs/server/COMPONENT_TOGGLES_FIX_REPORT_20260322.md` | Статусы и критерии завершения зафиксированы в релиз-чеклисте и основном отчёте |

## Итог аудита

- `PASS`: 19
- `PARTIAL`: 0
- `MISSING`: 0

## Verification Evidence

Контрольная сборка, выполненная в рамках этого аудита:

- Команда:
  - `xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build`
- Результат:
  - `** BUILD SUCCEEDED **`
- Лог прогона:
  - `/tmp/aladdin_xcodebuild_20260323.log`

Рекомендуемый финальный релиз-гейт (runtime):
1) Прогон `python3 docs/server/test_advanced_settings_smoke.py` на целевом окружении.
2) Ручной mini-log чек по checklist (`SAFARI APPLY`, parental POST, schedule/sleep/appLimits POST).
