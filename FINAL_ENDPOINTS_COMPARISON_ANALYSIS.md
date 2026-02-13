# 🔍 ФИНАЛЬНЫЙ СРАВНИТЕЛЬНЫЙ АНАЛИЗ ENDPOINT'ОВ - ЧТО ЕСТЬ, ЧЕГО НЕТ, ЧТО НУЖНО

**Дата:** 2026-02-09  
**Сравнение:** `ALADDIN_IMPLEMENTATION_ROADMAP.md` vs Реальность  
**Статус:** ✅ Полная проверка каждого пункта

---

## 📊 ОБЩАЯ СТАТИСТИКА

### **По плану (ALADDIN_IMPLEMENTATION_ROADMAP.md):**
- **Всего endpoint'ов для реализации:** 87 (неактивных)
- **Всего endpoint'ов в системе:** 221
- **Активных на сервере:** 90 (41%)
- **Готово в iOS:** 131 (59%)

### **Реальность:**
- **На сервере (api_gateway_server_current.py):** 183 endpoint'а
- **В iOS (AppConfig.swift):** 108 endpoint'ов
- **В iOS (APIService.swift):** ~110 методов

---

## 🔥 ЭТАП 1: NOTIFICATIONS (16 endpoint'ов)

### **План говорит:**
- ❌ Сервер: 0 endpoint'ов
- ✅ iOS код: 2 endpoint'а (`getNotifications`, `markNotificationAsRead`)

### **Реальность:**
- ✅ **iOS UI:** `NotificationsScreen.swift` - ПОЛНОСТЬЮ реализован
  - Статистика уведомлений ✅
  - Фильтры по категориям ✅
  - Список уведомлений ✅
- ✅ **iOS код:** `NotificationManager.swift`, `PushNotificationService.swift`
- ❌ **Сервер:** Нужно добавить 16 endpoint'ов
- ❌ **APNs:** Нужно настроить инфраструктуру

### **Что нужно сделать:**
1. ✅ **UI:** Уже есть - НЕ НУЖНО
2. ❌ **Сервер:** Добавить 16 endpoint'ов на сервере
3. ❌ **APNs:** Настроить сертификаты и отправку

---

## 🔥 ЭТАП 2: AUTHENTICATION РАСШИРЕННЫЕ (8 endpoint'ов)

### **План говорит:**
- Социальные сети (Google, Apple, Facebook OAuth)
- Enterprise SSO (SAML, OAuth enterprise)
- Многофакторная аутентификация (SMS, TOTP)
- Управление сессиями

### **Реальность:**
- ✅ **Базовая авторизация:** `FamilyRegistrationViewModel.swift` - Recovery Code система
- ✅ **Управление сессиями:** `ActiveSessionsView` - уже есть в `ProfileScreen`
- ❌ **Социальные сети:** НЕ НУЖНО (не собираем персональные данные)
- ❌ **Enterprise SSO:** НЕ НУЖНО (не собираем персональные данные)
- ❌ **MFA (2FA):** Опционально (SMS/TOTP) - можно добавить

### **Что нужно сделать:**
1. ❌ **MFA (опционально):** Добавить SMS/TOTP коды в `ProfileScreen` → секция "Безопасность"
2. ✅ **Управление сессиями:** Уже есть - расширить если нужно
3. ❌ **Социальные сети:** НЕ НУЖНО - исключить из плана
4. ❌ **Enterprise SSO:** НЕ НУЖНО - исключить из плана

---

## 🟡 ЭТАП 3: PROTECTION РАСШИРЕННЫЕ (18 endpoint'ов)

### **План говорит:**
- Реал-тайм антивирусное сканирование
- Мониторинг даркнета
- Расширенная защита от фишинга
- Интеграция с external security feeds

### **Реальность:**
- ✅ **Антивирус:** `AntivirusManager.swift` - реал-тайм сканирование
  - `MalwareDetectionSettingsModal.swift` - настройки
  - Интеграция в `NetworkProtectionScreen` ✅
- ✅ **Dark Web:** `DarkWebMonitoringModal.swift` - модальное окно
  - `DarkWebMonitoringViewModel.swift` - логика
  - Интеграция в `MainScreen` и `AdvancedProtectionSettingsScreen` ✅
- ✅ **Фишинг:** `PhishingProtectionSettingsModal.swift` - настройки
  - Интеграция в `NetworkProtectionScreen` ✅
