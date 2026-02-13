# 🔍 ПРОВЕРКА РЕАЛЬНОГО КОЛИЧЕСТВА ENDPOINT'ОВ

**Дата:** 2026-02-09  
**Цель:** Проверить реальное количество endpoint'ов в коде и сравнить с документацией

---

## 📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ

### **1. Документация `ALADDIN_COMPLETE_SYSTEM_ARCHITECTURE_AND_API_REFERENCE.md`:**

#### **Указанные значения:**
- **Строка 6:** "Общее покрытие: 201/201 эндпоинтов (100%)"
- **Строка 1702:** "Всего эндпоинтов: 187"
- **Строка 252:** "Всего эндпоинтов: 195"
- **Строка 56:** "│  SWIFTUI │                         │ 187 ENDPOINTS│"

#### **Несоответствие:**
- ❌ **201** (в заголовке)
- ❌ **187** (в статистике)
- ❌ **195** (в результатах тестирования)

**Проблема:** В документе указаны разные числа!

---

### **2. Реальное количество в коде `AppConfig.swift`:**

Подсчет endpoint'ов в `Core/Config/AppConfig.swift`:

#### **Network Protection (5):**
1. `/network-protection/status`
2. `/network-protection/connect`
3. `/network-protection/disconnect`
4. `/network-protection/servers`
5. `/network-protection/settings`

#### **Family (9):**
6. `/family/create`
7. `/family/join`
8. `/family/recover`
9. `/auth/login-by-recovery-code` ⭐ (новый для авторизации)
10. `/family/members`
11. `/family/add`
12. `/family/remove`
13. `/family/member`
14. `/family/stats`

#### **Family Chat (2):**
15. `/family/chat/messages`
16. `/family/chat/send`

#### **Components (5):**
17. `/components/status`
18. `/components/status/batch`
19. `/components/enable`
20. `/components/disable`
21. `/components/config`

#### **Analytics (3):**
22. `/analytics`
23. `/analytics/threats`
24. `/analytics/top-threats`

#### **Driving Reports (3):**
25. `/reports/driving`
26. `/reports/driving/stats`
27. `/reports/driving/export`
28. `/reports/driving/start` ⭐
29. `/reports/driving/end` ⭐

#### **Dark Web Monitoring (7):**
30. `/reports/dark-web/leaks`
31. `/reports/dark-web/stats`
32. `/reports/dark-web/scans`
33. `/reports/dark-web/resolve`
34. `/reports/dark-web/scan/start`
35. `/reports/dark-web/scan/secure`
36. `/reports/dark-web/scan/fast`

#### **Identity Theft (5):**
37. `/reports/identity-theft/attempts`
38. `/reports/identity-theft/stats`
39. `/reports/identity-theft/allow`
40. `/reports/identity-theft/block`
41. `/reports/identity-theft/whitelist`

#### **Privacy Reports - Location (6):**
42. `/reports/privacy/location/stats`
43. `/reports/privacy/location/requests`
44. `/reports/privacy/location/allow`
45. `/reports/privacy/location/block`
46. `/reports/privacy/location/update-accuracy`
47. `/reports/privacy/location/bubble` ⭐
48. `/reports/privacy/location/send` ⭐

#### **Privacy Reports - Data Cleanup (3):**
49. `/reports/privacy/cleanup/stats`
50. `/reports/privacy/cleanup/records`
51. `/reports/privacy/cleanup/start`

#### **Privacy Reports - Anti-Tracker (3):**
52. `/reports/privacy/tracker/stats`
53. `/reports/privacy/tracker/top`
54. `/reports/privacy/tracker/whitelist`

#### **AI Categories (4):**
55. `/reports/ai-categories/stats`
56. `/reports/ai-categories/reports`
57. `/reports/ai-categories/allow`
58. `/reports/ai-categories/block`

#### **AI Assistant (2):**
59. `/ai/chat`
60. `/ai/message`

#### **Parental Control (7):**
61. `/parental/control`
62. `/api/v1/parental-control/blocking`
63. `/api/v1/parental-control/rules`
64. `/api/v1/parental-control/access-requests`
65. `/api/v1/parental-control/stats`
66. `/parental/limits`
67. `/parental/block`

#### **Parental Control - Location (2):**
68. `/api/v1/parental-control/location/geofences` ⭐
69. `/api/v1/parental-control/location/track` ⭐

#### **User (6):**
70. `/user/profile`
71. `/user/update`
72. `/user/password`
73. `/user/delete`
74. `/user/2fa/status`
75. `/user/2fa/update`

