# 📊 ДЕТАЛЬНЫЙ ОТЧЕТ О ТЕСТИРОВАНИИ ENDPOINT'ОВ

**Дата:** 2026-02-11 23:42:46
**Base URL:** http://149.154.65.180:8002
**Family ID:** FAM_BC83237553F3

## 📈 СТАТИСТИКА

- **Всего endpoint'ов:** 238
- **✅ Успешно:** 0
- **❌ Ошибки:** 0
- **⏭️ Пропущено:** 238
- **🔐 Требуют авторизацию:** 0
- **🌐 Публичные:** 0

**Процент успеха:** 0.0%

### 📊 Статусы HTTP:

- **200 OK:** 0
- **201 Created:** 0
- **204 No Content:** 0
- **401 Unauthorized:** 0
- **403 Forbidden:** 0
- **404 Not Found:** 0
- **422 Validation Error:** 0
- **500+ Server Error:** 0

### ⚡ Производительность:

- **✅ Быстрые (< 2000ms):** 0
- **🐌 Медленные (> 2000ms):** 0

### 🔒 Безопасность:

- **✅ Без проблем:** 0
- **⚠️ Проблемы:** 0

### ✅ Валидация:

- **✅ Без проблем:** 0
- **⚠️ Проблемы:** 0

## 📋 ВСЕ РЕЗУЛЬТАТЫ

| Метод | Путь | Статус | HTTP | Время (мс) | Производительность | Безопасность | Валидация |
|-------|------|--------|------|------------|-------------------|--------------|-----------|
| POST | `/api/auth/login` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/auth/register` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/auth/refresh` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/auth/login-by-recovery-code` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/auth/logout` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/referral/code` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/referral/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/referral/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/referral/rewards` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/referral/test/payment/create` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/referral/test/payment/confirm` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/referral/test/discount/apply` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/payments/create` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/payments/status/{payment_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/payments/confirm` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/payments/recover` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/activation/retrieve` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/status/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/enable/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/disable/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/configuration/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/configuration/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/batch/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/protection/settings` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/protection/settings` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/protection/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/protection/threat-scenarios` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/protection/enable` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/protection/disable` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/protection/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/protection/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/family/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/family/create` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/ai-categories/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/ai-categories/reports` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/ai-categories/allow` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/ai-categories/block` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/ai-categories/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/tracker/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/tracker/top` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/privacy/tracker/whitelist` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/tracker/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/setup` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/alert` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/start` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/stop` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/data` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/crash-detection/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/reports/privacy/location/bubble` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/reports/privacy/location/send` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/dark-web/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/dark-web/leaks` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/dark-web/scans` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/dark-web/resolve` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/dark-web/scan/start` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/dark-web/scan/secure` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/dark-web/scan/fast` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/dark-web/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/records` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/privacy/cleanup/start` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/cleanup/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/identity-theft/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/identity-theft/attempts` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/identity-theft/allow` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/identity-theft/block` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/identity-theft/whitelist` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/identity-theft/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/location/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/location/requests` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/privacy/location/allow` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/privacy/location/block` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/reports/privacy/location/update-accuracy` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/privacy/location/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/roadside-assistance/call` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/roadside-assistance/status/{request_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/roadside-assistance/cancel/{request_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/roadside-assistance/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/roadside-assistance/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/v1/parental-control/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/v1/parental-control/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/parental/bypass/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/parental/bypass/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/iot/status/{homeId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/iot/devices/{homeId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/iot/threats/{homeId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/iot/device/{deviceId}/block` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/iot/scan/{homeId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/iot/fix/{threatId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/driving/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/driving/export` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/reports/driving/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/read` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/unread_count` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/mark_read/{notification_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/delete/{notification_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/bulk_mark_read` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/test` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| PUT | `/api/notifications/settings` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/categories` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/preferences` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| PUT | `/api/notifications/preferences` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/clear_all` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/archive/{notification_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/notifications/unarchive/{notification_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/filter` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/search` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/notifications/export` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/ai/assistant/chat` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/ai/assistant/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/ai/assistant/feedback` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/ai/assistant/capabilities` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/ai/assistant/analyze_threat` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/ai/assistant/recommendations` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/ai/assistant/report_incident` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/ai/assistant/security_tips` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/list` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/status/all` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/config/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/config/update/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/restart/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/metrics/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/logs/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/components/dependencies/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/test/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/components/update/{component_id}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/info` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/logs` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/system/maintenance` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/metrics` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/system/backup` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/backup/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/uptime` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/version` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/system/restart` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/system/resources` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/balance/{userId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/balance/add` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/balance/subtract` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/balance/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/rewards` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/rewards/claim` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/rewards/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/rewards/give` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/rewards/shop` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/rewards/purchase` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/achievements` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/achievements/unlock` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/achievements/progress` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/achievements/{achievementId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/achievements/claim` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/tournaments` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/tournaments/join` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/tournaments/{tournamentId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/tournaments/leaderboard` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/tournaments/leave` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/tournaments/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/settings` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/settings/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/settings/notifications` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/settings/notifications/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/progress` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/progress/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/progress/stats` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/gamification/progress/level` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/gamification/progress/reset` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/settings/{familyId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/settings/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/settings/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/settings/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/settings/conflicts` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/time-limits/{childId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/time-limits/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/time-limits/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/time-limits/reset` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/schedules/{childId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/schedules/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/schedules/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/schedules/delete` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/geofences/{childId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/geofences/add` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/geofences/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| DELETE | `/api/parental-control/geofences/{geofenceId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/parental-control/app-blocks/{childId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/app-blocks/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/parental-control/app-blocks/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/user/profile/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/user/profile/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/user/profile/history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/user/profile/privacy` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/user/profile/privacy/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/subscription/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/subscription/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/subscription/purchase-history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/subscription/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/subscription/status/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/subscription/auto-renewal` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/subscription/auto-renewal/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/subscription/cancel` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/settings/theme` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/theme/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/settings/language` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/language/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/settings/notifications` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/notifications/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/settings/biometry` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/settings/biometry/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/location/geofences/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/location/geofences/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| DELETE | `/api/location/geofences/{geofenceId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/location/movement-history` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/location/movement-history/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/location/status` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/location/status/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/chat/offline-messages/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/chat/offline-messages/send` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/chat/offline-messages/resolve-conflicts` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/offline-storage/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/offline-storage/data` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/offline-storage/data/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| DELETE | `/api/offline-storage/data/{dataId}` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/offline-storage/resolve-conflicts` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/report` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/crash-detection/notifications` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/crash-detection/notifications/send` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/elderly/medications/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/elderly/medications/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/elderly/appointments/sync` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| POST | `/api/elderly/appointments/update` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
| GET | `/api/health` | ⏭️ skipped | N/A | N/A | ✅ | N/A/100 | ✅ |
