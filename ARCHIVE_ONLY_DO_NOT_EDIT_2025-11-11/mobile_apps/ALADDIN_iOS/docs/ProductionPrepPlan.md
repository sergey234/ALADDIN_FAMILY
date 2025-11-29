# План подготовки ALADDIN iOS к продакшену

## 1. Текущее состояние

- **UI и ViewModel**  
  Экраны реализованы, навигация работает. Большинство данных подставляется из локальных моков.

- **Сеть**  
  `NetworkManager` настроен, SSL pinning включён (нужно добавить сертификаты в бандл).  
  Реальные вызовы подключены для `RemoteAnalyticsService` и `RemoteNotificationsService`, `ChildRewardsService` пока остаётся на мок-данных.

- **Локализация**  
  Русский язык готов. Английский выровнен для ключевых экранов (профиль, добавление участника, согласие, оплата).  
  `analytics_*`, `notifications_*`, `child_rewards_*` содержат лишние ключи — нужно очистить после подключения реальных данных.  
  Китайский и арабский временно не используются.

## 2. Что нужно убрать / привести в порядок

1. Очистить `LocalizationManager.swift` от неиспользуемых ключей (особенно `analytics_*`, `notifications_*`, `child_rewards_*`).  
2. Добавить SSL-сертификаты (`aladdin_cert.cer`, `aladdin_cert_backup.cer`) в Target Membership.  
3. Удалить моковые провайдеры данных из ViewModel после подключения реальных сервисов.  
4. Подготовить QA чеклист (статусы сетевых вызовов, обработка ошибок, fallback переводов).

## 3. Настоящее подключение данных (пошагово)

### 3.1 Analytics
1. Согласовать с backend JSON-схемы:  
   `/analytics/summary`, `/analytics/security`, `/analytics/family`, `/analytics/usage`, `/analytics/devices`.
2. Реализовать запросы в `RemoteAnalyticsService` (URLRequest, токены, декодирование).  
3. Подключить `AnalyticsViewModel` к сети, убрать fallback на `LocalAnalyticsService`.  
4. Написать unit- и интеграционные тесты.

### 3.2 Notifications
1. Создать `RemoteNotificationsService` (GET `/notifications`, POST `/notifications/{id}/read`). ✅ Реализовано: `Core/Notifications/RemoteNotificationsService.swift`.  
2. Обновить `NotificationsViewModel`, удалить статические данные. ✅ ViewModel теперь использует async/await и реальный API.  
3. Проверить UI и ошибки. ✅ Экран работает на реальных данных (моки оставлены только как offline fallback).  
4. Локализация и QA. ⏳ Требуется дочистить `notifications_*` ключи (RU ↔ EN), прогнать `advanced_quality_check.py` и smoke-тест на симуляторе.

### 3.3 Child Rewards
1. Описать API: список наград, история, операции.  
2. Реализовать `ChildRewardsService`, переписать `ChildRewardsViewModel`.  
3. Тесты: «выдать награду», «списать», «посмотреть историю».

## 4. Финальные шаги перед релизом

- Прогнать `check_localization_duplicates.py` и `check_localization_keysets.py` (только RU/EN) — статус OK.  
- Проверить работу приложения на английском (fallback).  
- Выполнить QA чеклист: авторизация, аналitika, уведомления, награды, оффлайн, обработка ошибок.  
- Сохранять результаты прогона в `docs/QAReports/SmokeTestRun_2025-11-11.md` (создавать новый файл для следующих дат).  
- Подготовить релизную сборку, обновить документацию и скриншоты (App Store).

## 5. TODO-лист

| ID | Задача | Статус |
|----|--------|--------|
| task-1 | Review localization duplicates | completed |
| task-2 | Fix localization duplicates | completed |
| task-3 | Run localization validation scripts (old) | cancelled |
| task-4 | Sync payment QR translations | completed |
| task-5 | Align analytics-related localization keys | pending |
| task-6 | zh/ar fallback strategy | cancelled |
| plan-analytics | Подключить реальный Analytics API | completed |
| plan-notifications | Реализовать RemoteNotificationsService | completed |
| plan-child-rewards | Реализовать ChildRewardsService | pending |
| plan-localization-cleanup | Очистить неиспользуемые ключи | completed |
| plan-qa | Подготовить QA чеклист | in_progress |

При выполнении задач обновлять статусы через `todo_write`, чтобы следующая система видела прогресс.


