# 📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ ENDPOINT'ОВ

**Дата:** 2026-02-11 23:44:38
**Base URL:** http://149.154.65.180:8002
**Family ID:** FAM_EBFDF1EDB7FA

## 📈 СТАТИСТИКА

- **Всего endpoint'ов:** 238
- **✅ Успешно:** 223
- **❌ Ошибки:** 14
- **⏭️ Пропущено:** 1
- **🔐 Требуют авторизацию:** 19
- **🌐 Публичные:** 218

**Процент успеха:** 93.7%

### 📊 Статусы HTTP:

- **200 OK:** 102
- **201 Created:** 0
- **204 No Content:** 0
- **401 Unauthorized:** 0
- **403 Forbidden:** 0
- **404 Not Found:** 9
- **422 Validation Error:** 121
- **500+ Server Error:** 5

### ⚡ Производительность:

- **✅ Быстрые (< 2000ms):** 237
- **🐌 Медленные (> 2000ms):** 0

### 🔒 Безопасность:

- **✅ Без проблем:** 0
- **⚠️ Проблемы:** 237

### ✅ Валидация:

- **✅ Без проблем:** 116
- **⚠️ Проблемы:** 121

## ✅ ДЕТАЛЬНЫЙ АНАЛИЗ 422 (VALIDATION ERROR)

**Всего:** 121

| Метод | Путь | Проблемы валидации |
|-------|------|-------------------|
| post | `/api/auth/login` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/auth/register` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/auth/refresh` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/auth/login-by-recovery-code` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/referral/test/payment/create` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| post | `/api/referral/test/payment/confirm` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| get | `/api/referral/test/discount/apply` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/payments/create` | Ошибки валидации: 6 полей; Типы ошибок: {'missing': 6} |
| post | `/api/payments/confirm` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/payments/recover` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/activation/retrieve` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/components/configuration/{component_id}` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/components/batch/status` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/protection/settings` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/protection/enable` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/protection/disable` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/protection/sync` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/family/create` | Ошибки валидации: 4 полей; Типы ошибок: {'missing': 4} |
| post | `/api/reports/ai-categories/allow` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/reports/ai-categories/block` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/reports/privacy/tracker/whitelist` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/crash-detection/setup` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/crash-detection/alert` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| post | `/api/crash-detection/data` | Ошибки валидации: 4 полей; Типы ошибок: {'missing': 4} |
| post | `/reports/privacy/location/bubble` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/reports/privacy/location/send` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| post | `/api/reports/dark-web/resolve` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/reports/identity-theft/allow` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/reports/identity-theft/block` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/reports/identity-theft/whitelist` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/reports/privacy/location/allow` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/reports/privacy/location/block` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/reports/privacy/location/update-accuracy` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/roadside-assistance/call` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| get | `/api/roadside-assistance/history` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/notifications/read` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/notifications/bulk_mark_read` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| put | `/api/notifications/preferences` | Ошибки валидации: 5 полей; Типы ошибок: {'missing': 5} |
| get | `/api/notifications/search` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/ai/assistant/chat` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/ai/assistant/feedback` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/ai/assistant/analyze_threat` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/ai/assistant/report_incident` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/components/config/update/{component_id}` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/system/maintenance` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/balance/add` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/gamification/balance/subtract` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/gamification/rewards/claim` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/gamification/rewards/history` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/rewards/give` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/gamification/rewards/purchase` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/gamification/achievements` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/achievements/unlock` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/gamification/achievements/progress` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/achievements/claim` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/gamification/tournaments/join` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/gamification/tournaments/leave` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/gamification/settings` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/settings/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/gamification/settings/notifications` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/settings/notifications/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/gamification/progress` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/progress/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/gamification/progress/stats` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/gamification/progress/level` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/gamification/progress/reset` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/parental-control/settings/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/settings/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/parental-control/time-limits/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/time-limits/reset` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/schedules/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/schedules/delete` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/geofences/add` | Ошибки валидации: 5 полей; Типы ошибок: {'missing': 5} |
| post | `/api/parental-control/geofences/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/app-blocks/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/parental-control/app-blocks/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/user/profile/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/user/profile/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/user/profile/history` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/user/profile/privacy` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/user/profile/privacy/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/subscription/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/subscription/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/subscription/purchase-history` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/subscription/status` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/subscription/status/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/subscription/auto-renewal` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/subscription/auto-renewal/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/subscription/cancel` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/settings/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/settings/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/settings/theme` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/settings/theme/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/settings/language` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/settings/language/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/settings/notifications` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/settings/notifications/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/settings/biometry` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/settings/biometry/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/location/geofences/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/location/geofences/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| get | `/api/location/movement-history` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/location/movement-history/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/location/status` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/location/status/update` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/chat/offline-messages/sync` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| post | `/api/chat/offline-messages/send` | Ошибки валидации: 4 полей; Типы ошибок: {'missing': 4} |
| post | `/api/chat/offline-messages/resolve-conflicts` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| post | `/api/offline-storage/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| get | `/api/offline-storage/data` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/offline-storage/data/update` | Ошибки валидации: 3 полей; Типы ошибок: {'missing': 3} |
| delete | `/api/offline-storage/data/{dataId}` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/offline-storage/resolve-conflicts` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/crash-detection/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/crash-detection/report` | Ошибки валидации: 4 полей; Типы ошибок: {'missing': 4} |
| get | `/api/crash-detection/notifications` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/crash-detection/notifications/send` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/elderly/medications/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/elderly/medications/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |
| post | `/api/elderly/appointments/sync` | Ошибки валидации: 2 полей; Типы ошибок: {'missing': 2} |
| post | `/api/elderly/appointments/update` | Ошибки валидации: 1 полей; Типы ошибок: {'missing': 1} |