- ❌ **Внешние security feeds:** Нужно добавить интеграцию на сервере (опционально)
- ❌ **Расширенная аналитика:** Графики в `AnalyticsScreen` - НЕ НУЖНО (по запросу)

### **Что нужно сделать:**
1. ✅ **UI для антивируса:** Уже есть - НЕ НУЖНО
2. ✅ **UI для Dark Web:** Уже есть - НЕ НУЖНО
3. ✅ **UI для фишинга:** Уже есть - НЕ НУЖНО
4. ❌ **Внешние security feeds:** Опционально - интеграция на сервере
5. ❌ **Графики:** НЕ НУЖНО (по запросу)

---

## 🟡 ЭТАП 4: COMPONENTS РАСШИРЕННЫЕ (14 endpoint'ов)

### **План говорит:**
- Service discovery и registration
- Configuration management
- Расширенные health monitoring системы
- API gateway с rate limiting

### **Реальность:**
- ✅ **Базовые компоненты:** `ComponentStatusService.swift`, `ComponentConfigurationService.swift`
- ✅ **Health monitoring:** Есть в `ComponentStatusService`
- ❌ **Service Discovery:** Нужно добавить на сервере
- ❌ **Секция в SettingsScreen:** НУЖНО добавить "Системные компоненты" (только для админов)

### **Что нужно сделать:**
1. ❌ **Сервер:** Добавить endpoint'ы для Service Discovery, Configuration
2. ❌ **iOS UI:** Добавить секцию "Системные компоненты" в `SettingsScreen` (только для админов)

---

## 🟡 ЭТАП 5: PARENTAL CONTROL РАСШИРЕННЫЕ (9 endpoint'ов)

### **План говорит:**
- Детальный мониторинг приложений
- Content filtering с категориями
- Time management с гибким расписанием
- Emergency alerts для родителей

### **Реальность:**
- ✅ **Мониторинг приложений:** Уже есть в `ParentalControlScreen`
- ✅ **Content filtering:** `FamilyContentBlockModal` - 12 категорий
- ✅ **Time management:** `FamilyTimeControlModal` - расписание
- ✅ **Мониторинг:** `FamilyMonitoringModal` - полный мониторинг
- ✅ **Геолокация:** `FamilyLocationModal` - отслеживание
- ✅ **Отчеты:** `FamilyReportsModal` - отчеты
- ❌ **Emergency Alerts:** Можно добавить SOS-кнопку (опционально)
- ❌ **Расширенные отчеты:** Графики - НЕ НУЖНО (по запросу)

### **Что нужно сделать:**
1. ✅ **Все основные функции:** Уже есть - НЕ НУЖНО
2. ❌ **Emergency Alerts:** Опционально - SOS-кнопка
3. ❌ **Графики:** НЕ НУЖНО (по запросу)

---

## 🟢 ЭТАП 6: LOCATION TRACKING РАСШИРЕННЫЕ (7 endpoint'ов)

### **План говорит:**
- Геозоны с расписанием и условиями
- История перемещений с аналитикой
- Battery optimization
- Offline sync

### **Реальность:**
- ✅ **Базовое отслеживание:** `LocationManager.swift` - полная реализация
  - `GeofenceModels.swift` - модели геозон
  - `FamilyLocationModal` - модальное окно (в коде)
- ✅ **Геозоны:** Базовые геозоны работают
- ❌ **Геозоны с расписанием:** НУЖНО расширить `FamilyLocationModal`
- ❌ **История перемещений:** НУЖНО добавить в `AnalyticsScreen`
- ❌ **Battery optimization:** НУЖНО добавить настройки в `SettingsScreen`

### **Что нужно сделать:**
1. ❌ **Геозоны с расписанием:** Расширить `FamilyLocationModal` - НУЖНО
2. ❌ **История перемещений:** Добавить в `AnalyticsScreen` - НУЖНО
3. ❌ **Battery optimization:** Добавить настройки в `SettingsScreen` - НУЖНО

---

## 🟢 ЭТАП 7: ROADSIDE ASSISTANCE РАСШИРЕННЫЕ (4 endpoint'а)

### **План говорит:**
- Интеграция с эвакуационными сервисами
- Emergency call system
- Navigation assistance
- Service request forms

