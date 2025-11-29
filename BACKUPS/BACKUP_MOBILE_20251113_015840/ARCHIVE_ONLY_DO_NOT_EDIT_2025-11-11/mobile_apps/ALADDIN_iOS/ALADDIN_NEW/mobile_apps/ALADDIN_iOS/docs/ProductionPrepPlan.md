### 3.1 Analytics
1. Согласовать с backend JSON-схемы для `/api/security/unified-dashboard` и `/api/security/unified-stats` (выполнено 2025-11-10, см. `security/api/mobile_api_endpoints.py`).
2. Реализовать запросы в `RemoteAnalyticsService` (GET, токены из Keychain/UserDefaults, конвертация категорий угроз) — **внедрено**, fallback оставлен только для второстепенных блоков.
3. Подключить `AnalyticsViewModel` к сети, убрать прямое использование `LocalAnalyticsService` (остались только резервные данные для пустых полей — удалить после валидации API).
4. Написать unit- и интеграционные тесты (✅ unit-тесты `RemoteAnalyticsServiceTests` добавлены; ⚠️ `xcodebuild test` не выполняется из-за отсутствия test-action в схеме — требуется настройка Xcode).

| plan-analytics | Подключить реальный Analytics API | in_progress |
| plan-notifications | Реализовать RemoteNotificationsService | pending |
| plan-child-rewards | Реализовать ChildRewardsService | pending |
| plan-localization-cleanup | Очистить неиспользуемые ключи | completed |
| plan-qa | Подготовить QA чеклист | pending |

- Выполнить QA чеклист: авторизация, аналitika, уведомления, награды, оффлайн, обработка ошибок.  
- Подготовить релизную сборку, обновить документацию и скриншоты (App Store).