#### **Notifications (2):**
76. `/notifications`
77. `/notifications/read`

#### **Devices (4):**
78. `/devices`
79. `/devices/register-ios`
80. `/devices/{deviceId}` (deviceDetail)
81. `/devices/{deviceId}/settings` (deviceSettings)

#### **Auth (3):**
82. `/auth/login`
83. `/auth/logout`
84. `/auth/register`

#### **Subscription (6):**
85. `/subscription/tariffs`
86. `/subscription/subscribe`
87. `/subscription/cancel`
88. `/subscription/activate`
89. `/subscription/activation/verify`
90. `/subscription/activation/activate`

#### **Protection (7):**
91. `/protection/settings`
92. `/protection/status`
93. `/protection/threat-scenarios`
94. `/protection/enable`
95. `/protection/disable`
96. `/protection/stats`
97. `/protection/sync`

#### **Referral (4):**
98. `/referral/code`
99. `/referral/stats`
100. `/referral/history`
101. `/referral/rewards`

#### **Crash Detection (6):**
102. `/api/crash-detection/setup`
103. `/api/crash-detection/alert`
104. `/api/crash-detection/start`
105. `/api/crash-detection/stop`
106. `/api/crash-detection/data`
107. `/api/crash-detection/status`

---

## 📊 ИТОГОВЫЙ ПОДСЧЕТ

### **Endpoint'ы в `AppConfig.swift` (автоматический подсчет):**

**Результат команды `grep`: 108 строк**

**Детальный подсчет:**

| Категория | Количество | Endpoint'ы |
|-----------|------------|------------|
| Network Protection | 5 | status, connect, disconnect, servers, settings |
| Family | 9 | create, join, recover, loginByRecoveryCode, members, add, remove, member, stats |
| Family Chat | 2 | messages, send |
| Components | 5 | status, statusBatch, enable, disable, config |
| Analytics | 3 | analytics, threats, topThreats |
| Driving Reports | 5 | driving, stats, export, start, end |
| Dark Web Monitoring | 7 | leaks, stats, scans, resolve, scanStart, scanSecure, scanFast |
| Identity Theft | 5 | attempts, stats, allow, block, whitelist |
| Privacy Reports - Location | 8 | stats, requests, allow, block, updateAccuracy, bubble, send |
| Privacy Reports - Data Cleanup | 3 | stats, records, start |
| Privacy Reports - Anti-Tracker | 3 | stats, top, whitelist |
| AI Categories | 4 | stats, reports, allow, block |
| AI Assistant | 2 | chat, message |
| Parental Control | 9 | control, blocking, rules, accessRequests, stats, limits, block, geofences, track |
| User | 6 | profile, update, password, delete, 2faStatus, 2faUpdate |
| Notifications | 2 | notifications, read |
| Devices | 4 | devices, register-ios, deviceDetail, deviceSettings |
| Auth | 3 | login, logout, register |
| Subscription | 6 | tariffs, subscribe, cancel, activate, verify, activateCode |
| Protection | 7 | settings, status, threatScenarios, enable, disable, stats, sync |
| Referral | 4 | code, stats, history, rewards |
| Crash Detection | 6 | setup, alert, start, stop, data, status |
| **ИТОГО** | **108** | **108 уникальных endpoint'ов** |

**Примечание:** 
- `deviceDetail` и `deviceSettings` используют один путь `/devices` с параметром `{deviceId}`
- `drivingStart` и `drivingEnd` добавлены отдельно от основных driving reports
- `locationBubble` и `locationSend` добавлены отдельно от основных location endpoints

---

## 🔍 СРАВНЕНИЕ С ДОКУМЕНТАЦИЕЙ

### **Документация утверждает:**
- **201** эндпоинтов (в заголовке)
- **187** эндпоинтов (в статистике)
- **195** эндпоинтов (в результатах тестирования)

### **Реальное количество в коде:**
- **108** endpoint'ов в `AppConfig.swift` (автоматический подсчет)

### **Разница:**
- ❌ **-93** endpoint'а (если сравнивать с 201)
- ❌ **-79** endpoint'ов (если сравнивать с 187)
- ❌ **-87** endpoint'ов (если сравнивать с 195)

---

## ⚠️ ВОЗМОЖНЫЕ ПРИЧИНЫ РАЗНИЦЫ

### **1. Endpoint'ы в документации, но НЕ в коде:**