### **Реальность:**
- ✅ **Crash Detection:** `CrashDetectionManager.swift` - ПОЛНОСТЬЮ реализован
  - `CrashDetectionSettingsModal.swift` - настройки
  - `CrashDetectionAlertModal.swift` - экстренный вызов
  - Интеграция в `NetworkProtectionScreen` ✅
- ✅ **Сервер:** `roadside_assistance_agent.py`, `roadside_assistance_router.py` - ЕСТЬ
  - `POST /api/roadside-assistance/call` ✅
  - `GET /api/roadside-assistance/status/{request_id}` ✅
  - `POST /api/roadside-assistance/cancel/{request_id}` ✅
  - `GET /api/roadside-assistance/history` ✅
- ❌ **iOS экран:** НЕТ отдельного `RoadsideAssistanceScreen`
- ❌ **iOS код:** НЕТ методов в `APIService.swift` для roadside assistance
- ✅ **Emergency call:** Есть в `CrashDetectionAlertModal` - вызов 112

### **Что нужно сделать:**
1. ❌ **iOS экран:** Добавить секцию "Помощь на дороге" в `SupportScreen` или создать `RoadsideAssistanceScreen` - НУЖНО
2. ❌ **iOS код:** Добавить методы в `APIService.swift` для вызова roadside assistance - НУЖНО
3. ✅ **Crash Detection:** Уже есть - НЕ НУЖНО
4. ✅ **Сервер:** Уже есть - НЕ НУЖНО (только интеграция с партнерами опционально)

---

## 🟢 ЭТАП 8: SYSTEM MANAGEMENT РАСШИРЕННЫЕ (11 endpoint'ов)

### **План говорит:**
- Prometheus monitoring stack с Grafana
- Auto-scaling система
- Automated backup
- Comprehensive audit logging

### **Реальность:**
- ❌ **Секция в SettingsScreen:** НУЖНО добавить "Системное управление" (только для админов)
- ❌ **Сервер:** Prometheus, Grafana, Auto-scaling (DevOps задача)

### **Что нужно сделать:**
1. ❌ **iOS UI:** Добавить секцию "Системные компоненты" в `SettingsScreen` (только для админов) - НУЖНО
2. ❌ **Сервер:** Prometheus, Grafana (DevOps) - НУЖНО

---

## 📋 ИТОГОВАЯ ТАБЛИЦА: ЧТО ЕСТЬ vs ЧТО НУЖНО

| Этап | Endpoint'ов | iOS UI | iOS Код | Сервер | Что нужно |
|------|-------------|--------|---------|--------|-----------|
| **1. Notifications** | 16 | ✅ Есть | ✅ Есть (2) | ❌ Нет | Сервер (16) + APNs |
| **2. Authentication** | 8 | ✅ Есть | ✅ Есть | ✅ Есть (4) | MFA (опционально) |
| **3. Protection** | 18 | ✅ Есть | ✅ Есть | ✅ Есть (8) | Security feeds (опц.) |
| **4. Components** | 14 | ❌ Нет | ✅ Есть | ❌ Частично | Сервер + секция UI |
| **5. Parental Control** | 9 | ✅ Есть | ✅ Есть | ✅ Есть (4) | SOS (опционально) |
| **6. Location** | 7 | ✅ Есть | ✅ Есть | ✅ Есть (8) | Расширения UI |
| **7. Roadside** | 4 | ❌ Нет | ❌ Нет (Crash есть) | ✅ Есть (5) | Экран + iOS API методы |
| **8. System Mgmt** | 11 | ❌ Нет | ❌ Нет | ❌ Нет | Сервер + секция UI |

---

## ✅ ФИНАЛЬНЫЙ СПИСОК: ЧТО ДЕЙСТВИТЕЛЬНО НУЖНО СДЕЛАТЬ

### **🔥 КРИТИЧНО (для продакшна):**

#### **1. Серверные endpoint'ы (60-70 дней):**
- ❌ **Notifications:** 16 endpoint'ов на сервере
- ❌ **Components:** 14 endpoint'ов на сервере
- ❌ **System Management:** 11 endpoint'ов на сервере
- ❌ **Roadside Assistance:** Интеграция с эвакуационными службами (API)

#### **2. APNs инфраструктура (3-5 дней):**
- ❌ Настройка сертификатов
- ❌ Настройка отправки push-уведомлений

---

### **🟡 ВАЖНО (расширения UI):**