## ❌ ДЕТАЛЬНЫЙ АНАЛИЗ 404 (NOT FOUND)

**Всего:** 9

| Метод | Путь | Причина | Действие |
|-------|------|---------|----------|
| get | `/api/payments/status/{payment_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| get | `/api/components/status/{component_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| post | `/api/components/enable/{component_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| post | `/api/components/disable/{component_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| get | `/api/components/configuration/{component_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| get | `/api/roadside-assistance/status/{request_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| post | `/api/notifications/mark_read/{notification_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| post | `/api/notifications/delete/{notification_id}` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |
| get | `/api/components/status/all` | Not Found - endpoint не найден | Проверить правильность пути или подключение роутер |

## 🔒 ПРОБЛЕМЫ БЕЗОПАСНОСТИ

**Всего:** 237

| Метод | Путь | Проблемы | Оценка |
|-------|------|----------|--------|
| post | `/api/auth/login` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 55/100 |
| post | `/api/auth/register` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 55/100 |
| post | `/api/auth/refresh` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 55/100 |
| post | `/api/auth/login-by-recovery-code` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/auth/logout` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/referral/code` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/referral/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/referral/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/referral/rewards` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/referral/test/payment/create` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/referral/test/payment/confirm` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/referral/test/discount/apply` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/payments/create` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/payments/status/{payment_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/payments/confirm` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/payments/recover` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/activation/retrieve` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/components/status/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/components/enable/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/components/disable/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/components/configuration/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/components/configuration/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/components/batch/status` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/protection/settings` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/protection/settings` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/protection/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/protection/threat-scenarios` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/protection/enable` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/protection/disable` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/protection/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/protection/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/family/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/family/create` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/ai-categories/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/ai-categories/reports` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/ai-categories/allow` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/ai-categories/block` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/ai-categories/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/tracker/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/tracker/top` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/privacy/tracker/whitelist` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/privacy/tracker/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/crash-detection/setup` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/alert` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/start` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/stop` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/data` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/crash-detection/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/reports/privacy/location/bubble` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/reports/privacy/location/send` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/dark-web/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/dark-web/leaks` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/dark-web/scans` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/dark-web/resolve` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/dark-web/scan/start` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/dark-web/scan/secure` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/dark-web/scan/fast` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/dark-web/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/cleanup/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/cleanup/records` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/privacy/cleanup/start` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/privacy/cleanup/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/identity-theft/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/identity-theft/attempts` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/identity-theft/allow` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/identity-theft/block` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/identity-theft/whitelist` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/identity-theft/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/location/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/privacy/location/requests` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/reports/privacy/location/allow` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/privacy/location/block` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/reports/privacy/location/update-accuracy` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/privacy/location/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/roadside-assistance/call` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/roadside-assistance/status/{request_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/roadside-assistance/cancel/{request_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/roadside-assistance/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/roadside-assistance/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/v1/parental-control/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/v1/parental-control/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/parental/bypass/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/parental/bypass/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/iot/status/{homeId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/iot/devices/{homeId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/iot/threats/{homeId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/iot/device/{deviceId}/block` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/iot/scan/{homeId}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/iot/fix/{threatId}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/reports/driving/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/driving/export` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/reports/driving/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/notifications` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/notifications/read` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/notifications/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/notifications/unread_count` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/notifications/mark_read/{notification_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/delete/{notification_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/bulk_mark_read` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/test` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| put | `/api/notifications/settings` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/notifications/categories` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/notifications/preferences` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| put | `/api/notifications/preferences` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/clear_all` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/archive/{notification_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/notifications/unarchive/{notification_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/notifications/filter` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/notifications/search` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/notifications/export` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/ai/assistant/chat` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/ai/assistant/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/ai/assistant/feedback` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/ai/assistant/capabilities` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/ai/assistant/analyze_threat` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/ai/assistant/recommendations` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/ai/assistant/report_incident` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/ai/assistant/security_tips` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/list` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/status/all` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/config/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/components/config/update/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/components/restart/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/components/metrics/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/logs/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/components/dependencies/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/components/test/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/components/update/{component_id}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/system/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/system/info` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/system/logs` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/system/maintenance` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/system/metrics` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/system/backup` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/system/backup/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/system/uptime` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/system/version` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/system/restart` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/system/resources` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/balance/{userId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/balance/add` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/gamification/balance/subtract` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/balance/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/rewards` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/rewards/claim` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/rewards/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/rewards/give` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/rewards/shop` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/rewards/purchase` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/achievements` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/achievements/unlock` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/achievements/progress` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/achievements/{achievementId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/achievements/claim` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/tournaments` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/tournaments/join` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/tournaments/{tournamentId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/tournaments/leaderboard` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/tournaments/leave` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/tournaments/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/settings` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/settings/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/settings/notifications` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/settings/notifications/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/progress` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/progress/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/gamification/progress/stats` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/gamification/progress/level` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/gamification/progress/reset` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/settings/{familyId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/settings/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/settings/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/settings/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/settings/conflicts` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/parental-control/time-limits/{childId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/time-limits/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/time-limits/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/time-limits/reset` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/schedules/{childId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/schedules/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/schedules/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/schedules/delete` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/geofences/{childId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/geofences/add` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/parental-control/geofences/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| delete | `/api/parental-control/geofences/{geofenceId}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/parental-control/app-blocks/{childId}` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/parental-control/app-blocks/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/parental-control/app-blocks/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/user/profile/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/user/profile/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/user/profile/history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/user/profile/privacy` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/user/profile/privacy/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/subscription/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/subscription/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/subscription/purchase-history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| get | `/api/subscription/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/subscription/status/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/subscription/auto-renewal` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/subscription/auto-renewal/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/subscription/cancel` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/settings/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/settings/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/settings/theme` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/settings/theme/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/settings/language` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/settings/language/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/settings/notifications` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/settings/notifications/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/settings/biometry` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/settings/biometry/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/location/geofences/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/location/geofences/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| delete | `/api/location/geofences/{geofenceId}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/location/movement-history` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/location/movement-history/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/location/status` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/location/status/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/chat/offline-messages/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/chat/offline-messages/send` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/chat/offline-messages/resolve-conflicts` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/offline-storage/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/offline-storage/data` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/offline-storage/data/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| delete | `/api/offline-storage/data/{dataId}` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/offline-storage/resolve-conflicts` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/crash-detection/report` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/crash-detection/notifications` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |
| post | `/api/crash-detection/notifications/send` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/elderly/medications/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/elderly/medications/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/elderly/appointments/sync` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| post | `/api/elderly/appointments/update` | Используется HTTP вместо HTTPS; Нет защиты от CSRF | 75/100 |
| get | `/api/health` | Используется HTTP вместо HTTPS; Нет защиты от XSS | 80/100 |

## 📋 ВСЕ РЕЗУЛЬТАТЫ

| Метод | Путь | Статус | HTTP | Время (мс) | Производительность | Безопасность | Валидация |
|-------|------|--------|------|------------|-------------------|--------------|-----------|
| POST | `/api/auth/login` | ⚠️ validation_error | 422 | 30.29 | ✅ | 55/100 | ⚠️ |
| POST | `/api/auth/register` | ⚠️ validation_error | 422 | 28.78 | ✅ | 55/100 | ⚠️ |
| POST | `/api/auth/refresh` | ⚠️ validation_error | 422 | 28.06 | ✅ | 55/100 | ⚠️ |
| POST | `/api/auth/login-by-recovery-code` | ⚠️ validation_error | 422 | 25.5 | ✅ | 75/100 | ⚠️ |
| POST | `/api/auth/logout` | ✅ success | 200 | 26.47 | ✅ | 75/100 | ✅ |
| GET | `/api/referral/code` | ❌ server_error | 500 | 34.5 | ✅ | 80/100 | ✅ |
| GET | `/api/referral/stats` | ❌ server_error | 500 | 71.14 | ✅ | 80/100 | ✅ |
| GET | `/api/referral/history` | ❌ server_error | 500 | 125.99 | ✅ | 80/100 | ✅ |
| GET | `/api/referral/rewards` | ❌ server_error | 500 | 60.47 | ✅ | 80/100 | ✅ |
| POST | `/api/referral/test/payment/create` | ⚠️ validation_error | 422 | 62.26 | ✅ | 75/100 | ⚠️ |
| POST | `/api/referral/test/payment/confirm` | ⚠️ validation_error | 422 | 25.73 | ✅ | 75/100 | ⚠️ |
| GET | `/api/referral/test/discount/apply` | ⚠️ validation_error | 422 | 26.6 | ✅ | 80/100 | ⚠️ |
| POST | `/api/payments/create` | ⚠️ validation_error | 422 | 27.73 | ✅ | 75/100 | ⚠️ |
| GET | `/api/payments/status/{payment_id}` | ❌ not_found | 404 | 47.06 | ✅ | 80/100 | ✅ |
| POST | `/api/payments/confirm` | ⚠️ validation_error | 422 | 28.68 | ✅ | 75/100 | ⚠️ |
| POST | `/api/payments/recover` | ⚠️ validation_error | 422 | 26.35 | ✅ | 75/100 | ⚠️ |
| POST | `/api/activation/retrieve` | ⚠️ validation_error | 422 | 38.47 | ✅ | 75/100 | ⚠️ |
| GET | `/api/components/status/{component_id}` | ❌ not_found | 404 | 28.73 | ✅ | 80/100 | ✅ |
| POST | `/api/components/enable/{component_id}` | ❌ not_found | 404 | 33.63 | ✅ | 75/100 | ✅ |
| POST | `/api/components/disable/{component_id}` | ❌ not_found | 404 | 28.97 | ✅ | 75/100 | ✅ |
| GET | `/api/components/configuration/{component_id}` | ❌ not_found | 404 | 30.18 | ✅ | 80/100 | ✅ |
| POST | `/api/components/configuration/{component_id}` | ⚠️ validation_error | 422 | 30.87 | ✅ | 75/100 | ⚠️ |
| POST | `/api/components/batch/status` | ⚠️ validation_error | 422 | 30.21 | ✅ | 75/100 | ⚠️ |
| GET | `/api/protection/settings` | ✅ success | 200 | 38.58 | ✅ | 80/100 | ✅ |
| POST | `/api/protection/settings` | ⚠️ validation_error | 422 | 28.06 | ✅ | 75/100 | ⚠️ |
| GET | `/api/protection/status` | ✅ success | 200 | 30.69 | ✅ | 80/100 | ✅ |
| GET | `/api/protection/threat-scenarios` | ✅ success | 200 | 28.27 | ✅ | 80/100 | ✅ |
| POST | `/api/protection/enable` | ⚠️ validation_error | 422 | 28.16 | ✅ | 75/100 | ⚠️ |
| POST | `/api/protection/disable` | ⚠️ validation_error | 422 | 29.22 | ✅ | 75/100 | ⚠️ |
| GET | `/api/protection/stats` | ✅ success | 200 | 30.32 | ✅ | 80/100 | ✅ |
| POST | `/api/protection/sync` | ⚠️ validation_error | 422 | 29.0 | ✅ | 75/100 | ⚠️ |
| GET | `/api/family/stats` | ✅ success | 200 | 31.67 | ✅ | 80/100 | ✅ |
| POST | `/api/family/create` | ⚠️ validation_error | 422 | 27.43 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/ai-categories/stats` | ✅ success | 200 | 27.06 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/ai-categories/reports` | ✅ success | 200 | 27.83 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/ai-categories/allow` | ⚠️ validation_error | 422 | 26.31 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/ai-categories/block` | ⚠️ validation_error | 422 | 25.83 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/ai-categories/health` | ✅ success | 200 | 27.02 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/tracker/stats` | ✅ success | 200 | 41.02 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/tracker/top` | ✅ success | 200 | 30.8 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/privacy/tracker/whitelist` | ⚠️ validation_error | 422 | 26.33 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/privacy/tracker/health` | ✅ success | 200 | 27.15 | ✅ | 80/100 | ✅ |
| POST | `/api/crash-detection/setup` | ⚠️ validation_error | 422 | 27.57 | ✅ | 75/100 | ⚠️ |
| POST | `/api/crash-detection/alert` | ⚠️ validation_error | 422 | 28.69 | ✅ | 75/100 | ⚠️ |
| POST | `/api/crash-detection/start` | ✅ success | 200 | 26.51 | ✅ | 75/100 | ✅ |
| POST | `/api/crash-detection/stop` | ✅ success | 200 | 25.6 | ✅ | 75/100 | ✅ |
| POST | `/api/crash-detection/data` | ⚠️ validation_error | 422 | 28.02 | ✅ | 75/100 | ⚠️ |
| GET | `/api/crash-detection/status` | ✅ success | 200 | 27.78 | ✅ | 80/100 | ✅ |
| POST | `/reports/privacy/location/bubble` | ⚠️ validation_error | 422 | 27.4 | ✅ | 75/100 | ⚠️ |
| POST | `/reports/privacy/location/send` | ⚠️ validation_error | 422 | 27.51 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/dark-web/stats` | ✅ success | 200 | 29.91 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/dark-web/leaks` | ✅ success | 200 | 25.83 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/dark-web/scans` | ✅ success | 200 | 27.84 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/dark-web/resolve` | ⚠️ validation_error | 422 | 26.37 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/dark-web/scan/start` | ✅ success | 200 | 31.93 | ✅ | 75/100 | ✅ |
| POST | `/api/reports/dark-web/scan/secure` | ✅ success | 200 | 29.55 | ✅ | 75/100 | ✅ |
| POST | `/api/reports/dark-web/scan/fast` | ✅ success | 200 | 50.85 | ✅ | 75/100 | ✅ |
| GET | `/api/reports/dark-web/health` | ✅ success | 200 | 33.8 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/stats` | ✅ success | 200 | 28.74 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/records` | ✅ success | 200 | 37.82 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/privacy/cleanup/start` | ✅ success | 200 | 25.75 | ✅ | 75/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/health` | ✅ success | 200 | 30.69 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/identity-theft/stats` | ✅ success | 200 | 30.56 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/identity-theft/attempts` | ✅ success | 200 | 31.05 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/identity-theft/allow` | ⚠️ validation_error | 422 | 25.89 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/identity-theft/block` | ⚠️ validation_error | 422 | 26.84 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/identity-theft/whitelist` | ⚠️ validation_error | 422 | 33.21 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/identity-theft/health` | ✅ success | 200 | 27.62 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/location/stats` | ✅ success | 200 | 34.42 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/privacy/location/requests` | ✅ success | 200 | 28.51 | ✅ | 80/100 | ✅ |
| POST | `/api/reports/privacy/location/allow` | ⚠️ validation_error | 422 | 27.31 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/privacy/location/block` | ⚠️ validation_error | 422 | 27.16 | ✅ | 75/100 | ⚠️ |
| POST | `/api/reports/privacy/location/update-accuracy` | ⚠️ validation_error | 422 | 25.91 | ✅ | 75/100 | ⚠️ |
| GET | `/api/reports/privacy/location/health` | ✅ success | 200 | 28.11 | ✅ | 80/100 | ✅ |
| POST | `/api/roadside-assistance/call` | ⚠️ validation_error | 422 | 27.05 | ✅ | 75/100 | ⚠️ |
| GET | `/api/roadside-assistance/status/{request_id}` | ❌ not_found | 404 | 26.43 | ✅ | 80/100 | ✅ |
| POST | `/api/roadside-assistance/cancel/{request_id}` | ✅ success | 200 | 25.93 | ✅ | 75/100 | ✅ |
| GET | `/api/roadside-assistance/history` | ⚠️ validation_error | 422 | 27.81 | ✅ | 80/100 | ⚠️ |
| GET | `/api/roadside-assistance/health` | ✅ success | 200 | 27.47 | ✅ | 80/100 | ✅ |
| GET | `/api/v1/parental-control/stats` | ✅ success | 200 | 27.16 | ✅ | 80/100 | ✅ |
| GET | `/api/v1/parental-control/status` | ✅ success | 200 | 26.41 | ✅ | 80/100 | ✅ |
| GET | `/parental/bypass/stats` | ✅ success | 200 | 26.81 | ✅ | 80/100 | ✅ |
| GET | `/parental/bypass/status` | ✅ success | 200 | 27.04 | ✅ | 80/100 | ✅ |
| GET | `/api/iot/status/{homeId}` | ✅ success | 200 | 26.3 | ✅ | 80/100 | ✅ |
| GET | `/api/iot/devices/{homeId}` | ✅ success | 200 | 27.59 | ✅ | 80/100 | ✅ |
| GET | `/api/iot/threats/{homeId}` | ✅ success | 200 | 30.45 | ✅ | 80/100 | ✅ |
| POST | `/api/iot/device/{deviceId}/block` | ✅ success | 200 | 26.71 | ✅ | 75/100 | ✅ |
| POST | `/api/iot/scan/{homeId}` | ✅ success | 200 | 31.79 | ✅ | 75/100 | ✅ |
| POST | `/api/iot/fix/{threatId}` | ✅ success | 200 | 30.24 | ✅ | 75/100 | ✅ |
| GET | `/api/reports/driving/stats` | ✅ success | 200 | 26.5 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/driving/export` | ✅ success | 200 | 26.87 | ✅ | 80/100 | ✅ |
| GET | `/api/reports/driving/health` | ✅ success | 200 | 31.21 | ✅ | 80/100 | ✅ |
| GET | `/api/notifications` | ✅ success | 200 | 28.14 | ✅ | 80/100 | ✅ |
| POST | `/api/notifications/read` | ⚠️ validation_error | 422 | 25.12 | ✅ | 75/100 | ⚠️ |
| GET | `/api/notifications/stats` | ✅ success | 200 | 29.55 | ✅ | 80/100 | ✅ |
| GET | `/api/notifications/unread_count` | ✅ success | 200 | 25.53 | ✅ | 80/100 | ✅ |
| POST | `/api/notifications/mark_read/{notification_id}` | ❌ not_found | 404 | 32.22 | ✅ | 75/100 | ✅ |
| POST | `/api/notifications/delete/{notification_id}` | ❌ not_found | 404 | 27.32 | ✅ | 75/100 | ✅ |
| POST | `/api/notifications/bulk_mark_read` | ⚠️ validation_error | 422 | 28.43 | ✅ | 75/100 | ⚠️ |
| POST | `/api/notifications/test` | ❌ server_error | 500 | 32.22 | ✅ | 75/100 | ✅ |
| PUT | `/api/notifications/settings` | ✅ success | 200 | 57.66 | ✅ | 75/100 | ✅ |
| GET | `/api/notifications/categories` | ✅ success | 200 | 27.58 | ✅ | 80/100 | ✅ |
| GET | `/api/notifications/preferences` | ✅ success | 200 | 27.51 | ✅ | 80/100 | ✅ |
| PUT | `/api/notifications/preferences` | ⚠️ validation_error | 422 | 24.11 | ✅ | 75/100 | ⚠️ |
| POST | `/api/notifications/clear_all` | ✅ success | 200 | 32.49 | ✅ | 75/100 | ✅ |
| POST | `/api/notifications/archive/{notification_id}` | ✅ success | 200 | 33.14 | ✅ | 75/100 | ✅ |
| POST | `/api/notifications/unarchive/{notification_id}` | ✅ success | 200 | 27.34 | ✅ | 75/100 | ✅ |
| GET | `/api/notifications/filter` | ✅ success | 200 | 28.11 | ✅ | 80/100 | ✅ |
| GET | `/api/notifications/search` | ⚠️ validation_error | 422 | 25.57 | ✅ | 80/100 | ⚠️ |
| GET | `/api/notifications/export` | ✅ success | 200 | 27.78 | ✅ | 80/100 | ✅ |
| POST | `/api/ai/assistant/chat` | ⚠️ validation_error | 422 | 30.08 | ✅ | 75/100 | ⚠️ |
| GET | `/api/ai/assistant/history` | ✅ success | 200 | 27.85 | ✅ | 80/100 | ✅ |
| POST | `/api/ai/assistant/feedback` | ⚠️ validation_error | 422 | 28.12 | ✅ | 75/100 | ⚠️ |
| GET | `/api/ai/assistant/capabilities` | ✅ success | 200 | 25.0 | ✅ | 80/100 | ✅ |
| POST | `/api/ai/assistant/analyze_threat` | ⚠️ validation_error | 422 | 25.81 | ✅ | 75/100 | ⚠️ |
| GET | `/api/ai/assistant/recommendations` | ✅ success | 200 | 24.7 | ✅ | 80/100 | ✅ |
| POST | `/api/ai/assistant/report_incident` | ⚠️ validation_error | 422 | 29.35 | ✅ | 75/100 | ⚠️ |
| GET | `/api/ai/assistant/security_tips` | ✅ success | 200 | 26.1 | ✅ | 80/100 | ✅ |
| GET | `/api/components/health` | ✅ success | 200 | 26.51 | ✅ | 80/100 | ✅ |
| GET | `/api/components/list` | ✅ success | 200 | 27.28 | ✅ | 80/100 | ✅ |
| GET | `/api/components/status/all` | ❌ not_found | 404 | 26.63 | ✅ | 80/100 | ✅ |
| GET | `/api/components/config/{component_id}` | ✅ success | 200 | 31.73 | ✅ | 80/100 | ✅ |
| POST | `/api/components/config/update/{component_id}` | ⚠️ validation_error | 422 | 25.92 | ✅ | 75/100 | ⚠️ |
| POST | `/api/components/restart/{component_id}` | ✅ success | 200 | 26.38 | ✅ | 75/100 | ✅ |
| GET | `/api/components/metrics/{component_id}` | ✅ success | 200 | 26.27 | ✅ | 80/100 | ✅ |
| GET | `/api/components/logs/{component_id}` | ✅ success | 200 | 29.18 | ✅ | 80/100 | ✅ |
| GET | `/api/components/dependencies/{component_id}` | ✅ success | 200 | 32.74 | ✅ | 80/100 | ✅ |
| POST | `/api/components/test/{component_id}` | ✅ success | 200 | 27.17 | ✅ | 75/100 | ✅ |
| POST | `/api/components/update/{component_id}` | ✅ success | 200 | 26.28 | ✅ | 75/100 | ✅ |
| GET | `/api/system/health` | ✅ success | 200 | 29.33 | ✅ | 80/100 | ✅ |
| GET | `/api/system/info` | ✅ success | 200 | 43.43 | ✅ | 80/100 | ✅ |
| GET | `/api/system/logs` | ✅ success | 200 | 36.15 | ✅ | 80/100 | ✅ |
| POST | `/api/system/maintenance` | ⚠️ validation_error | 422 | 29.08 | ✅ | 75/100 | ⚠️ |
| GET | `/api/system/metrics` | ✅ success | 200 | 30.26 | ✅ | 80/100 | ✅ |
| POST | `/api/system/backup` | ✅ success | 200 | 27.31 | ✅ | 75/100 | ✅ |
| GET | `/api/system/backup/status` | ✅ success | 200 | 25.16 | ✅ | 80/100 | ✅ |
| GET | `/api/system/uptime` | ✅ success | 200 | 30.78 | ✅ | 80/100 | ✅ |
| GET | `/api/system/version` | ✅ success | 200 | 25.26 | ✅ | 80/100 | ✅ |
| POST | `/api/system/restart` | ✅ success | 200 | 29.08 | ✅ | 75/100 | ✅ |
| GET | `/api/system/resources` | ✅ success | 200 | 28.23 | ✅ | 80/100 | ✅ |
| GET | `/api/gamification/balance/{userId}` | ✅ success | 200 | 27.84 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/balance/add` | ⚠️ validation_error | 422 | 28.39 | ✅ | 75/100 | ⚠️ |
| POST | `/api/gamification/balance/subtract` | ⚠️ validation_error | 422 | 26.91 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/balance/history` | ✅ success | 200 | 26.78 | ✅ | 80/100 | ✅ |
| GET | `/api/gamification/rewards` | ✅ success | 200 | 26.5 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/rewards/claim` | ⚠️ validation_error | 422 | 25.17 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/rewards/history` | ⚠️ validation_error | 422 | 25.31 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/rewards/give` | ⚠️ validation_error | 422 | 33.79 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/rewards/shop` | ✅ success | 200 | 25.42 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/rewards/purchase` | ⚠️ validation_error | 422 | 24.24 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/achievements` | ⚠️ validation_error | 422 | 26.4 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/achievements/unlock` | ⚠️ validation_error | 422 | 27.31 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/achievements/progress` | ⚠️ validation_error | 422 | 27.3 | ✅ | 80/100 | ⚠️ |
| GET | `/api/gamification/achievements/{achievementId}` | ✅ success | 200 | 27.88 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/achievements/claim` | ⚠️ validation_error | 422 | 34.16 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/tournaments` | ✅ success | 200 | 28.49 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/tournaments/join` | ⚠️ validation_error | 422 | 26.51 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/tournaments/{tournamentId}` | ✅ success | 200 | 24.85 | ✅ | 80/100 | ✅ |
| GET | `/api/gamification/tournaments/leaderboard` | ✅ success | 200 | 27.36 | ✅ | 80/100 | ✅ |
| POST | `/api/gamification/tournaments/leave` | ⚠️ validation_error | 422 | 26.36 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/tournaments/history` | ✅ success | 200 | 25.03 | ✅ | 80/100 | ✅ |
| GET | `/api/gamification/settings` | ⚠️ validation_error | 422 | 28.46 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/settings/update` | ⚠️ validation_error | 422 | 28.72 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/settings/notifications` | ⚠️ validation_error | 422 | 26.32 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/settings/notifications/update` | ⚠️ validation_error | 422 | 27.87 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/progress` | ⚠️ validation_error | 422 | 35.46 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/progress/update` | ⚠️ validation_error | 422 | 27.12 | ✅ | 75/100 | ⚠️ |
| GET | `/api/gamification/progress/stats` | ⚠️ validation_error | 422 | 26.68 | ✅ | 80/100 | ⚠️ |
| GET | `/api/gamification/progress/level` | ⚠️ validation_error | 422 | 27.1 | ✅ | 80/100 | ⚠️ |
| POST | `/api/gamification/progress/reset` | ⚠️ validation_error | 422 | 37.33 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/settings/{familyId}` | ✅ success | 200 | 26.4 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/settings/update` | ⚠️ validation_error | 422 | 25.88 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/settings/history` | ✅ success | 200 | 27.82 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/settings/sync` | ⚠️ validation_error | 422 | 26.53 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/settings/conflicts` | ✅ success | 200 | 27.21 | ✅ | 80/100 | ✅ |
| GET | `/api/parental-control/time-limits/{childId}` | ✅ success | 200 | 28.71 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/time-limits/update` | ⚠️ validation_error | 422 | 25.42 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/time-limits/history` | ✅ success | 200 | 27.29 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/time-limits/reset` | ⚠️ validation_error | 422 | 26.38 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/schedules/{childId}` | ✅ success | 200 | 28.88 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/schedules/update` | ⚠️ validation_error | 422 | 25.43 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/schedules/history` | ✅ success | 200 | 24.32 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/schedules/delete` | ⚠️ validation_error | 422 | 27.48 | ✅ | 75/100 | ⚠️ |
| GET | `/api/parental-control/geofences/{childId}` | ✅ success | 200 | 27.32 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/geofences/add` | ⚠️ validation_error | 422 | 29.26 | ✅ | 75/100 | ⚠️ |
| POST | `/api/parental-control/geofences/update` | ⚠️ validation_error | 422 | 27.99 | ✅ | 75/100 | ⚠️ |
| DELETE | `/api/parental-control/geofences/{geofenceId}` | ✅ success | 200 | 25.88 | ✅ | 75/100 | ✅ |
| GET | `/api/parental-control/app-blocks/{childId}` | ✅ success | 200 | 26.66 | ✅ | 80/100 | ✅ |
| POST | `/api/parental-control/app-blocks/update` | ⚠️ validation_error | 422 | 25.31 | ✅ | 75/100 | ⚠️ |
| POST | `/api/parental-control/app-blocks/sync` | ⚠️ validation_error | 422 | 27.65 | ✅ | 75/100 | ⚠️ |
| POST | `/api/user/profile/sync` | ⚠️ validation_error | 422 | 25.76 | ✅ | 75/100 | ⚠️ |
| POST | `/api/user/profile/update` | ⚠️ validation_error | 422 | 31.47 | ✅ | 75/100 | ⚠️ |
| GET | `/api/user/profile/history` | ⚠️ validation_error | 422 | 27.69 | ✅ | 80/100 | ⚠️ |
| GET | `/api/user/profile/privacy` | ⚠️ validation_error | 422 | 26.38 | ✅ | 80/100 | ⚠️ |
| POST | `/api/user/profile/privacy/update` | ⚠️ validation_error | 422 | 25.81 | ✅ | 75/100 | ⚠️ |
| POST | `/api/subscription/sync` | ⚠️ validation_error | 422 | 26.89 | ✅ | 75/100 | ⚠️ |
| POST | `/api/subscription/update` | ⚠️ validation_error | 422 | 26.01 | ✅ | 75/100 | ⚠️ |
| GET | `/api/subscription/purchase-history` | ⚠️ validation_error | 422 | 26.23 | ✅ | 80/100 | ⚠️ |
| GET | `/api/subscription/status` | ⚠️ validation_error | 422 | 26.0 | ✅ | 80/100 | ⚠️ |
| POST | `/api/subscription/status/update` | ⚠️ validation_error | 422 | 26.2 | ✅ | 75/100 | ⚠️ |
| GET | `/api/subscription/auto-renewal` | ⚠️ validation_error | 422 | 28.88 | ✅ | 80/100 | ⚠️ |
| POST | `/api/subscription/auto-renewal/update` | ⚠️ validation_error | 422 | 29.99 | ✅ | 75/100 | ⚠️ |
| POST | `/api/subscription/cancel` | ⚠️ validation_error | 422 | 31.74 | ✅ | 75/100 | ⚠️ |
| POST | `/api/settings/sync` | ⚠️ validation_error | 422 | 25.03 | ✅ | 75/100 | ⚠️ |
| POST | `/api/settings/update` | ⚠️ validation_error | 422 | 28.49 | ✅ | 75/100 | ⚠️ |
| GET | `/api/settings/theme` | ⚠️ validation_error | 422 | 28.05 | ✅ | 80/100 | ⚠️ |
| POST | `/api/settings/theme/update` | ⚠️ validation_error | 422 | 27.79 | ✅ | 75/100 | ⚠️ |
| GET | `/api/settings/language` | ⚠️ validation_error | 422 | 25.26 | ✅ | 80/100 | ⚠️ |
| POST | `/api/settings/language/update` | ⚠️ validation_error | 422 | 27.86 | ✅ | 75/100 | ⚠️ |
| GET | `/api/settings/notifications` | ⚠️ validation_error | 422 | 27.28 | ✅ | 80/100 | ⚠️ |
| POST | `/api/settings/notifications/update` | ⚠️ validation_error | 422 | 28.8 | ✅ | 75/100 | ⚠️ |
| GET | `/api/settings/biometry` | ⚠️ validation_error | 422 | 25.45 | ✅ | 80/100 | ⚠️ |
| POST | `/api/settings/biometry/update` | ⚠️ validation_error | 422 | 27.28 | ✅ | 75/100 | ⚠️ |
| POST | `/api/location/geofences/sync` | ⚠️ validation_error | 422 | 26.44 | ✅ | 75/100 | ⚠️ |
| POST | `/api/location/geofences/update` | ⚠️ validation_error | 422 | 25.46 | ✅ | 75/100 | ⚠️ |
| DELETE | `/api/location/geofences/{geofenceId}` | ✅ success | 200 | 25.6 | ✅ | 75/100 | ✅ |
| GET | `/api/location/movement-history` | ⚠️ validation_error | 422 | 27.03 | ✅ | 80/100 | ⚠️ |
| POST | `/api/location/movement-history/update` | ⚠️ validation_error | 422 | 28.16 | ✅ | 75/100 | ⚠️ |
| GET | `/api/location/status` | ⚠️ validation_error | 422 | 25.21 | ✅ | 80/100 | ⚠️ |
| POST | `/api/location/status/update` | ⚠️ validation_error | 422 | 25.68 | ✅ | 75/100 | ⚠️ |
| POST | `/api/chat/offline-messages/sync` | ⚠️ validation_error | 422 | 29.64 | ✅ | 75/100 | ⚠️ |
| POST | `/api/chat/offline-messages/send` | ⚠️ validation_error | 422 | 34.28 | ✅ | 75/100 | ⚠️ |
| POST | `/api/chat/offline-messages/resolve-conflicts` | ⚠️ validation_error | 422 | 26.1 | ✅ | 75/100 | ⚠️ |
| POST | `/api/offline-storage/sync` | ⚠️ validation_error | 422 | 32.15 | ✅ | 75/100 | ⚠️ |
| GET | `/api/offline-storage/data` | ⚠️ validation_error | 422 | 27.77 | ✅ | 80/100 | ⚠️ |
| POST | `/api/offline-storage/data/update` | ⚠️ validation_error | 422 | 40.1 | ✅ | 75/100 | ⚠️ |
| DELETE | `/api/offline-storage/data/{dataId}` | ⚠️ validation_error | 422 | 31.3 | ✅ | 75/100 | ⚠️ |
| POST | `/api/offline-storage/resolve-conflicts` | ⚠️ validation_error | 422 | 25.13 | ✅ | 75/100 | ⚠️ |
| POST | `/api/crash-detection/sync` | ⚠️ validation_error | 422 | 29.4 | ✅ | 75/100 | ⚠️ |
| POST | `/api/crash-detection/report` | ⚠️ validation_error | 422 | 26.82 | ✅ | 75/100 | ⚠️ |
| GET | `/api/crash-detection/notifications` | ⚠️ validation_error | 422 | 30.22 | ✅ | 80/100 | ⚠️ |
| POST | `/api/crash-detection/notifications/send` | ⚠️ validation_error | 422 | 29.92 | ✅ | 75/100 | ⚠️ |
| POST | `/api/elderly/medications/sync` | ⚠️ validation_error | 422 | 35.75 | ✅ | 75/100 | ⚠️ |
| POST | `/api/elderly/medications/update` | ⚠️ validation_error | 422 | 32.37 | ✅ | 75/100 | ⚠️ |
| POST | `/api/elderly/appointments/sync` | ⚠️ validation_error | 422 | 25.77 | ✅ | 75/100 | ⚠️ |
| POST | `/api/elderly/appointments/update` | ⚠️ validation_error | 422 | 24.34 | ✅ | 75/100 | ⚠️ |
| GET | `/` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/health` | ✅ success | 200 | 26.73 | ✅ | 80/100 | ✅ |