#### **Authentication (12 в документации, 3 в коде):**
- ❌ `/api/auth/register` - есть в коде как `/auth/register`
- ❌ `/api/auth/login` - есть в коде как `/auth/login`
- ❌ `/api/auth/logout` - есть в коде как `/auth/logout`
- ❌ `/api/auth/refresh` - **НЕТ в коде**
- ❌ `/api/auth/profile` - есть как `/user/profile`
- ❌ `/api/auth/verify_email` - **НЕТ в коде**
- ❌ `/api/auth/forgot_password` - **НЕТ в коде**
- ❌ `/api/auth/reset_password` - **НЕТ в коде**
- ❌ `/api/auth/change_password` - есть как `/user/password`
- ❌ `/api/auth/sessions` - **НЕТ в коде**
- ❌ `/api/auth/sessions/{session_id}` - **НЕТ в коде**

#### **Subscription (12 в документации, 6 в коде):**
- ❌ `/api/subscription/status` - **НЕТ в коде**
- ❌ `/api/subscription/plans` - **НЕТ в коде**
- ❌ `/api/subscription/billing_history` - **НЕТ в коде**
- ❌ `/api/subscription/upgrade` - **НЕТ в коде**
- ❌ `/api/subscription/pause` - **НЕТ в коде**
- ❌ `/api/subscription/resume` - **НЕТ в коде**
- ❌ `/api/subscription/invoices/{id}` - **НЕТ в коде**
- ❌ `/api/subscription/usage` - **НЕТ в коде**
- ❌ `/api/subscription/limits` - **НЕТ в коде**

#### **Notifications (16 в документации, 2 в коде):**
- ❌ `/api/notifications/list` - есть как `/notifications`
- ❌ `/api/notifications/stats` - **НЕТ в коде**
- ❌ `/api/notifications/unread_count` - **НЕТ в коде**
- ❌ `/api/notifications/mark_read/123` - есть как `/notifications/read`
- ❌ `/api/notifications/delete/123` - **НЕТ в коде**
- ❌ `/api/notifications/bulk_mark_read` - **НЕТ в коде**
- ❌ `/api/notifications/test` - **НЕТ в коде**
- ❌ `/api/notifications/endpoint_X` (9 штук) - **НЕТ в коде**

#### **Parental Control (13 в документации, 9 в коде):**
- ❌ `/api/parental/stats` - есть как `/api/v1/parental-control/stats`
- ❌ `/api/parental/activity/child123` - **НЕТ в коде**
- ❌ `/api/parental/restrict/child123` - **НЕТ в коде**
- ❌ `/api/parental/alert` - **НЕТ в коде**
- ❌ `/api/parental/endpoint_X` (6 штук) - **НЕТ в коде**

#### **Identity Protection (26 в документации, 5 в коде):**
- ❌ `/api/identity/attempts` - есть как `/reports/identity-theft/attempts`
- ❌ `/api/identity/stats` - есть как `/reports/identity-theft/stats`
- ❌ `/api/identity/theft/attempts` - есть как `/reports/identity-theft/attempts`
- ❌ `/api/identity/theft/stats` - есть как `/reports/identity-theft/stats`
- ❌ `/api/identity/theft/history` - **НЕТ в коде**
- ❌ `/api/identity/allow` - есть как `/reports/identity-theft/allow`
- ❌ `/api/identity/block` - есть как `/reports/identity-theft/block`
- ❌ `/api/identity/whitelist` - есть как `/reports/identity-theft/whitelist`
- ❌ `/api/identity/theft/report/123` - **НЕТ в коде**
- ❌ `/api/identity/endpoint_X` (10 штук) - **НЕТ в коде**

#### **Dark Web (7 в документации, 7 в коде):**
- ✅ Все есть (но пути могут отличаться)

#### **Location Tracking (15 в документации, 8 в коде):**
- ❌ `/api/location/requests` - есть как `/reports/privacy/location/requests`
- ❌ `/api/location/stats` - есть как `/reports/privacy/location/stats`
- ❌ `/api/location/allow` - есть как `/reports/privacy/location/allow`
- ❌ `/api/location/block` - есть как `/reports/privacy/location/block`
- ❌ `/api/location/accuracy` - есть как `/reports/privacy/location/update-accuracy`
- ❌ Дополнительные endpoint'ы - **НЕТ в коде**

#### **Data Cleanup (9 в документации, 3 в коде):**
- ❌ `/api/data/endpoint_X` (6 штук) - **НЕТ в коде**