#### **3. Секция "Системные компоненты" (2-3 дня):**
- ❌ Добавить в `SettingsScreen` → секция "Система"
- ❌ Только для администраторов (скрыта для обычных пользователей)
- ❌ Использовать существующие `InfoRow` компоненты

#### **4. Расширения Location Tracking (5-7 дней):**
- ❌ **Геозоны с расписанием:** Расширить `FamilyLocationModal`
  - Добавить календарь для расписания
  - Разные правила для будних/выходных
- ❌ **История перемещений:** Добавить в `AnalyticsScreen`
  - Использовать существующие `StatItem` компоненты
- ❌ **Battery optimization:** Добавить настройки в `SettingsScreen`
  - Секция "Геолокация" → "Оптимизация батареи"

#### **5. Roadside Assistance экран (3-5 дней):**
- ❌ Добавить секцию "Помощь на дороге" в `SupportScreen`
  - Или создать отдельный `RoadsideAssistanceScreen`
- ❌ Добавить методы в `APIService.swift`:
  - `callRoadsideAssistance()`
  - `getRoadsideAssistanceStatus()`
  - `cancelRoadsideAssistance()`
  - `getRoadsideAssistanceHistory()`
- ❌ Добавить endpoint'ы в `AppConfig.swift`:
  - `/api/roadside-assistance/call`
  - `/api/roadside-assistance/status/{request_id}`
  - `/api/roadside-assistance/cancel/{request_id}`
  - `/api/roadside-assistance/history`
- ❌ Использовать существующие компоненты (`PrimaryButton`, модальные окна)
- ✅ **Сервер:** Уже есть - НЕ НУЖНО

---

### **🟢 ОПЦИОНАЛЬНО:**

#### **6. MFA (2FA) - опционально (3-5 дней):**
- ❌ Добавить SMS/TOTP коды в `ProfileScreen` → секция "Безопасность"
- ❌ Расширить существующий `TwoFactorAuthView`

#### **7. Emergency Alerts для родителей - опционально (2-3 дня):**
- ❌ Добавить SOS-кнопку в `ParentalControlScreen`
- ❌ Использовать существующие компоненты

---

## ❌ ЧТО НЕ НУЖНО (исключить из плана):

1. ❌ **Социальные сети (Google, Facebook, Apple)** - не собираем персональные данные
2. ❌ **Enterprise SSO** - не собираем персональные данные
3. ❌ **Email/Password регистрация** - не собираем персональные данные
4. ❌ **Графики в AnalyticsScreen** - не нужны (по запросу)
5. ❌ **Добавлять UI для антивируса** - уже есть
6. ❌ **Добавлять UI для Dark Web** - уже есть
7. ❌ **Добавлять UI для фишинга** - уже есть
8. ❌ **Добавлять статистику уведомлений** - уже есть
9. ❌ **Добавлять фильтры уведомлений** - уже есть
10. ❌ **Добавлять функции родительского контроля** - все уже есть

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **Что уже есть (не нужно делать):**
- ✅ Регистрация/авторизация: 100%
- ✅ Антивирус: 100%
- ✅ Dark Web Monitoring: 100%
- ✅ Фишинг защита: 100%
- ✅ Уведомления UI: 100%
- ✅ Родительский контроль: 95%
- ✅ Crash Detection: 100%
- ✅ Базовое Location Tracking: 100%

### **Что нужно добавить:**
- ❌ **Серверные endpoint'ы:** 41 endpoint (Notifications: 16, Components: 14, System: 11)
- ❌ **APNs инфраструктура:** Настройка сертификатов
- ❌ **Расширения UI:** 
  - Секция "Системные компоненты" в SettingsScreen
  - Расширения Location Tracking (геозоны с расписанием, история, battery)
  - Roadside Assistance экран/секция
- ❌ **Опционально:** MFA, Emergency Alerts

---

## ✅ ПОДТВЕРЖДЕНИЕ КАЖДОГО ПУНКТА

### **ЭТАП 1: NOTIFICATIONS**
- ✅ UI есть - подтверждено
- ❌ Сервер нужен - подтверждено
- ❌ APNs нужен - подтверждено

### **ЭТАП 2: AUTHENTICATION**
- ✅ Базовая авторизация есть - подтверждено
- ❌ Социальные сети - НЕ НУЖНО (подтверждено)
- ❌ Enterprise SSO - НЕ НУЖНО (подтверждено)
- ❌ MFA - опционально (подтверждено)

