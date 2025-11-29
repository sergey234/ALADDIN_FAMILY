# Notifications Integration Handoff

## 1. Что уже сделано
- **Бэкенд**
  - Добавлен роутер `security/api/routers/notifications_router.py` (регистрация в `mobile_api_endpoints.py`).
  - Возвращает структуру `{ notifications: [...], unread_count }`, каждая запись содержит `id`, `icon`, `title`, `message`, `timestamp`, `type`, `is_read`, `priority`, `action_required`, `action_url`, `metadata`.
  - При первом запуске создаёт демо-уведомления через `_ensure_seed_notifications`, чтобы фронт не отображал пустой список.
  - Менеджер `family_notification_manager_enhanced` расширен методами `get_notifications_for_family`, `mark_notification_as_read`, `mark_all_notifications_as_read`.

- **iOS**
  - Новый сервис `Core/Notifications/RemoteNotificationsService.swift` (async/await, авторизация, snake_case↔camelCase).
  - `ViewModels/NotificationsViewModel.swift` переписан под сервис: реальные данные, fallback только при ошибке, сохранены фильтры, добавлена работа с метаданными.
  - Экран `Screens/12_NotificationsScreen.swift` адаптирован под `AppNotification.kind`, счётчики и цветовые индикаторы используют новые модели.
  - План (`docs/ProductionPrepPlan.md`) и глобальный TODO обновлены, `plan-notifications` закрыт.

## 2. Что осталось выполнить
1. **Локализация**
   - Просмотреть блок `notifications_*` в `Core/Localization/LocalizationManager.swift`.
   - Архивировать ключи, которые больше не используются после упрощения экрана.
   - Выровнять пары RU ↔ EN для актуальных уведомлений (остальные языки — позже, по стратегии пользователя).

2. **Качество и тесты**
   - Прогнать:
     ```bash
     cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
     python3 scripts/advanced_quality_check.py --target mobile_apps/ALADDIN_iOS
     ```
   - Собрать и запустить симулятор iPhone 13:
     ```bash
     xcodebuild clean build -scheme ALADDIN -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 13'
     ```
   - Проверить экран уведомлений (фильтры, отметка «прочитано», fallback при отключённой сети).

3. **Документация**
   - По итогам очистки локализации и QA обновить `ProductionPrepPlan.md` (секция 4) и зафиксировать фактические результаты.
   - Если появятся новые строки локализации, внести их в `LocalizationProcessInstruction.md`.

## 3. Полезные ссылки
- Бэкенд: `security/api/routers/notifications_router.py`, регистрация — `mobile_api_endpoints.py`.
- iOS: `Core/Notifications/RemoteNotificationsService.swift`, `ViewModels/NotificationsViewModel.swift`, `Screens/12_NotificationsScreen.swift`.
- План: `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/ProductionPrepPlan.md` (секции 1, 3.2, 5).

## 4. Примечания для следующей ML-системы
- Токен авторизации берётся из Keychain (`KeychainManager.authToken`), при отсутствии — из `AppConfig.authToken`.
- При тестировании учитывайте, что роутер задаёт демо-данные: это нормально до полного подключения внешнего источника.
- После локализационной чистки загоните `check_localization_duplicates.py` и `check_localization_keysets.py` (только RU/EN, как договорено ранее).
- Следующий крупный этап по плану — Child Rewards: не начинался, но связан с аналогичной заменой моков.