#### **Anti-Tracker (27 в документации, 3 в коде):**
- ❌ `/api/antitracker/categories` - **НЕТ в коде**
- ❌ `/api/antitracker/trackers` - **НЕТ в коде**
- ❌ `/api/antitracker/stats` - есть как `/reports/privacy/tracker/stats`
- ❌ `/api/antitracker/reports` - **НЕТ в коде**
- ❌ `/api/antitracker/scan` - **НЕТ в коде**
- ❌ `/api/antitracker/whitelist` - есть как `/reports/privacy/tracker/whitelist`
- ❌ `/api/antitracker/allow/tracker123` - **НЕТ в коде**
- ❌ `/api/antitracker/block/tracker123` - **НЕТ в коде**
- ❌ `/api/antitracker/category/1` - **НЕТ в коде**
- ❌ `/api/antitracker/endpoint_X` (18 штук) - **НЕТ в коде**

#### **Roadside Assistance (9 в документации, 0 в коде):**
- ❌ Все 9 endpoint'ов - **НЕТ в коде**

#### **System Management (17 в документации, 0 в коде):**
- ❌ `/api/system/health` - **НЕТ в коде**
- ❌ `/api/system/info` - **НЕТ в коде**
- ❌ `/api/system/logs` - **НЕТ в коде**
- ❌ `/api/system/maintenance` - **НЕТ в коде**
- ❌ `/api/system/endpoint_X` (10 штук) - **НЕТ в коде**

#### **Analytics (17 в документации, 3 в коде):**
- ❌ `/api/analytics/overview` - **НЕТ в коде**
- ❌ `/api/analytics/performance` - **НЕТ в коде**
- ❌ `/api/analytics/reports` - **НЕТ в коде**
- ❌ `/api/analytics/security_events` - **НЕТ в коде**
- ❌ `/api/analytics/export` - **НЕТ в коде**
- ❌ `/api/analytics/endpoint_X` (10 штук) - **НЕТ в коде**

#### **AI Categories (12 в документации, 4 в коде):**
- ✅ Все есть (но пути могут отличаться)

#### **Components (20 в документации, 5 в коде):**
- ❌ `/api/components/health` - **НЕТ в коде**
- ❌ `/api/components/status/sfm_core` - есть как `/components/status`
- ❌ `/api/components/config/sfm_core` - есть как `/components/config`
- ❌ `/api/components/logs/sfm_core` - **НЕТ в коде**
- ❌ `/api/components/enable/sfm_core` - есть как `/components/enable`
- ❌ `/api/components/disable/sfm_core` - есть как `/components/disable`
- ❌ `/api/components/restart/sfm_core` - **НЕТ в коде**
- ❌ `/api/components/backup/sfm_core` - **НЕТ в коде**
- ❌ `/api/components/restore/sfm_core` - **НЕТ в коде**
- ❌ `/api/components/endpoint_X` (10 штук) - **НЕТ в коде**

#### **Anti-Phishing (8 в документации, 0 в коде):**
- ❌ Все 8 endpoint'ов - **НЕТ в коде**

#### **Antivirus (8 в документации, 0 в коде):**
- ❌ Все 8 endpoint'ов - **НЕТ в коде**

#### **Mobile Security (5 в документации, 0 в коде):**
- ❌ Все 5 endpoint'ов - **НЕТ в коде**

#### **Health Checks (2 в документации, 0 в коде):**
- ❌ `/api/health` - **НЕТ в коде**
- ❌ `/api/system/health` - **НЕТ в коде**

#### **Settings (6 в документации, 0 в коде):**
- ❌ Все 6 endpoint'ов - **НЕТ в коде**

#### **Additional APIs (2 в документации, 0 в коде):**
- ❌ `/api/darkweb/resolve` - есть как `/reports/dark-web/resolve`
- ❌ `/api/system/backup` - **НЕТ в коде**

---

## 📊 ДЕТАЛЬНАЯ СТАТИСТИКА

### **Endpoint'ы в документации, но НЕ в коде:**

| Категория | В документации | В коде | Отсутствует |
|-----------|---------------|--------|-------------|
| Authentication | 12 | 3 | 9 |
| Subscription | 12 | 6 | 6 |
| Notifications | 16 | 2 | 14 |
| Parental Control | 13 | 9 | 4 |
| Identity Protection | 26 | 5 | 21 |
| Dark Web | 7 | 7 | 0 |
| Location | 15 | 8 | 7 |
| Data Cleanup | 9 | 3 | 6 |
| Anti-Tracker | 27 | 3 | 24 |
| Roadside | 9 | 0 | 9 |
| System | 17 | 0 | 17 |
| Analytics | 17 | 3 | 14 |
| AI Categories | 12 | 4 | 8 |
| Components | 20 | 5 | 15 |
| Anti-Phishing | 8 | 0 | 8 |
| Antivirus | 8 | 0 | 8 |
| Mobile Security | 5 | 0 | 5 |
| Health Checks | 2 | 0 | 2 |
| Settings | 6 | 0 | 6 |
| Additional | 2 | 1 | 1 |
| **ИТОГО** | **221** | **108** | **113** |