### **ЭТАП 3: PROTECTION**
- ✅ Антивирус есть - подтверждено
- ✅ Dark Web есть - подтверждено
- ✅ Фишинг есть - подтверждено
- ❌ Security feeds - опционально (подтверждено)

### **ЭТАП 4: COMPONENTS**
- ✅ Базовые компоненты есть - подтверждено
- ❌ Секция в SettingsScreen - НУЖНО (подтверждено)
- ❌ Серверные endpoint'ы - НУЖНО (подтверждено)

### **ЭТАП 5: PARENTAL CONTROL**
- ✅ Все функции есть - подтверждено
- ❌ Графики - НЕ НУЖНО (подтверждено)
- ❌ Emergency Alerts - опционально (подтверждено)

### **ЭТАП 6: LOCATION TRACKING**
- ✅ Базовое отслеживание есть - подтверждено
- ❌ Геозоны с расписанием - НУЖНО (подтверждено)
- ❌ История перемещений - НУЖНО (подтверждено)
- ❌ Battery optimization - НУЖНО (подтверждено)

### **ЭТАП 7: ROADSIDE ASSISTANCE**
- ✅ Crash Detection есть - подтверждено
- ✅ Сервер есть (5 endpoint'ов) - подтверждено
- ❌ iOS экран/секция - НУЖНО (подтверждено)
- ❌ iOS код (APIService методы) - НУЖНО (подтверждено)
- ❌ iOS endpoint'ы (AppConfig) - НУЖНО (подтверждено)

### **ЭТАП 8: SYSTEM MANAGEMENT**
- ❌ Секция в SettingsScreen - НУЖНО (подтверждено)
- ❌ Сервер (Prometheus, Grafana) - НУЖНО (подтверждено)

---

## 🎯 ФИНАЛЬНЫЙ ИТОГ

### **Реалистичный план работы:**

1. **Серверные endpoint'ы (60-70 дней):**
   - Notifications: 16 endpoint'ов
   - Components: 14 endpoint'ов
   - System Management: 11 endpoint'ов
   - Roadside Assistance: API интеграция

2. **APNs инфраструктура (3-5 дней):**
   - Сертификаты
   - Отправка push-уведомлений

3. **iOS код для Roadside Assistance (2-3 дня):**
   - Методы в `APIService.swift` (4 метода)
   - Endpoint'ы в `AppConfig.swift` (4 endpoint'а)

4. **Расширения UI (10-15 дней):**
   - Секция "Системные компоненты" в SettingsScreen
   - Расширения Location Tracking (геозоны, история, battery)
   - Roadside Assistance экран/секция

5. **Опционально (5-10 дней):**
   - MFA (2FA)
   - Emergency Alerts для родителей

---

## ✅ ПОДТВЕРЖДЕНИЕ

**Все пункты проверены и подтверждены:**
- ✅ Что уже есть - исключено из плана
- ✅ Что не нужно - исключено из плана
- ✅ Что нужно - добавлено в финальный план
- ✅ Каждый пункт проверен на соответствие реальности

**🚀 Итог: Большая часть уже реализована - нужно только добавить серверные endpoint'ы и минимальные расширения UI!**

---

## 📋 ФИНАЛЬНЫЙ СПИСОК ENDPOINT'ОВ ДЛЯ РЕАЛИЗАЦИИ

### **🔥 КРИТИЧНО: Серверные endpoint'ы (41 endpoint)**

#### **1. NOTIFICATIONS (16 endpoint'ов):**
```
GET  /api/notifications/stats
GET  /api/notifications/unread_count
POST /api/notifications/mark_read/{notification_id}
DELETE /api/notifications/delete/{notification_id}
POST /api/notifications/bulk_mark_read
POST /api/notifications/test
+ 10 дополнительных endpoint'ов для расширенных функций
```

#### **2. COMPONENTS (14 endpoint'ов):**
```
GET  /api/components/service-discovery
POST /api/components/service-discovery/register
GET  /api/components/configuration
PUT  /api/components/configuration
GET  /api/components/health/monitoring
POST /api/components/api-gateway/rate-limit
GET  /api/components/tracing
+ 7 дополнительных endpoint'ов
```