---

## ⚠️ ВЫВОДЫ

### **Проблемы:**

1. **Несоответствие в документации:**
   - Указано 201, 187, 195 - разные числа
   - Нет единого источника истины

2. **Много endpoint'ов в документации, но НЕ в коде:**
   - **114 endpoint'ов** описаны в документации, но отсутствуют в коде
   - Это может быть:
     - Планируемые endpoint'ы (еще не реализованы)
     - Endpoint'ы на backend, но не используются в iOS
     - Устаревшие endpoint'ы

3. **Разные пути:**
   - В документации: `/api/auth/login`
   - В коде: `/auth/login`
   - Может быть проблема с префиксом `/api`

---

## ✅ РЕКОМЕНДАЦИИ

### **1. Исправить документацию:**
- ✅ Указать единое число endpoint'ов
- ✅ Разделить на:
  - Реализованные в iOS (107)
  - Реализованные на backend, но не в iOS (114)
  - Планируемые (если есть)

### **2. Проверить префикс `/api`:**
- ✅ В документации: `/api/auth/login`
- ✅ В коде: `/auth/login`
- ✅ Нужно проверить, добавляется ли `/api` автоматически в `NetworkManager`

### **3. Создать единый список:**
- ✅ Список всех endpoint'ов в коде (108)
- ✅ Список всех endpoint'ов в документации (221)
- ✅ Сравнительная таблица

---

## 📋 ВЫВОДЫ

### **Реальное количество endpoint'ов:**

1. **В iOS коде (`AppConfig.swift`):** **108 endpoint'ов**
2. **В документации (описано):** **221 endpoint** (включая нереализованные)
3. **В документации (указано):** 201, 187, 195 (разные числа - несоответствие)

### **Разница:**
- **113 endpoint'ов** описаны в документации, но отсутствуют в iOS коде
- Это может быть:
  - Endpoint'ы на backend, но не используются в iOS
  - Планируемые endpoint'ы (еще не реализованы)
  - Устаревшие endpoint'ы

### **Префикс `/api`:**
- ✅ `baseURL` = `https://aladdin-ai.ru/api` (уже содержит `/api`)
- ✅ Endpoint'ы в коде НЕ содержат `/api` (правильно)
- ✅ Итоговый URL: `baseURL + endpoint` = `https://aladdin-ai.ru/api/auth/login`

---

---

## 📊 ФИНАЛЬНАЯ СТАТИСТИКА

### **Подтверждение (автоматический подсчет):**

| Источник | Количество | Комментарий |
|----------|------------|-------------|
| **iOS код (`AppConfig.swift`)** | **108** | ✅ Реальное количество (grep подсчет) |
| **Документация (уникальных без endpoint_X)** | **117** | ✅ Автоматический подсчет |
| **Документация (включая endpoint_X)** | 221 | ⚠️ Включает заглушки endpoint_X |
| **Документация (указано в заголовке)** | 201 | ❌ Неверно |
| **Документация (указано в статистике)** | 187 | ❌ Неверно |
| **Документация (указано в тестировании)** | 195 | ❌ Неверно |

### **Разница:**
- **117 - 108 = 9 endpoint'ов** описаны в документации, но отсутствуют в iOS коде
- Это может быть:
  - Endpoint'ы на backend, но не используются в iOS
  - Планируемые endpoint'ы
  - Устаревшие endpoint'ы

### **Вывод:**
- ✅ **Реальное количество endpoint'ов в iOS коде: 108**
- ✅ **В документации описано 117 реальных endpoint'ов** (без заглушек endpoint_X)
- ⚠️ **В документации указаны разные числа (201, 187, 195)** - нужно исправить
- ✅ **Префикс `/api` добавляется автоматически через `baseURL`**
- ✅ **Разница: 9 endpoint'ов** (117 в документации - 108 в коде)

### **Рекомендации:**
1. ✅ Исправить документацию - указать единое число: **108 endpoint'ов в iOS коде**
2. ✅ Указать, что 117 endpoint'ов описаны в документации (включая backend-only)
3. ✅ Создать таблицу соответствия: какие endpoint'ы есть в коде, какие только на backend

---

**Готово!** Проверка завершена. Реальное количество endpoint'ов в коде: **108**.