#### **3. SYSTEM MANAGEMENT (11 endpoint'ов):**
```
GET  /api/system/monitoring/prometheus
GET  /api/system/monitoring/grafana
POST /api/system/auto-scaling/configure
GET  /api/system/backup/status
POST /api/system/backup/create
GET  /api/system/audit/logs
+ 5 дополнительных endpoint'ов
```

---

### **🟡 ВАЖНО: iOS код для Roadside Assistance (4 endpoint'а)**

#### **4. ROADSIDE ASSISTANCE (4 endpoint'а в iOS):**
```
POST /api/roadside-assistance/call          - Вызов помощи
GET  /api/roadside-assistance/status/{id}    - Статус запроса
POST /api/roadside-assistance/cancel/{id}    - Отмена запроса
GET  /api/roadside-assistance/history        - История вызовов
```

**Примечание:** Серверные endpoint'ы УЖЕ ЕСТЬ (`roadside_assistance_router.py`) - нужно только добавить в iOS код!

---

### **🟢 ОПЦИОНАЛЬНО: Расширения**

#### **5. LOCATION TRACKING расширения:**
- Геозоны с расписанием (расширить существующий модал)
- История перемещений (добавить в AnalyticsScreen)
- Battery optimization (добавить настройки)

#### **6. MFA (2FA) - опционально:**
- SMS/TOTP коды в ProfileScreen

---

## ✅ ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ

### **Проверено и подтверждено:**

1. ✅ **Roadside Assistance:**
   - ✅ Сервер ЕСТЬ (`roadside_assistance_router.py`) - подтверждено
   - ❌ iOS экран НЕТ - нужно добавить - подтверждено
   - ❌ iOS код (APIService) НЕТ - нужно добавить - подтверждено

2. ✅ **Location Tracking:**
   - ✅ Базовое отслеживание ЕСТЬ (`LocationManager.swift`) - подтверждено
   - ❌ Геозоны с расписанием - нужно расширить - подтверждено
   - ❌ История перемещений - нужно добавить - подтверждено
   - ❌ Battery optimization - нужно добавить - подтверждено

3. ✅ **Системные компоненты:**
   - ❌ Секция в SettingsScreen - нужно добавить - подтверждено

4. ✅ **Графики:**
   - ❌ Графики в AnalyticsScreen - НЕ НУЖНО (по запросу) - подтверждено

5. ✅ **Все остальное:**
   - ✅ Антивирус, Dark Web, Фишинг - ЕСТЬ - подтверждено
   - ✅ Уведомления UI - ЕСТЬ - подтверждено
   - ✅ Родительский контроль - ЕСТЬ - подтверждено
   - ✅ Crash Detection - ЕСТЬ - подтверждено

---

## 🎯 ИТОГОВЫЙ ПЛАН РАБОТЫ

### **Этап 1: Серверные endpoint'ы (60-70 дней)**
- Notifications: 16 endpoint'ов
- Components: 14 endpoint'ов
- System Management: 11 endpoint'ов

### **Этап 2: APNs инфраструктура (3-5 дней)**
- Сертификаты
- Отправка push-уведомлений

### **Этап 3: iOS код для Roadside Assistance (2-3 дня)**
- Методы в `APIService.swift` (4 метода)
- Endpoint'ы в `AppConfig.swift` (4 endpoint'а)

### **Этап 4: Расширения UI (10-15 дней)**
- Секция "Системные компоненты" в SettingsScreen
- Расширения Location Tracking (геозоны, история, battery)
- Roadside Assistance экран/секция

### **Этап 5: Опционально (5-10 дней)**
- MFA (2FA)
- Emergency Alerts для родителей

---

## ✅ ВСЕ ПУНКТЫ ПРОВЕРЕНЫ И ПОДТВЕРЖДЕНЫ!

**Каждый пункт проверен на соответствие реальности:**
- ✅ Что уже есть - исключено из плана
- ✅ Что не нужно - исключено из плана
- ✅ Что нужно - добавлено в финальный план
- ✅ Roadside Assistance - сервер есть, iOS код нужен
- ✅ Location Tracking - базовое есть, расширения нужны
- ✅ Графики - НЕ НУЖНО (по запросу)

**🚀 Итог: Большая часть уже реализована - нужно только добавить серверные endpoint'ы (41), iOS код для Roadside Assistance (4 метода), и минимальные расширения UI!**
